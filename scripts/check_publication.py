"""Check the exact Git publication set. This is not a confidentiality detector."""
from __future__ import annotations

import argparse
from pathlib import Path, PurePosixPath
import subprocess
import sys

MANIFEST = "publication-files.txt"
MAX_FILE_BYTES = 1_000_000
MAX_TOTAL_BYTES = 5_000_000


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=root, stderr=subprocess.PIPE)


def inventory(root: Path, ref: str | None) -> dict[str, tuple[str, str]]:
    """Return path -> (mode, blob SHA) for a commit or the staged index."""
    args = ("ls-tree", "-rz", ref) if ref else ("ls-files", "--stage", "-z")
    entries: dict[str, tuple[str, str]] = {}
    for record in git(root, *args).split(b"\0"):
        if not record:
            continue
        metadata, name = record.split(b"\t", 1)
        fields = metadata.decode("ascii").split()
        path = name.decode("utf-8", errors="strict")
        if ref:
            mode, kind, sha = fields
            if kind != "blob":
                raise ValueError("Submodules and non-file entries are not allowed.")
        else:
            mode, sha, stage = fields
            if stage != "0":
                raise ValueError("Resolve all merge conflicts before publication.")
        if mode not in {"100644", "100755"}:
            raise ValueError("Only regular files are allowed; no links or submodules.")
        entries[path] = (mode, sha)
    return entries


def parse_manifest(content: str) -> set[str]:
    paths: set[str] = set()
    for line in content.splitlines():
        if not line or line.startswith("#"):
            continue
        path = PurePosixPath(line)
        if (line != line.strip() or path.is_absolute() or ".." in path.parts
                or "\\" in line or ":" in line or str(path) != line):
            raise ValueError("Manifest entries must be canonical relative file paths.")
        if line in paths:
            raise ValueError("Manifest contains duplicate entries.")
        paths.add(line)
    if MANIFEST not in paths:
        raise ValueError("The publication manifest must include itself.")
    return paths


def check(root: Path, ref: str | None = "HEAD") -> int:
    entries = inventory(root, ref)
    if MANIFEST not in entries:
        raise ValueError("Publication manifest is missing from the selected Git tree.")
    total = 0
    contents: dict[str, str] = {}
    for path, (_, sha) in entries.items():
        size = int(git(root, "cat-file", "-s", sha))
        total += size
        if size > MAX_FILE_BYTES or total > MAX_TOTAL_BYTES:
            raise ValueError("Publication exceeds the reviewed text-file size limits.")
        raw = git(root, "cat-file", "blob", sha)
        if b"\0" in raw:
            raise ValueError("Binary content is outside the reviewed publication scope.")
        try:
            contents[path] = raw.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError("Only UTF-8 text files are in the publication scope.") from error
    allowed = parse_manifest(contents[MANIFEST])
    if allowed != set(entries):
        # Do not print unexpected filenames: they may themselves identify a person.
        added = len(set(entries) - allowed)
        missing = len(allowed - set(entries))
        raise ValueError(f"Inventory mismatch: {added} unlisted and {missing} missing files. Review the Git diff and manifest.")
    return len(entries)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--ref", default="HEAD", help="Commit/ref to inspect (default: HEAD).")
    selection.add_argument("--staged", action="store_true", help="Inspect staged blobs, not working-directory files.")
    args = parser.parse_args(argv)
    try:
        count = check(Path.cwd(), None if args.staged else args.ref)
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        message = str(error) if isinstance(error, ValueError) else "Unable to read the selected Git tree."
        print(f"Publication check failed: {message}", file=sys.stderr)
        return 1
    print(f"Publication inventory passed: {count} reviewed text-file paths. Content and disclosure approval still require human review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
