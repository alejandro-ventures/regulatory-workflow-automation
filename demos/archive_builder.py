"""Build a bookmarked demonstration archive from invented local documents."""

import argparse
from contextlib import ExitStack
from hashlib import sha256
from html import escape
from io import BytesIO
import json
from pathlib import Path
import sys
from xml.etree.ElementTree import ParseError

from defusedxml import ElementTree as SafeXML
from defusedxml.common import DefusedXmlException
from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen.canvas import Canvas


NOTICE = "SYNTHETIC DEMONSTRATION - NOT FOR REGULATORY SUBMISSION"
AUTHOR = "Regulatory Workflow Demo"
INDEX = b"""<?xml version="1.0" encoding="UTF-8"?>
<archive synthetic="true" id="DEMO-ARCHIVE-A">
  <document file="acknowledgement.pdf" title="Invented acknowledgement"/>
  <document file="dossier.pdf" title="Invented dossier"/>
</archive>
"""
REQUIRED_PDFS = {"acknowledgement.pdf", "dossier.pdf"}


def render_pdf(title: str, pages: list[list[str]]) -> bytes:
    buffer = BytesIO()
    canvas = Canvas(buffer, pagesize=A4, invariant=1)
    canvas.setAuthor(AUTHOR)
    canvas.setCreator(AUTHOR)
    canvas.setTitle(title)
    canvas.setSubject(NOTICE)
    for number, lines in enumerate(pages, start=1):
        canvas.setFont("Helvetica-Bold", 14)
        canvas.drawString(40, 800, title)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(40, 780, NOTICE)
        canvas.setFont("Courier", 8)
        for offset, line in enumerate(lines):
            canvas.drawString(40, 755 - offset * 10, line)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(40, 30, f"DRAFT - HUMAN REVIEW REQUIRED | Page {number}")
        canvas.showPage()
    canvas.save()
    return buffer.getvalue()


def publish(files: dict[str, bytes], output: Path) -> None:
    if output.exists():
        raise ValueError("Output already exists; choose a fresh directory.")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir()
    with ExitStack() as rollback:
        rollback.callback(output.rmdir)
        for name, content in files.items():
            path = output / name
            with path.open("xb") as stream:
                rollback.callback(path.unlink)
                stream.write(content)
        rollback.pop_all()


def create_fixtures(output: Path) -> None:
    publish({
        "index.xml": INDEX,
        "acknowledgement.pdf": render_pdf("Invented acknowledgement", [
            ["DEMO-ARCHIVE-A", "Fictional receipt for demonstration only.",
             "This is not an authority acknowledgement."],
        ]),
        "dossier.pdf": render_pdf("Invented dossier", [
            ["DEMO-ARCHIVE-A", "Example Material Alpha", "Invented administrative overview."],
            ["DEMO-ARCHIVE-A", "Example Material Alpha", "Invented supporting information."],
        ]),
    }, output)


def read_index(content: bytes) -> list[tuple[str, str]]:
    if len(content) > 100_000:
        raise ValueError("Demonstration index exceeds 100,000 bytes.")
    try:
        raw = content.decode("ascii")
        root = SafeXML.fromstring(content, forbid_dtd=True)
    except (UnicodeError, ParseError, DefusedXmlException) as error:
        raise ValueError("Index must be valid ASCII XML without DTDs or entities.") from error
    if any(ord(char) < 32 and char not in "\r\n\t" for char in raw):
        raise ValueError("Index contains unsupported control characters.")
    if root.tag != "archive" or root.attrib != {"synthetic": "true", "id": "DEMO-ARCHIVE-A"}:
        raise ValueError("Expected the synthetic DEMO-ARCHIVE-A index schema.")
    entries: list[tuple[str, str]] = []
    for child in root:
        if child.tag != "document" or set(child.attrib) != {"file", "title"} or len(child):
            raise ValueError("Index entries require only a file and title.")
        name, title = child.attrib["file"], child.attrib["title"]
        if name not in REQUIRED_PDFS or not title.strip() or len(title) > 70:
            raise ValueError("Index must reference the two invented PDFs with short titles.")
        if any(ord(char) < 32 or ord(char) > 126 for char in title):
            raise ValueError("Index titles must use printable ASCII.")
        entries.append((name, title))
    if len(entries) != 2 or {name for name, _ in entries} != REQUIRED_PDFS:
        raise ValueError("Index must list each required PDF exactly once.")
    return entries


def read_pdf(content: bytes) -> PdfReader:
    try:
        reader = PdfReader(BytesIO(content), strict=True)
        if reader.is_encrypted:
            raise ValueError("Encrypted PDFs are not supported.")
        if not 1 <= len(reader.pages) <= 100:
            raise ValueError("Each demonstration PDF must contain 1 to 100 pages.")
        metadata = reader.metadata
        if metadata is None or metadata.author != AUTHOR or metadata.subject != NOTICE:
            raise ValueError("Use only the generated synthetic PDFs with neutral metadata.")
        root = reader.trailer["/Root"]
        if any(key in root for key in ("/AcroForm", "/OpenAction", "/AA", "/Names")):
            raise ValueError("Forms, actions, and named resources are outside the demo scope.")
        for page in reader.pages:
            if "/Annots" in page or "/AA" in page:
                raise ValueError("Annotated or interactive PDF pages are outside the demo scope.")
            if NOTICE not in (page.extract_text() or ""):
                raise ValueError("Every source PDF page must carry the synthetic notice.")
        return reader
    except PdfReadError as error:
        raise ValueError("Unreadable PDF input; no document was skipped.") from error


