"""Create invented baseline and revised spreadsheet exports locally."""

import argparse
from contextlib import ExitStack
from datetime import datetime
from io import BytesIO
from pathlib import Path
import sys

from openpyxl import Workbook

from demos.reference_monitor import COLUMNS


def spreadsheet(revised: bool = False) -> bytes:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Synthetic changes"
    workbook.properties.creator = "Regulatory Workflow Demo"
    workbook.properties.lastModifiedBy = "Regulatory Workflow Demo"
    workbook.properties.title = "Invented change listing - demonstration only"
    workbook.properties.created = datetime(2030, 1, 15)
    workbook.properties.modified = datetime(2030, 1, 15)
    worksheet.append(COLUMNS)
    worksheet.append(("DEMO-REF-C", "Example Substance Gamma", "Monograph",
                      "Revision 2" if revised else "Revision 1",
                      "2030-02-15" if revised else "2030-01-15"))
    worksheet.append(("DEMO-REF-D", "Example Substance Gamma Hydrate", "Monograph", "New entry", "2030-01-15"))
    worksheet.append(("DEMO-REF-E", "Example Substance Delta", "Monograph", "Revision 1", "2030-01-15"))
    worksheet.append(("DEMO-REF-F", "Example General Topic", "Chapter", "Revision 1", "2030-01-15"))
    buffer = BytesIO()
    workbook.save(buffer)
    workbook.close()
    return buffer.getvalue()


def generate(output: Path) -> None:
    if output.exists():
        raise ValueError("Fixture output already exists; choose a fresh directory.")
    files = {"baseline.xlsx": spreadsheet(), "revised.xlsx": spreadsheet(True)}
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        generate(args.output)
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"Error: fixture write failed ({error.strerror or 'I/O error'}).", file=sys.stderr)
        return 1
    print("Created invented baseline.xlsx and revised.xlsx. No source-service content was used.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
