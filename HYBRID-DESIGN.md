# Hybrid portfolio design

[Back to portfolio](README.md)

**Status: report-composer and offline monitoring demos implemented; archive demo remains proposed.**

The [report demo instructions](demos/README.md) describe the implemented scope.
It uses a single module with generic layouts defined in Python, rather than a
package directory or external templates. This keeps the first demo small and
avoids redistributing binary templates.

The [monitor demo](demos/MONITOR.md) uses one module for both local adapters and
a small spreadsheet fixture generator. Each run writes an immutable checkpoint
after its review outputs; later runs explicitly select a previous checkpoint.
No live source adapters or notification delivery are included.

## 1. Positioning

**Regulatory Workflow Automation**

> Practical automation for reference monitoring, report drafting, and submission
> archive preparation, demonstrated with synthetic data.

The portfolio should offer two reading paths:

- **A two-minute overview:** understand the problem, see an output, and identify
  the human-review boundary.
- **A technical deep dive:** inspect runnable source, execute a synthetic example,
  and read tests for meaningful failure cases.

Keep the four existing case studies. Add three standalone demonstration modules:
one monitoring demo with distinct EDQM-style and USP-style input adapters, one
report composer, and one archive builder. These are portfolio implementations,
not claims that the original operational tools have been released or validated.

## 2. Repository and visitor experience

Start with one repository, rather than four small repositories. A visitor can
see the full story and run the demos without navigating separate installations.
Split a demo out only if it develops an independent audience or release cycle.

The landing page should contain, in order:

1. A short purpose statement and synthetic-data notice.
2. A preview of the report and archive outputs.
3. Four project cards linking to a case study and the relevant demo.
4. A quick-start section with one command per demo.
5. A compact architecture overview.
6. Verified test status, limitations, and publication boundaries.

Use neutral styling, no authority or company logos, and no fabricated metrics.
Prefer cropped previews generated from synthetic outputs over screenshots of
workstations, terminals, browsers, or internal applications.

### Proposed additions

```text
demos/
  reference_monitor/
  report_composer/
  archive_builder/
fixtures/
  monitoring/
  reporting/
  archiving/
tests/
previews/
.github/
  workflows/
    tests.yml
pyproject.toml
```

This tree describes the target structure, not a list of completed deliverables.
Keep the existing case studies and example walkthroughs. Store generated files
under an ignored output directory, not beside the inputs.

## 3. Demonstration contracts

### A. Reference monitor: two sources, one review queue

**Demonstrates:** parsing, normalization, matching, state management, and traceable
review candidates.

- **EDQM-style input:** invented RSS and a local HTML announcement with invented
  reference rows. No downloaded source pages or copied publication text.
- **USP-style input:** a locally generated synthetic spreadsheet of changes.
  No subscription export, portal login, or browser profile.
- **Other inputs:** a fictional interest list and explicit local state.
- **Outputs:** a structured JSON review queue and an HTML notification preview.
  Each candidate includes source record identity, match reason, and source context.
- **Visible scenario:** first run identifies relevant entries; a second run with
  the same state produces no new candidates; a changed fixture produces a new entry.

Use separate input adapters but a shared normalized record and matching engine.
Share only genuinely common behavior; do not build a generic scraping framework.

The demo has no network access, scheduling, credentials, or email delivery.
Describe its state as successful local processing, not confirmed notification
delivery. Publish state only after all required local outputs are written
successfully. A failed write must leave the previous state usable and return an
explicit error.

### B. Report composer: structured input to reviewable drafts

**Demonstrates:** input validation, template population, consistent tables, and
explicit review status.

- **Inputs:** a synthetic JSON record containing a fictional product, reporting
  period, demonstration dossier ID, and amendment list.
- **Templates:** newly authored generic layouts, not corporate templates.
- **Outputs:** a DOCX cover letter and annual-report draft, plus an HTML preview.
- **Visible scenario:** inspect sample input, generate drafts, and compare the
  amendment table with the supplied records.

Every output carries a visible demonstration-only and not-approved notice.
Document author properties must use a neutral value, not the operating-system
user. Do not generate signatures, real application numbers, or company details.

The first version deliberately starts from structured input. Extraction from
previous reports and real submission packages remains outside the demo. Explain
this difference from the operational workflow in the case study.

### C. Archive builder: synthetic package to navigable archive

**Demonstrates:** deterministic assembly, XML rendering, PDF bookmarks, and
focused integrity checks.

