# Offline reference monitor

[Portfolio](../README.md) | [EDQM case study](../case-studies/edqm-reference-monitor.md) |
[USP case study](../case-studies/usp-update-review-assistant.md) |
[Source](reference_monitor.py) | [Tests](../tests/test_reference_monitor.py)

**Synthetic demonstration. No live access, account credentials, or company data.**

Two local adapters feed a common review queue:

- **EDQM-style:** an invented RSS feed points to an invented XML-compatible HTML
  table. The layout is not a copy of an EDQM page.
- **USP-style:** a locally generated spreadsheet contains invented change records.
  It is not a real USP export or an exact replica of its schema.

The demo identifies references of interest, distinguishes identifier/exact-name/
substring matches, and records successful local processing. Nothing is emailed,
scheduled, submitted, or assessed for regulatory impact.

## Run the three scenarios

Use Python 3.11 or newer. From the repository root in PowerShell, create the
environment if needed, then install the monitor extra:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[monitor]"
.\.venv\Scripts\python.exe -m demos.monitor_fixtures --output output\monitor-inputs
```

Skip the environment-creation command if the showcase environment already exists.
Package installation may use the network; generation and monitoring do not.
The [fixture generator](monitor_fixtures.py) creates baseline and revised XLSX
files with neutral author metadata under the ignored output directory.

For editor diagnostics, select this showcase's `.venv` interpreter in VS Code.
A different workspace interpreter may report missing optional monitor dependencies
even when the commands above work.

Define the common local inputs:

```powershell
$inputs = @(
  '--feed', 'fixtures\monitoring\feed.xml',
  '--interests', 'fixtures\monitoring\interests.json',
  '--confirm-synthetic'
)
```

**1. First observation**

```powershell
.\.venv\Scripts\python.exe -m demos.reference_monitor @inputs --spreadsheet output\monitor-inputs\baseline.xlsx --output output\monitor-first
Start-Process .\output\monitor-first\preview.html
```

**2. Identical repeat, carrying forward the first checkpoint**

```powershell
.\.venv\Scripts\python.exe -m demos.reference_monitor @inputs --spreadsheet output\monitor-inputs\baseline.xlsx --previous output\monitor-first\state.json --output output\monitor-repeat
```

**3. Revised record, carrying forward the second checkpoint**

```powershell
.\.venv\Scripts\python.exe -m demos.reference_monitor @inputs --spreadsheet output\monitor-inputs\revised.xlsx --previous output\monitor-repeat\state.json --output output\monitor-revised
```

Each command needs a new output directory. Rerunning these commands against
existing directories fails rather than overwriting evidence. Choose new directory
names to repeat the walkthrough.

The installed `monitor-demo` entry point accepts the same arguments. On other
platforms, use `.venv/bin/python`, the appropriate path separators, and individual
arguments instead of the PowerShell `$inputs` array.

## Verified expected results

| Scenario | Distinct monograph records | New records | Review candidates |
|---|---:|---:|---:|
| First | 5 | 5 | 3 |
| Identical repeat | 5 | 0 | 0 |
| Revised spreadsheet | 5 | 1 | 1 |

The first queue contains:

| Source | Invented reference | Reason |
|---|---|---|
| EDQM-style | DEMO-REF-A / Example Substance Alpha | Reference identifier |
| USP-style | DEMO-REF-C / Example Substance Gamma | Exact name |
| USP-style | DEMO-REF-D / Example Substance Gamma Hydrate | Substring name; verify relevance |

Two other monograph records do not match. A spreadsheet chapter is filtered out.
Both matching and nonmatching monographs are recorded as observed. The revised
fixture changes the revision and date of DEMO-REF-C; it does not add a new product.

## Outputs and state contract

Each completed run creates:

| File | Purpose |
|---|---|
| `review-queue.json` | Versioned structured output with summary counts and matching candidates. |
| `preview.html` | Local browser review queue with labels, context, and match reasons. |
| `state.json` | Versioned checkpoint for an explicitly selected later run. |

The JSON queue has `schema_version`, `synthetic`, `summary`, and `candidates`.
Summary fields are `observed`, `new_records`, `matches`, `already_seen`, and
`duplicates`. Each candidate has a fingerprint, a normalized record, and match
reasons with interest identifiers.

A record includes source, source record identifier, reference identifier, name,
revision, date, and descriptive source context. Its SHA-256 fingerprint covers
all those normalized fields, including source identity. The hash is a local
deduplication key, not proof of authenticity or an audit signature.

- Exact duplicate records within a run collapse to one.
- A changed revision, date, name, or context is a newly observed version.
- Records no longer present in current inputs remain in the accumulated checkpoint.
- A previously observed version that reappears is not new.
- Omitting `--previous` deliberately starts a fresh assessment.
- A missing, malformed, incompatible, or corrupt checkpoint fails explicitly.
- Changing interest IDs, names, or substring settings requires a fresh assessment.
  Reordering otherwise identical interests does not.

This design compares record versions, not publication announcements as a whole,
and does not detect deletions or determine whether a revision is newer than another.

## Input boundaries and failure behavior

The [feed](../fixtures/monitoring/feed.xml),
[announcement](../fixtures/monitoring/announcement.html), and
[interest list](../fixtures/monitoring/interests.json) are invented source fixtures.
Spreadsheet input must have a single `Synthetic changes` sheet with literal
columns `Reference ID`, `Name`, `Document type`, `Revision`, and `Date`.

Identifiers require a `DEMO-` prefix; dates require valid ISO calendar dates.
Names and revisions must be nonempty text. Whitespace is normalized; name
matching is case-insensitive. Substring matching is opt-in per interest and is
always labeled as requiring relevance review.

Feed links must be local HTML basenames within the fixture directory. URLs,
path traversal, XML entities/DTDs, invalid schemas, and spreadsheet formulas are
rejected. The synthetic markers are guardrails, not a private-data detector.
Do not pass operational documents or arbitrary untrusted large files.

All input parsing and rendering completes before creating the output directory.
The queue and preview are written before the checkpoint. Failed writes trigger
cleanup of this run's files; the previous checkpoint is never changed.
File locks or permission failures can prevent cleanup and are surfaced explicitly.
Do not consume outputs until the command exits successfully.

There is no shared mutable state or automatic selection of the latest checkpoint.
Concurrent runs using the same previous checkpoint can produce the same candidates.
This is not an exactly-once notification service or a crash-safe database.

## Test and limitations

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -p test_reference_monitor.py -v
```

Install the monitor extra before running these tests. For the full suite, install
`".[monitor,archive]"` and omit the `-p` selector. Tests cover both adapters,
all three scenarios, matching reasons, chapter filtering, duplicate handling,
changed interests, invalid inputs/checkpoints, escaped HTML, output collisions,
write/render failures, and offline execution. The existing report tests also run.

The [CI workflow](../.github/workflows/tests.yml) defines the test matrix and
commands for all three demos. Check the [Actions results](https://github.com/dbstudioai/regulatory-workflow-automation/actions)
for the exact commit being evaluated; configuration alone does not establish
that the checks passed.

This demo intentionally excludes source acquisition, portal authentication,
real source parsing, email delivery, and scheduling. A match is a review
candidate, not regulatory advice.
