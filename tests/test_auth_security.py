import unittest
import os
import subprocess
import json
import re

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


    def test_deploy_script_no_hardcoded_secrets(self):
        """Verify deploy_to_cloudflare.py does not contain hardcoded API tokens."""
        deploy_script = os.path.join(self.root_dir, 'deploy_to_cloudflare.py')
        with open(deploy_script, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIsNone(re.search(r"(?:cfut_|ghp_)[A-Za-z0-9_-]{20,}", content), "No hardcoded API tokens in deploy_to_cloudflare.py")

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
                    self.assertIsNone(re.search(r"(?:cfut_|ghp_)[A-Za-z0-9_-]{20,}", data), f"Found API token in tracked file: {rel_path}")

    def test_kam_role_based_access(self):
        """Verify KAM role-based auth and modal are present in js and html."""
        kam_js_path = os.path.join(self.root_dir, 'js', 'kam-dashboard.js')
        site_kam_js_path = os.path.join(self.root_dir, 'site', 'js', 'kam-dashboard.js')
        index_html_path = os.path.join(self.root_dir, 'index.html')
        site_html_path = os.path.join(self.root_dir, 'site', 'index.html')

        for p in [kam_js_path, site_kam_js_path]:
            self.assertTrue(os.path.exists(p), f"{p} should exist")
            with open(p, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertIn("KAM_AUTH_ACCOUNTS", content, f"KAM_AUTH_ACCOUNTS must be defined in {p}")
            self.assertIn("canUserEditOverallPlan", content, f"canUserEditOverallPlan must be defined in {p}")
            self.assertIn("canUserEditPartnerPlan", content, f"canUserEditPartnerPlan must be defined in {p}")
            self.assertIn("getPartnerPlanCellHtml", content, f"getPartnerPlanCellHtml must be defined in {p}")

        for p in [index_html_path, site_html_path]:
            self.assertTrue(os.path.exists(p), f"{p} should exist")
            with open(p, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertIn("kamLoginModal", content, f"kamLoginModal must be in {p}")
            self.assertIn("kamAuthWidgetContainer", content, f"kamAuthWidgetContainer must be in {p}")

if __name__ == '__main__':
    unittest.main()

