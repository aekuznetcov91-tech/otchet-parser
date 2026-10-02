"""Release safety checks: failures must never publish an unchecked snapshot."""
import subprocess
import tempfile
import tarfile
import io
import unittest
from pathlib import Path
from unittest.mock import patch

import deploy_to_cloudflare as release
from scripts.sync_frontend import sync_frontend
from scripts.etl.export import safe_save_json


class TestRelease(unittest.TestCase):
    def setUp(self):
        quiet = patch("builtins.print")
        quiet.start()
        self.addCleanup(quiet.stop)

    def test_frontend_sources_and_generated_assets_match(self):
        self.assertEqual(sync_frontend(check=True), [])

    def test_sync_check_does_not_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / 'generated.js'
            with patch('scripts.sync_frontend.expected_assets', return_value={target: b'new'}):
                with self.assertRaises(RuntimeError):
                    sync_frontend(root, check=True)
                self.assertFalse(target.exists())
                sync_frontend(root)
                self.assertEqual(target.read_bytes(), b'new')

    def test_atomic_export_keeps_old_file_on_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'data.json'
            target.write_text('old')
            with patch('scripts.etl.export.os.replace', side_effect=OSError('disk failure')):
                with self.assertRaises(OSError):
                    safe_save_json({'new': 1}, target)
            self.assertEqual(target.read_text(), 'old')
            self.assertFalse(Path(str(target) + '.tmp').exists())
            safe_save_json({'new': 1}, target)
            self.assertEqual(target.read_text(), '{"new":1}')

    def test_nonzero_wrangler_with_success_text_is_failure(self):
        result = subprocess.CompletedProcess(['wrangler'], 1, 'Success pages.dev', 'failed')
        with patch.object(release.subprocess, 'run', return_value=result):
            with self.assertRaises(RuntimeError):
                release.run(['wrangler'])

    def test_failed_tests_stop_before_git(self):
        with patch.object(release, 'deployment_environment', return_value=({}, 'test')), \
             patch.object(release.shutil, 'which', return_value='node'), \
             patch.object(release, 'sync_frontend'), patch.object(release, 'validate_site'), \
             patch.object(release, 'run', side_effect=RuntimeError('tests failed')), \
             patch.object(release, 'sync_and_push_git') as push:
            with self.assertRaises(RuntimeError):
                release.deploy(git_only=True)
            push.assert_not_called()

    def test_git_failure_stops_later_commands(self):
        for failure in ('fetch', 'merge-base', 'add', 'commit', 'push'):
            commands = []
            def fake_run(args, **kwargs):
                commands.append(args)
                if args[1] == failure:
                    raise RuntimeError('failure')
                if args[1] == 'branch': return 'main'
                if args[1] == 'diff' and '--name-only' in args: return 'README.md'
                if args[1] == 'rev-parse': return 'abc'
                return ''
            with self.subTest(failure=failure), patch.object(release, 'run', side_effect=fake_run):
                with self.assertRaises(RuntimeError):
                    release.sync_and_push_git()
                self.assertEqual(commands[-1][1], failure)

    def test_wrong_branch_does_not_stage_or_push(self):
        with patch.object(release, 'run', return_value='feature') as run:
            with self.assertRaises(RuntimeError): release.sync_and_push_git()
            self.assertEqual(run.call_count, 1)

    def test_remote_commit_must_match(self):
        def fake_run(args, **kwargs):
            if args[1] == 'branch': return 'main'
            if args[1] == 'rev-parse': return 'expected'
            if args[1] == 'ls-remote': return 'other\trefs/heads/main'
            return ''
        with patch.object(release, 'run', side_effect=fake_run):
            with self.assertRaisesRegex(RuntimeError, 'does not match'):
                release.sync_and_push_git()

    def test_cloudflare_uses_published_commit_archive(self):
        calls = []
        revision = 'a' * 40
        def fake_run(args, **kwargs):
            calls.append(args)
            if args[:2] == ['git', 'archive']:
                self.assertEqual(args[-2:], [revision, 'site'])
                archive = next(arg.split('=', 1)[1] for arg in args if arg.startswith('--output='))
                with tarfile.open(archive, 'w') as tar:
                    info = tarfile.TarInfo('site/index.html')
                    info.size = 4
                    tar.addfile(info, io.BytesIO(b'test'))
            return 'OK'
        env = {'CLOUDFLARE_API_TOKEN': 'test', 'CLOUDFLARE_ACCOUNT_ID': 'test'}
        with patch.object(release, 'deployment_environment', return_value=(env, 'test')), \
             patch.object(release.shutil, 'which', return_value='wrangler'), \
             patch.object(release, 'sync_frontend'), \
             patch.object(release, 'run', side_effect=fake_run), \
             patch.object(release, 'sync_and_push_git', return_value=revision):
            self.assertEqual(release.deploy(), revision)
        self.assertIn('--commit-hash=' + revision, calls[-1])
        self.assertNotEqual(Path(calls[-1][3]), release.ROOT / 'site')

    def test_push_failure_prevents_cloudflare(self):
        env = {'CLOUDFLARE_API_TOKEN': 'test', 'CLOUDFLARE_ACCOUNT_ID': 'test'}
        with patch.object(release, 'deployment_environment', return_value=(env, 'test')), \
             patch.object(release.shutil, 'which', return_value='node'), \
             patch.object(release, 'sync_frontend'), patch.object(release, 'validate_site'), \
             patch.object(release, 'run', return_value='OK') as run, \
             patch.object(release, 'sync_and_push_git', side_effect=RuntimeError('push failed')):
            with self.assertRaises(RuntimeError): release.deploy()
            self.assertEqual(run.call_count, 1)

    def test_staged_secrets_block_commit(self):
        with patch.object(release, 'run', return_value='config.local.json'):
            with self.assertRaises(RuntimeError): release.validate_staged_changes()
        token = 'cfut' + '_' + 'a' * 30
        with patch.object(release, 'run', side_effect=['file.py', '+' + token]):
            with self.assertRaises(RuntimeError): release.validate_staged_changes()
        self.assertNotIn(token, release.redact(token))

    def test_oversized_asset_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            (site / 'index.html').write_text('test')
            with (site / 'large.json').open('wb') as f:
                f.truncate(release.MAX_FILE_BYTES)
            with self.assertRaises(RuntimeError): release.validate_site(site)
