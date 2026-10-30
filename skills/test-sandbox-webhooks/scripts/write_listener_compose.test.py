import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest


SCRIPT = Path(__file__).with_name("write_listener_compose.py")


class ListenerSetupTest(unittest.TestCase):
    def run_script(self, cwd, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args], cwd=cwd, capture_output=True, text=True
        )

    def test_generate_refuse_overwrite_and_force(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            result = self.run_script(root, "--app-port", "4321", "--webhook-path", "hooks/tyxter")
            self.assertEqual(result.returncode, 0, result.stderr)
            compose = root / "compose.tyxter-cli.yaml"
            env = root / ".env.tyxter-cli.example"
            self.assertIn(".env.tyxter-cli", compose.read_text())
            self.assertIn("http://host.docker.internal:4321/hooks/tyxter", env.read_text())
            self.assertIn("https://api.tyxter.com", env.read_text())
            compose.write_text("customer configuration")
            result = self.run_script(root)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("--force", result.stderr)
            self.assertEqual(compose.read_text(), "customer configuration")
            result = self.run_script(root, "--force")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("services:", compose.read_text())
            self.assertEqual(
                sorted(p.name for p in root.iterdir()),
                [".env.tyxter-cli.example", "compose.tyxter-cli.yaml"],
            )

    def test_second_destination_failure_leaves_no_partial_setup_and_can_retry(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            args = ("--env-example", "missing/listener.env.example")
            result = self.run_script(root, *args)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Cannot write listener setup", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(list(root.iterdir()), [])
            (root / "missing").mkdir()
            result = self.run_script(root, *args)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_force_staging_failure_preserves_existing_output(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            compose = root / "compose.tyxter-cli.yaml"
            compose.write_text("customer configuration")
            result = self.run_script(root, "--force", "--env-example", "missing/env")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(compose.read_text(), "customer configuration")
            self.assertEqual(list(root.iterdir()), [compose])

    def test_unwritable_directory_reports_error_without_traceback(self):
        if os.geteuid() == 0:
            self.skipTest("root bypasses directory permissions")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            root.chmod(0o500)
            try:
                result = self.run_script(root)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Cannot write listener setup", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(list(root.iterdir()), [])
            finally:
                root.chmod(0o700)

    def test_destinations_must_be_distinct(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            result = self.run_script(root, "--compose", "same", "--env-example", "./same")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(list(root.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
