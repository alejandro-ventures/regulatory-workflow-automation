# Offline archive builder

[Portfolio](../README.md) | [Case study](../case-studies/rims-archive-preparation.md) |
[Source](archive_builder.py) | [Tests](../tests/test_archive_builder.py)

**Synthetic demonstration only. No RIMS access, real submissions, or corporate templates.**

This small demo generates an invented package and assembles it into a bookmarked
PDF. It demonstrates document ordering, raw XML rendering, page-count checks,
relative-file manifests, and SHA-256 hashes. It does not automate system uploads
or determine whether a submission is complete.

## Run locally

From the repository root in PowerShell, using the existing showcase environment:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[archive]"
.\.venv\Scripts\python.exe -m demos.archive_builder fixtures --output output\archive-inputs
.\.venv\Scripts\python.exe -m demos.archive_builder build --input output\archive-inputs --output output\archive-demo --confirm-synthetic
Start-Process .\output\archive-demo\preview.html
```

For a fresh checkout, first create an environment with `py -3.11 -m venv .venv`.
Python 3.11 or newer is required. Select the showcase's own environment in VS Code
if the editor reports missing optional packages.

The installed `archive-demo` command provides the same `fixtures` and `build`
subcommands. On other platforms use `.venv/bin/python` and platform-appropriate
path separators. Initial dependency installation may need network access; both
demo commands run offline.

Choose new output directories when repeating the commands: existing directories
are rejected, not overwritten. Binary examples are generated locally, remain
ignored by Git, and do not need to be uploaded.

## Inputs and outputs

The fixture command produces exactly three files:

- `index.xml`: explicitly synthetic archive `DEMO-ARCHIVE-A`, defining document order.
- `acknowledgement.pdf`: one page of invented receipt text, not an authority receipt.
- `dossier.pdf`: two pages about fictional Example Material Alpha.

The archive command produces eight files:

| File | Expected content |
|---|---|
| `index.xml` | Byte-preserved original index. |
| `archive-note.pdf` | One-page generic note and limitations. |
| `index-rendering.pdf` | One-page raw XML rendering for the default fixture. |
| `acknowledgement.pdf` | Byte-preserved source PDF, one page. |
| `dossier.pdf` | Byte-preserved source PDF, two pages. |
| `merged-archive.pdf` | Five pages and four top-level bookmarks. |
| `manifest.json` | Component order, page ranges, counts, and SHA-256 hashes. |
| `preview.html` | Local summary linking to the archive, manifest, and XML. |

Expected assembly order and bookmark starts:

```text
1  Synthetic archive note
2  Synthetic index
3  Invented acknowledgement
4  Invented dossier (continues on page 5)
```

The default page-count check is `1 + 1 + 1 + 2 = 5`. Longer XML is wrapped in a
fixed-width font and paginated; the manifest uses actual counts rather than
assuming the index always fits one page.

## Validation and integrity boundaries

- The input folder must contain exactly the expected three regular files.
  Missing, extra, duplicate index entries, symbolic links, and unexpected paths fail.
- XML requires the demo schema and printable ASCII titles. DTDs/entities are rejected.
- PDF inputs must be readable, unencrypted, contain 1 to 100 pages, have the
  neutral demo author/subject, and display the synthetic notice on every page.
- Forms, annotations, document actions, and named resources are outside the demo scope.
- Inputs are never changed. Original XML and source PDF bytes are retained in output.
- The merged PDF is reopened to verify its page total against the components.
- The manifest contains only relative filenames, with hashes for the XML,
  each component, and the merged archive.
- All rendering and checking happens before output creation. Write failures trigger
  cleanup of files created by that run. File locks may prevent cleanup and surface
  as errors. Wait for successful CLI exit before consuming any output.

This is not a PDF sanitizer, signature validator, malware scanner, archival-format
certifier, or crash-safe transaction system. Neutral metadata and synthetic labels
do not establish that arbitrary input is safe or nonconfidential. Use only the
generated fixtures; do not pass real packages or large/untrusted documents.

Equal page counts do not prove content correctness, ordering, legibility, or source
completeness. Hashes support comparison, not authenticity. A human must inspect the
result. No approved status, signature, submission, or RIMS upload is produced.

## Tests and verification

Archive-only:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_archive_builder.py -v
```

All demos:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[monitor,archive]"
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Tests check page totals, bookmark destinations, component hashes, actual text,
neutral metadata, unchanged inputs, long-index pagination, invalid input,
overwrite protection, write-failure cleanup, and CLI confirmation/errors.
The [CI workflow](../.github/workflows/tests.yml) defines the test matrix and demo
commands. Check the [Actions results](https://github.com/dbstudioai/regulatory-workflow-automation/actions)
for the exact commit being evaluated; configuration alone is not evidence that
the checks passed.
