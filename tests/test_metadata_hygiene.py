"""Publication regressions for bundled demos, not a sanitizer for arbitrary input.

Inspect expanded OOXML members and reachable PDF objects, including compressed
metadata streams. Only files generated in these tests are opened. Limits keep
accidental artifact growth from silently reducing inspection coverage.
"""

import getpass
from html import unescape
from io import BytesIO
from pathlib import Path
import re
import socket
import tempfile
import unittest
from zipfile import ZIP_DEFLATED, ZipFile

from pypdf import PdfReader, PdfWriter
from pypdf.generic import (
    ArrayObject, ByteStringObject, DictionaryObject, IndirectObject,
    NameObject, StreamObject, TextStringObject, DecodedStreamObject,
)

from demos.archive_builder import build, create_fixtures, render_pdf
from demos.monitor_fixtures import generate as generate_spreadsheets
from demos.reference_monitor import run as run_monitor
from demos.report_composer import generate as generate_report, load_report


ROOT = Path(__file__).resolve().parents[1]
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_EXPANDED_BYTES = 32 * 1024 * 1024
MAX_OBJECTS = 5000
CANARY_HOME = "C:/Users/MetadataCanaryUser"
CANARY_HOST = "METADATA-CANARY-HOST"


def normalized(value: str) -> str:
    # Handle XML entities, Windows paths, and JSON-escaped Windows paths.
    return re.sub(r"/+", "/", unescape(value).replace("\\", "/")).casefold()


def identifying_labels(text: str, paths: list[str], hostname: str,
                       username: str = "", location: str = "") -> set[str]:
    """Return labels, never private matched values, in assertion failures."""
    value = normalized(text)
    found = set()
    for index, path in enumerate(paths):
        needle = normalized(path).rstrip("/")
        # Match the exact directory as well as descendants, but not another
        # user's longer name. PDF structural names are excluded during decoding.
        pattern = r"(?<![a-z0-9])" + re.escape(needle) + r"(?=/|$|[\s\"'<>])"
        if len(needle) >= 4 and re.search(pattern, value):
            found.add(f"local path {index + 1}")
    host = hostname.casefold().strip()
    # Short/generic host labels occur naturally in prose and format syntax.
    if len(host) >= 5 and host not in {"localhost", "localhost.localdomain", "runner", "ubuntu", "windows", "computer"}:
        if re.search(r"(?<![a-z0-9_-])" + re.escape(host) + r"(?![a-z0-9_-])", value):
            found.add("hostname")
    user = username.casefold().strip()
    if user and user not in {"root", "user", "runner", "admin", "administrator", "unknown", "system", "demo"}:
        if len(user) >= 5:
            present = re.search(r"(?<![a-z0-9_-])" + re.escape(user) + r"(?![a-z0-9_-])", value)
        else:
            # Short usernames can be normal words. Require an exact author-like
            # metadata field, not a match in the document body or PDF syntax.
            identity_field = "/info/" in location.casefold() or re.search(
                r"/(author|creator|lastmodifiedby|username)$", location.casefold())
            xml_identity = r"<(?:[a-z0-9_]+:)?(?:author|creator|lastmodifiedby|username)(?:\s[^>]*)?>\s*"
            present = (identity_field and value.strip() == user) or re.search(
                xml_identity + re.escape(user) + r"\s*</", value)
            if location.casefold().startswith("docprops/"):
                present = present or re.search(r">\s*" + re.escape(user) + r"\s*<", value)
        if present:
            found.add("username")
    return found


