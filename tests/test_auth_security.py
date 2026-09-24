import unittest
import os
import subprocess
import json

class TestAuthSecurity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def test_readme_sanitized(self):
        """Verify README.md has no exposed plain text credentials."""
        readme_path = os.path.join(self.root_dir, 'README.md')
        self.assertTrue(os.path.exists(readme_path), "README.md should exist")
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertNotIn("Basic Auth: director / password", content, "Plaintext credentials must not be present in README.md")
        self.assertNotIn("director / password", content, "director / password pair must not be present in README.md")

    def test_gitignore_protects_secrets(self):
        """Verify .gitignore includes sensitive files and scratch dirs."""
        gitignore_path = os.path.join(self.root_dir, '.gitignore')
        self.assertTrue(os.path.exists(gitignore_path), ".gitignore should exist")
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        self.assertIn(".env", lines, ".env must be ignored")
        self.assertIn("config.local.json", lines, "config.local.json must be ignored")
        self.assertIn("scratch/", lines, "scratch/ must be ignored")

    def test_functions_middleware_exists_and_synced(self):
        """Verify edge middleware exists in both functions/ and site/functions/ and are identical."""
        func_mw = os.path.join(self.root_dir, 'functions', '_middleware.js')
        site_mw = os.path.join(self.root_dir, 'site', 'functions', '_middleware.js')
        
        self.assertTrue(os.path.exists(func_mw), "functions/_middleware.js must exist")
        self.assertTrue(os.path.exists(site_mw), "site/functions/_middleware.js must exist")

        with open(func_mw, 'r', encoding='utf-8') as f1, open(site_mw, 'r', encoding='utf-8') as f2:
            c1 = f1.read()
            c2 = f2.read()
        
        self.assertEqual(c1, c2, "site/functions/_middleware.js must be identical to functions/_middleware.js")
        self.assertIn("export async function onRequest", c1, "Middleware must export onRequest")
        self.assertIn("WWW-Authenticate", c1, "Middleware must return WWW-Authenticate header")
        self.assertIn("timingSafeEqual", c1, "Middleware must implement constant-time comparison")
        self.assertIn("crypto.subtle", c1, "Middleware must use crypto.subtle for hashing")
        self.assertIn("AUTH_USER", c1, "Middleware must support AUTH_USER env var")
        self.assertIn("AUTH_PASS", c1, "Middleware must support AUTH_PASS env var")

    def test_deploy_script_no_hardcoded_secrets(self):
        """Verify deploy_to_cloudflare.py does not contain hardcoded API tokens."""
        deploy_script = os.path.join(self.root_dir, 'deploy_to_cloudflare.py')
        with open(deploy_script, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertNotIn("cfut_", content, "No hardcoded Cloudflare API tokens in deploy_to_cloudflare.py")

    def test_tracked_files_no_leaked_cloudflare_tokens(self):
        """Verify no git-tracked files contain Cloudflare API tokens."""
        git_res = subprocess.run(["git", "ls-files"], cwd=self.root_dir, capture_output=True, text=True, errors='replace')
        if git_res.returncode == 0:
            tracked_files = git_res.stdout.splitlines()
            for rel_path in tracked_files:
                # Skip binary, large files, or the security test itself
                if rel_path.endswith(('.png', '.jpg', '.ico', '.xlsx', '.xls', '.json')) or 'test_auth_security.py' in rel_path:
                    continue
                full_path = os.path.join(self.root_dir, rel_path)
                if os.path.exists(full_path):
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        data = f.read()
                    self.assertNotIn("cfut_", data, f"Found Cloudflare API token in tracked file: {rel_path}")

if __name__ == '__main__':
    unittest.main()