- **Inputs:** a local synthetic XML index and PDFs generated from invented text.
- **Outputs:** an archive note, rendered index PDF, merged bookmarked PDF, and
  JSON manifest with relative filenames, order, page counts, and file hashes.
- **Visible scenario:** assemble the package, inspect bookmarks and manifest, and
  compare expected and actual page totals.

Preserve the source index and input files. Use an explicit assembly order and
reject missing or ambiguous required inputs. Do not silently skip unreadable or
unsupported PDFs. Refuse to overwrite an existing output package by default.

Hashes support comparison, not proof of authenticity. Equal page counts are a
narrow assembly check, not content validation. No RIMS access, upload, internal
filing rules, or automatic workflow closure is included.

## 4. Implementation choices

- Use Python with a small command-line interface for each demo.
- Select and document the supported Python range during implementation, then
  test that range in CI. Do not inherit version claims from the operational tools.
- Use standard-library parsing and state handling where suitable.
- Use focused libraries for spreadsheets, DOCX generation, PDF generation, and
  PDF merging. Choose them when implementing; avoid a web framework initially.
- Keep demo dependencies separable so running the monitor does not require the
  entire document-generation toolchain.
- Provide fixtures and documented expected results. No paid services, API keys,
  corporate network access, or live accounts should be necessary.
- Show clear validation errors and return a nonzero exit status on failure.
- Avoid printing absolute local paths or embedding them in generated artifacts.
- Keep outputs deterministic where practical; fix fixture dates and record order.
  Do not promise byte-identical PDFs or DOCX files unless tested.

## 5. Acceptance tests

| Area | Required checks |
|---|---|
| Monitor | Identifier and exact-name matches; clearly labeled substring matches; irrelevant records excluded; repeated input suppressed; revised records detected. |
| Monitor failures | Malformed input and corrupt state fail explicitly; output-write failure does not mark entries processed; no silent state reset. |
| Report | Required fields validated; input amendments match table rows; both documents produced; demonstration labels and neutral metadata present. |
| Report failures | Missing values and rendering or write failures fail explicitly; no success message for incomplete output. The first demo has no external templates. |
| Archive | Source files unchanged; specified order and bookmarks preserved; total pages correct; manifest counts and hashes match actual files. |
| Archive failures | Missing, unreadable, unsupported, or ambiguous inputs fail explicitly; existing outputs are not overwritten silently. |
| Release | Clean installation; all documented commands run on fixtures; no secrets or personal metadata in the exact release files. |

CI should use synthetic fixtures only and should not receive production secrets.
Add a test-status badge only after the workflow exists and passes. Publish actual
test results rather than presenting these proposed checks as completed evidence.

## 6. Source and disclosure boundary

Other people publishing company code does not establish permission to publish
this code. Removing names and passwords also does not resolve source ownership.

Two routes are possible:

1. **Default:** author focused demonstration implementations using invented
   fixtures and generic layouts. Check that the project concepts themselves may
   be disclosed; new code is not an automatic exemption from employment obligations.
2. **Approved reuse:** include selected existing source only after publication
   rights are confirmed, then review the actual files, dependencies, assets,
   metadata, and history being released.

Do not copy entire working folders or operational Git history. Do not add a license
until the right to license the relevant material is established. Review permissions
before any upload, including a private GitHub repository.

Use the [publication checklist](PUBLICATION-CHECKLIST.md) for the release review.
Keep personal details, credentials, usernames, company affiliations, internal
procedures, and licensed source content outside the release.

## 7. Build sequence and definition of done

1. **Report composer first:** provides an immediately understandable visual result
   and a compact end-to-end demonstration.
2. **Reference monitor second:** adds parsing, matching, and state-management evidence
   while representing the EDQM and USP case studies distinctly.
3. **Archive builder third:** adds document assembly and integrity verification.
4. **Presentation and release:** generate synthetic previews, connect case studies
   to demos, add tested quick starts and CI, then review the exact publication set.

A demo is complete only when its source, synthetic fixtures, expected outputs,
tests, setup instructions, and limitations agree and its documented command works
in a clean environment.

As demos ship, replace documentation-only status notices accurately. Update the
existing ignore rules deliberately for any selected generated preview assets;
do not disable the blanket operational-document exclusions.

**Still outside scope:** production-source copying, repository creation, licensing,
or publication. The report demo was implemented as a subsequent local step.
