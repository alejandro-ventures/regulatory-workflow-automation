# Annual report composer demo

[Portfolio](../README.md) | [Case study](../case-studies/fda-annual-report-composer.md) |
[Source](report_composer.py) | [Invented input](../fixtures/reporting/annual-report.json) |
[Tests](../tests/test_report_composer.py)

Also available: [offline reference-monitor demo](MONITOR.md) and
[archive-builder demo](ARCHIVE.md).

An offline demonstration that turns invented structured data into two reviewable
DOCX drafts and a self-contained HTML preview. The layouts were authored for this
showcase in Python; no corporate templates or operational source code are used.

**DEMONSTRATION ONLY - NOT FOR REGULATORY SUBMISSION**

## Run on Windows

Requires Python 3.11 or newer. From the repository root in PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
.\.venv\Scripts\python.exe -m demos.report_composer --input fixtures\reporting\annual-report.json --output output\report-demo --confirm-synthetic
Start-Process .\output\report-demo\preview.html
```

If you have a different supported Python version, select it in the first command.
Activation is not necessary. Once installed, the equivalent CLI is:

```powershell
.\.venv\Scripts\report-demo.exe --input fixtures\reporting\annual-report.json --output output\another-demo --confirm-synthetic
```

On macOS or Linux, create the environment with `python3 -m venv .venv` and use
`.venv/bin/python` for the install and module commands. Use the same input and
output locations with your platform's path separators.

The initial dependency installation may require network access. Generation itself
does not use a network, live accounts, external fonts, scripts, or remote assets.

## Expected result

The supplied fixture produces:

| Output | Contents |
|---|---|
| `cover-letter.docx` | Fictional companion letter, metadata table, two-record amendment count, and review notice. |
| `annual-report.docx` | Metadata table, two amendment rows in input order, and reviewer checklist. |
| `preview.html` | Input summary, amendment table, review notices, and relative links to both DOCX drafts. |

Expected values:

```text
Product: Example Material Alpha
Dossier: DEMO-DOSSIER-A
Reporting year: 2030
Prepared on: 2031-01-15
Amendments: DEMO-SEQUENCE-A, DEMO-SEQUENCE-B
Review status: DRAFT - NOT APPROVED
```

Open the HTML file locally in a browser. GitHub's file viewer does not render
arbitrary HTML as a live application. DOCX pagination can vary between viewers;
this demo does not promise fixed page counts or byte-identical files.

Generated files live under the ignored `output` directory. They are not intended
to be committed or automatically uploaded.

## Input contract

See the [fixture](../fixtures/reporting/annual-report.json) for the complete schema.
All fields are required; unknown and duplicate JSON fields are rejected.

- `synthetic`: must be the Boolean `true`.
- `product`: nonempty text, at most 200 characters.
- `dossier`: an invented uppercase `DEMO-` identifier, at most 60 characters.
- `reporting_year`: integer from 2000 to 2100.
- `prepared_on`: valid `YYYY-MM-DD` date, not before the reporting year.
- `amendments`: zero to 100 records, each with a unique demonstration `sequence`,
  valid `date`, and nonempty `description` of at most 1,000 characters.
- Amendment dates must fall in the reporting year and not exceed `prepared_on`.
- Control characters and invalid XML characters are rejected.

The calendar-year rule is a simplification for this demo, not a statement of
regulatory reporting requirements. The synthetic flag and demonstration IDs
are guardrails, not automated proof that text contains no private information.
Use invented descriptions and product labels only.

## Failure behavior

- `--confirm-synthetic` is required as an explicit user acknowledgement.
- Invalid input returns an error and does not start output generation.
- Existing output directories are rejected; select a fresh directory for each run.
- All three files are rendered in memory before creating the output directory.
  The directory and files are created exclusively, and failed writes trigger
  cleanup of files created by that run. Generation is not an atomic directory
  transaction; consumers must wait for the CLI's successful exit.
- File-system errors return a nonzero exit status without exposing absolute
  paths in ordinary CLI error messages. Unexpected programming errors are not hidden.
- File-system locks or permissions can prevent writing or cleanup. Such errors
  are surfaced rather than hidden; inspect the output after an error and do not
  assume generation succeeded.

## Test

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_report_composer.py -v
```

For the full suite, install `".[monitor,archive]"` and omit the `-p` selector.

Tests check validation, malformed JSON, empty amendment lists, exact DOCX table
values, neutral author metadata, demonstration labels, HTML escaping, overwrite
protection, staged-output cleanup, and CLI exit behavior.

The [CI workflow](../.github/workflows/tests.yml) defines the supported test matrix
and demo commands. Check the [Actions results](https://github.com/dbstudioai/regulatory-workflow-automation/actions)
for the exact commit being evaluated; configuration alone is not evidence of a
successful run or permission to publish.

## Deliberate limits

This is a new generic demonstration, not a public release of the operational FDA
report generator. It does not extract previous reports, parse submission packages,
assess completeness, manage operational records, provide signatures, or submit
anything. Outputs remain unapproved drafts. Ownership and disclosure review are
required for each release; public availability is not evidence of that approval.
