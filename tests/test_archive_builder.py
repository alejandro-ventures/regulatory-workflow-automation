from contextlib import redirect_stderr, redirect_stdout
from hashlib import sha256
from io import BytesIO, StringIO
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from pypdf import PdfReader, PdfWriter

from demos.archive_builder import (
    AUTHOR, INDEX, NOTICE, build, create_fixtures, index_pdf, main, read_index, read_pdf,
)


class ArchiveBuilderTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / "source"
        self.output = self.root / "archive"
        create_fixtures(self.source)

    def test_end_to_end_pages_hashes_order_bookmarks_and_metadata(self) -> None:
        before = {path.name: path.read_bytes() for path in self.source.iterdir()}
        with patch("socket.socket", side_effect=AssertionError("Network not allowed")):
            manifest = build(self.source, self.output)
        self.assertEqual(len(list(self.output.iterdir())), 8)
        self.assertEqual(json.loads((self.output / "manifest.json").read_text()), manifest)
        self.assertEqual(manifest["checks"], {"expected_pages": 5, "actual_pages": 5, "page_count_matches": True})
        merged = PdfReader(self.output / "merged-archive.pdf")
        self.assertEqual(len(merged.pages), 5)
        self.assertEqual(merged.metadata.author, AUTHOR)
        self.assertEqual(merged.metadata.subject, NOTICE)
        self.assertEqual([merged.get_destination_page_number(item) for item in merged.outline], [0, 1, 2, 3])
        self.assertEqual([item.title for item in merged.outline],
                         ["Synthetic archive note", "Synthetic index", "Invented acknowledgement", "Invented dossier"])
        for page in merged.pages:
            self.assertIn(NOTICE, page.extract_text())
        self.assertIn("Invented supporting information.", merged.pages[4].extract_text())
        self.assertEqual(manifest["merged"]["sha256"], sha256((self.output / "merged-archive.pdf").read_bytes()).hexdigest())
        for component in manifest["components"]:
            self.assertEqual(component["sha256"], sha256((self.output / component["file"]).read_bytes()).hexdigest())
            self.assertEqual(component["pages"], len(PdfReader(self.output / component["file"]).pages))
        for name, content in before.items():
            self.assertEqual((self.source / name).read_bytes(), content)
            self.assertEqual((self.output / name).read_bytes(), content)
        self.assertEqual(manifest["index"]["sha256"], sha256(INDEX).hexdigest())
        self.assertNotIn(str(self.root), (self.output / "manifest.json").read_text())

    def test_missing_extra_and_duplicate_inputs(self) -> None:
        (self.source / "extra.txt").write_text("invented")
        with self.assertRaisesRegex(ValueError, "exactly"):
            build(self.source, self.output)
        (self.source / "extra.txt").unlink()
        (self.source / "dossier.pdf").unlink()
        with self.assertRaisesRegex(ValueError, "exactly"):
            build(self.source, self.output)
        duplicate = INDEX.replace(b'dossier.pdf', b'acknowledgement.pdf')
        with self.assertRaisesRegex(ValueError, "exactly once"):
            read_index(duplicate)

    def test_invalid_xml_paths_and_entities(self) -> None:
        for content in (
            b"<archive>",
            INDEX.replace(b'synthetic="true"', b'synthetic="false"'),
            INDEX.replace(b'dossier.pdf', b'../dossier.pdf'),
            INDEX.replace(b'dossier.pdf', b'https://example.invalid/dossier.pdf'),
            b'<!DOCTYPE archive [<!ENTITY x "x">]><archive/>',
        ):
            with self.subTest(content=content), self.assertRaises(ValueError):
                read_index(content)

    def test_raw_xml_rendering_wraps_long_lines_and_paginates(self) -> None:
        content = (b"A" * 250 + b"END-MARKER\n") * 40
        reader = read_pdf(index_pdf(content))
        self.assertEqual(len(reader.pages), 2)
        extracted = "".join(page.extract_text() for page in reader.pages)
        self.assertEqual(extracted.count("END-MARKER"), 40)

    def test_rejects_broken_encrypted_and_nonsynthetic_pdfs(self) -> None:
        for kind in ("broken", "encrypted", "unlabeled", "empty"):
            if kind == "broken":
                content = b"not a PDF"
            else:
                writer = PdfWriter()
                if kind != "empty":
                    writer.add_blank_page(width=200, height=200)
                if kind == "encrypted":
                    writer.encrypt("invented-test-value")
                buffer = BytesIO()
                writer.write(buffer)
                writer.close()
                content = buffer.getvalue()
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                read_pdf(content)

    def test_existing_output_not_overwritten(self) -> None:
        build(self.source, self.output)
        before = {path.name: path.read_bytes() for path in self.output.iterdir()}
        with self.assertRaisesRegex(ValueError, "already exists"):
            build(self.source, self.output)
        self.assertEqual(before, {path.name: path.read_bytes() for path in self.output.iterdir()})
        with self.assertRaisesRegex(ValueError, "already exists"):
            create_fixtures(self.source)

    def test_write_failure_rolls_back_without_modifying_input(self) -> None:
        original_open = Path.open
        before = {path.name: path.read_bytes() for path in self.source.iterdir()}

        def failing_open(path, *args, **kwargs):
            if path.parent == self.output and path.name == "manifest.json":
                raise OSError("Simulated write failure")
            return original_open(path, *args, **kwargs)

        with patch("pathlib.Path.open", autospec=True, side_effect=failing_open):
            with self.assertRaisesRegex(OSError, "Simulated"):
                build(self.source, self.output)
        self.assertFalse(self.output.exists())
        self.assertEqual(before, {path.name: path.read_bytes() for path in self.source.iterdir()})

    def test_cli_confirmation_success_and_failure(self) -> None:
        args = ["build", "--input", str(self.source), "--output", str(self.output), "--confirm-synthetic"]
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            self.assertEqual(main(args), 0)
        self.assertIn("Completed build", stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit) as caught:
            main(args[:-1])
        self.assertEqual(caught.exception.code, 2)
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            self.assertEqual(main(args), 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("already exists", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