def expanded_text(content: bytes, suffix: str) -> list[tuple[str, str]]:
    """Decode known generated formats; fail rather than skip oversized data."""
    if len(content) > MAX_FILE_BYTES:
        raise AssertionError("Generated artifact exceeds inspection size limit")
    parts: list[tuple[str, str]] = []
    expanded = 0

    def add(location: str, data: bytes | str) -> None:
        nonlocal expanded
        raw = data.encode("utf-8") if isinstance(data, str) else data
        expanded += len(raw)
        if expanded > MAX_EXPANDED_BYTES:
            raise AssertionError("Expanded artifact exceeds inspection size limit")
        if isinstance(data, str):
            parts.append((location, data))
        else:
            for encoding in ("utf-8", "utf-16-le", "utf-16-be"):
                parts.append((location, data.decode(encoding, errors="replace")))

    if suffix in {".docx", ".xlsx"}:
        with ZipFile(BytesIO(content)) as package:
            members = package.infolist()
            if len(members) > 256 or sum(item.file_size for item in members) > MAX_EXPANDED_BYTES:
                raise AssertionError("OOXML package exceeds inspection limits")
            for member in members:
                add(member.filename, package.read(member))
    elif suffix == ".pdf":
        reader = PdfReader(BytesIO(content), strict=True)
        visited: set[tuple[int, int]] = set()
        count = 0

        def walk(obj: object, location: str, depth: int = 0) -> None:
            nonlocal count
            count += 1
            if count > MAX_OBJECTS or depth > 64:
                raise AssertionError("PDF object graph exceeds inspection limits")
            if isinstance(obj, IndirectObject):
                key = (obj.idnum, obj.generation)
                if key in visited:
                    return
                visited.add(key)
                walk(obj.get_object(), location, depth + 1)
            elif isinstance(obj, DictionaryObject):
                if isinstance(obj, StreamObject):
                    add(location + " decoded stream", obj.get_data())
                for key, child in obj.items():
                    walk(child, location + str(key), depth + 1)
            elif isinstance(obj, ArrayObject):
                for index, child in enumerate(obj):
                    walk(child, f"{location}[{index}]", depth + 1)
            elif isinstance(obj, NameObject):
                # /Root and other structural PDF names are not user text.
                return
            elif isinstance(obj, (TextStringObject, str)):
                add(location, str(obj))
            elif isinstance(obj, (ByteStringObject, bytes)):
                add(location, bytes(obj))

        walk(reader.trailer, "PDF trailer")
    elif suffix in {".html", ".json", ".xml"}:
        add("text", content)
    else:
        raise AssertionError(f"Unexpected generated artifact type: {suffix}")
    return parts


