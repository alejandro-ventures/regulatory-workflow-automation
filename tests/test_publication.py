from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.check_publication import check, parse_manifest


class PublicationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.git("init", "-q")
        self.write("README.md", b"Invented demonstration.\n")
        self.write("publication-files.txt", b"README.md\npublication-files.txt\n")
        self.git("add", ".")

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, stderr=subprocess.PIPE)

    def write(self, path, content):
        (self.root / path).write_bytes(content)

    def test_reads_staged_blobs_not_working_copy(self):
        self.write("README.md", b"\x00unstaged data")
        self.assertEqual(check(self.root, None), 2)
        self.git("add", "README.md")
        with self.assertRaisesRegex(ValueError, "Binary"):
            check(self.root, None)

    def test_unlisted_file_fails_without_printing_its_name(self):
        self.write("unreviewed.json", b"{}")
        self.git("add", ".")
        with self.assertRaisesRegex(ValueError, "1 unlisted") as caught:
            check(self.root, None)
        self.assertNotIn("unreviewed.json", str(caught.exception))

    def test_missing_file_fails(self):
        self.git("update-index", "--force-remove", "README.md")
        with self.assertRaisesRegex(ValueError, "1 missing"):
            check(self.root, None)

    def test_binary_file_fails_even_if_listed(self):
        self.write("README.md", b"\xff\xfe")
        self.git("add", ".")
        with self.assertRaisesRegex(ValueError, "UTF-8"):
            check(self.root, None)

    def test_link_mode_is_rejected(self):
        sha = self.git("rev-parse", ":README.md").decode().strip()
        self.git("update-index", "--cacheinfo", f"120000,{sha},README.md")
        with self.assertRaisesRegex(ValueError, "regular files"):
            check(self.root, None)

    def test_committed_ref_is_independent_of_index(self):
        self.git("-c", "user.name=Demo", "-c", "user.email=demo@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "Synthetic test")
        self.write("unreviewed.json", b"{}")
        self.git("add", ".")
        self.assertEqual(check(self.root), 2)
        with self.assertRaises(ValueError):
            check(self.root, None)

    def test_manifest_paths_and_duplicates(self):
        for entry in ("../data", "/data", "./data", "dir//data", "data ", "a:b", "a\\b"):
            with self.subTest(entry=entry), self.assertRaises(ValueError):
                parse_manifest(f"publication-files.txt\n{entry}\n")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            parse_manifest("publication-files.txt\npublication-files.txt\n")
        with self.assertRaisesRegex(ValueError, "itself"):
            parse_manifest("README.md\n")


if __name__ == "__main__":
    unittest.main()
