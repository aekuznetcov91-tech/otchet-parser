"""Exercise the deployed handler code with isolated durable storage, never production."""
import pathlib,subprocess,shutil,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class TestServerSecurity(unittest.TestCase):
    def test_security_scenarios(self):
        node=shutil.which('node')
        self.assertIsNotNone(node,'Node is required; security tests must not be skipped')
        r=subprocess.run([node,'tests/security_worker.mjs'],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
    def test_security_generated_assets(self):
        r=subprocess.run([shutil.which('node'),'scripts/build_security.cjs','--check'],cwd=ROOT,capture_output=True,text=True)
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
    def test_no_browser_pins_or_auth_storage(self):
        s=(ROOT/'site/js/kam/access.js').read_text(encoding='utf-8')
        self.assertNotIn('pins:',s)
        self.assertNotIn('localStorage.getItem',s)
        self.assertNotIn('fillKamTestPin',(ROOT/'site/index.html').read_text(encoding='utf-8'))