class MetadataHygieneTests(unittest.TestCase):
    def test_all_bundled_demo_outputs_exclude_machine_identity(self) -> None:
        with tempfile.TemporaryDirectory(prefix="demo-metadata-") as temporary:
            root = Path(temporary)
            generate_report(load_report(ROOT / "fixtures/reporting/annual-report.json"), root / "report")
            generate_spreadsheets(root / "spreadsheets")
            monitoring = ROOT / "fixtures/monitoring"
            previous = None
            for name, spreadsheet in (("first", "baseline.xlsx"), ("repeat", "baseline.xlsx"), ("revised", "revised.xlsx")):
                destination = root / name
                run_monitor(monitoring / "feed.xml", root / "spreadsheets" / spreadsheet,
                            monitoring / "interests.json", previous, destination)
                previous = destination / "state.json"
            create_fixtures(root / "archive-inputs")
            build(root / "archive-inputs", root / "archive")
            paths = [str(Path.home()), str(ROOT), str(root), tempfile.gettempdir()]
            hostname = socket.gethostname()
            username = getpass.getuser()
            artifacts = sorted(path for path in root.rglob("*") if path.is_file())
            self.assertEqual(len(artifacts), 25)
            for artifact in artifacts:
                with self.subTest(artifact=artifact.relative_to(root).as_posix()):
                    parts = expanded_text(artifact.read_bytes(), artifact.suffix)
                    self.assertTrue(parts, "Artifact inspection produced no text")
                    for location, text in parts:
                        self.assertFalse(identifying_labels(text, paths, hostname, username, location),
                                         f"Identifying data in {artifact.name}: {location}")

    def test_compressed_ooxml_custom_properties_are_inspected(self) -> None:
        canary = f"{CANARY_HOME}/private/input.json on {CANARY_HOST}"
        buffer = BytesIO()
        with ZipFile(buffer, "w", compression=ZIP_DEFLATED) as package:
            package.writestr("docProps/core.xml", "<coreProperties/>")
            package.writestr("docProps/custom.xml", f"<Properties><value>{canary}</value></Properties>")
        content = buffer.getvalue()
        self.assertNotIn(canary.encode(), content, "Canary must be hidden by ZIP compression")
        for suffix in (".docx", ".xlsx"):
            with self.subTest(suffix=suffix):
                findings = [(location, identifying_labels(text, [CANARY_HOME], CANARY_HOST))
                            for location, text in expanded_text(content, suffix)]
                self.assertTrue(any(location == "docProps/custom.xml" and
                                    labels == {"local path 1", "hostname"} for location, labels in findings))

    def test_pdf_info_and_compressed_metadata_are_inspected(self) -> None:
        writer = PdfWriter()
        writer.append(PdfReader(BytesIO(render_pdf("Canary test", [["Invented fixture only"]]))))
        writer.add_metadata({"/Keywords": CANARY_HOST})
        metadata = DecodedStreamObject()
        metadata.set_data(f'<metadata source="{CANARY_HOME}/private/input.json"/>'.encode())
        metadata[NameObject("/Type")] = NameObject("/Metadata")
        metadata[NameObject("/Subtype")] = NameObject("/XML")
        writer.root_object[NameObject("/Metadata")] = writer._add_object(metadata.flate_encode())
        buffer = BytesIO()
        writer.write(buffer)
        writer.close()
        content = buffer.getvalue()
        self.assertNotIn(CANARY_HOME.encode(), content, "Path canary must be compressed")
        findings = [(location, identifying_labels(text, [CANARY_HOME], CANARY_HOST))
                    for location, text in expanded_text(content, ".pdf")]
        self.assertTrue(any("/Info/Keywords" in location and "hostname" in labels
                            for location, labels in findings))
        self.assertTrue(any("/Metadata decoded stream" in location and "local path 1" in labels
                            for location, labels in findings))

    def test_identity_matching_handles_escaping_without_short_name_false_positives(self) -> None:
        self.assertEqual(identifying_labels(r'C:\\Users\\MetadataCanaryUser\\private\\input.json',
                                           [CANARY_HOME], CANARY_HOST), {"local path 1"})
        self.assertEqual(identifying_labels("/rooted/demo C:/Users/Alfred/demo.xml Demonstration",
                                           ["/root", "C:/Users/Al"], "demo"), set())
        self.assertEqual(identifying_labels("runner generated an invented example", [], "runner"), set())
        for value in (CANARY_HOME, f'<value>{CANARY_HOME}</value>', f'"{CANARY_HOME}"'):
            with self.subTest(value=value):
                self.assertEqual(identifying_labels(value, [CANARY_HOME], ""), {"local path 1"})
        self.assertEqual(identifying_labels("MetadataCanaryUser", [], "", "MetadataCanaryUser"), {"username"})
        self.assertEqual(identifying_labels("Al", [], "", "Al", "PDF trailer/Info/Author"), {"username"})
        self.assertEqual(identifying_labels("<dc:creator>Al</dc:creator>", [], "", "Al"), {"username"})
        self.assertEqual(identifying_labels("Al appears in ordinary text", [], "", "Al"), set())
        self.assertEqual(identifying_labels("runner", [], "", "runner", "PDF trailer/Info/Author"), set())

    def test_pdf_structural_names_are_not_home_directory_values(self) -> None:
        writer = PdfWriter()
        writer.add_blank_page(width=100, height=100)
        writer.root_object[NameObject("/TestStructuralName")] = NameObject("/Root")
        buffer = BytesIO()
        writer.write(buffer)
        writer.close()
        self.assertFalse(any(identifying_labels(text, ["/root"], "")
                             for _, text in expanded_text(buffer.getvalue(), ".pdf")))

    def test_inspection_fails_closed_on_limits_and_unknown_formats(self) -> None:
        with self.assertRaisesRegex(AssertionError, "size limit"):
            expanded_text(b"x" * (MAX_FILE_BYTES + 1), ".json")
        with self.assertRaisesRegex(AssertionError, "Unexpected"):
            expanded_text(b"invented", ".unknown")


if __name__ == "__main__":
    unittest.main()