def index_pdf(content: bytes) -> bytes:
    # Fixed-width splitting keeps every ASCII character; long lines are not clipped.
    lines: list[str] = []
    for line in content.decode("ascii").expandtabs(4).splitlines():
        lines.extend([line[start:start + 100] for start in range(0, len(line), 100)] or [""])
    pages = [lines[start:start + 65] for start in range(0, len(lines), 65)]
    return render_pdf("Synthetic index - raw XML rendering", pages)


def build(source: Path, output: Path) -> dict[str, object]:
    if source.is_symlink() or not source.is_dir():
        raise ValueError("Input must be a local synthetic package directory.")
    actual = {path.name for path in source.iterdir()}
    if actual != REQUIRED_PDFS | {"index.xml"}:
        raise ValueError("Input package must contain exactly index.xml and the two invented PDFs.")
    if any(not path.is_file() or path.is_symlink() for path in source.iterdir()):
        raise ValueError("Input package must contain regular files, not folders or symbolic links.")
    inputs = {name: (source / name).read_bytes() for name in sorted(actual)}
    entries = read_index(inputs["index.xml"])
    note = render_pdf("Synthetic archive note", [[
        "Archive: DEMO-ARCHIVE-A",
        "Purpose: demonstrate deterministic document assembly.",
        "Order: archive note, rendered index, documents in index order.",
        "Original XML and source PDF bytes are retained.",
        "No signature, regulatory approval, or RIMS upload is performed.",
        "Page counts and hashes do not establish completeness or authenticity.",
    ]])
    files = {"index.xml": inputs["index.xml"], "archive-note.pdf": note,
             "index-rendering.pdf": index_pdf(inputs["index.xml"])}
    files.update({name: inputs[name] for name, _ in entries})
    order = [("archive-note.pdf", "Synthetic archive note"),
             ("index-rendering.pdf", "Synthetic index")] + entries
    writer = PdfWriter()
    writer.add_metadata({"/Author": AUTHOR, "/Creator": AUTHOR, "/Title": "Synthetic submission archive",
                         "/Subject": NOTICE})
    components: list[dict[str, object]] = []
    page_total = 0
    try:
        for name, title in order:
            reader = read_pdf(files[name])
            count = len(reader.pages)
            for page in reader.pages:
                writer.add_page(page)
            writer.add_outline_item(title, page_total)
            components.append({"file": name, "title": title, "pages": count,
                               "start_page": page_total + 1, "end_page": page_total + count,
                               "sha256": sha256(files[name]).hexdigest()})
            page_total += count
        merged = BytesIO()
        writer.write(merged)
        files["merged-archive.pdf"] = merged.getvalue()
    finally:
        writer.close()
    actual_pages = len(read_pdf(files["merged-archive.pdf"]).pages)
    if actual_pages != page_total:
        raise ValueError("Merged page count does not equal the component total.")
    manifest: dict[str, object] = {
        "schema_version": 1, "synthetic": True, "archive_id": "DEMO-ARCHIVE-A",
        "review_status": "NOT APPROVED", "components": components,
        "index": {"file": "index.xml", "sha256": sha256(inputs["index.xml"]).hexdigest()},
        "merged": {"file": "merged-archive.pdf", "pages": actual_pages,
                   "sha256": sha256(files["merged-archive.pdf"]).hexdigest()},
        "checks": {"expected_pages": page_total, "actual_pages": actual_pages, "page_count_matches": True},
    }
    files["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
    rows = "".join(
        f'<tr><td>{escape(str(item["title"]))}</td><td>{item["pages"]}</td>'
        f'<td>{item["start_page"]}-{item["end_page"]}</td></tr>' for item in components
    )
    files["preview.html"] = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Synthetic archive preview</title>
<style>
body{{margin:0;background:#edf2f7;color:#17283b;font:16px/1.6 system-ui,sans-serif}}
main{{max-width:900px;margin:32px auto;padding:24px;background:white;border-radius:12px}}
.notice{{padding:16px;background:#fff1dc;border-left:5px solid #aa5700}}
table{{width:100%;border-collapse:collapse}}th,td{{padding:12px;text-align:left;border-bottom:1px solid #ccd7e2}}
a{{color:#164a7b}}@media(max-width:640px){{main{{margin:0;padding:16px}}}}
</style></head><body><main>
<p>REGULATORY WORKFLOW DEMO / OFFLINE ARCHIVING</p><h1>Submission archive preview</h1>
<p class="notice">{NOTICE}</p><p><strong>DRAFT - NOT APPROVED</strong> | DEMO-ARCHIVE-A</p>
<p>{actual_pages} pages assembled. Component page totals match.</p>
<p><a href="merged-archive.pdf">Open bookmarked archive PDF</a> |
<a href="manifest.json">Inspect manifest and hashes</a> | <a href="index.xml">Preserved XML</a></p>
<table><thead><tr><th>Component</th><th>Pages</th><th>Archive pages</th></tr></thead><tbody>{rows}</tbody></table>
<p>Review content, ordering, legibility, and bookmarks. Matching counts do not prove
completeness or correctness; hashes do not prove authenticity. No RIMS access or upload occurs.</p>
</main></body></html>""".encode("utf-8")
    publish(files, output)
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    fixtures = commands.add_parser("fixtures", help="Generate an invented three-file package.")
    fixtures.add_argument("--output", type=Path, required=True)
    archive = commands.add_parser("build", help="Assemble an invented package.")
    archive.add_argument("--input", type=Path, required=True)
    archive.add_argument("--output", type=Path, required=True)
    archive.add_argument("--confirm-synthetic", action="store_true", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "fixtures":
            create_fixtures(args.output)
        else:
            build(args.input, args.output)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"Error: file operation failed ({error.strerror or 'I/O error'}). "
              "Do not use an incomplete output package.", file=sys.stderr)
        return 1
    print(f"{NOTICE}. Completed {args.command}; inputs were not modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
