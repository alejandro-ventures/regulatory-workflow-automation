# Synthetic walkthroughs

[Back to portfolio](../README.md)

All records below were invented specifically for this showcase. They are
manually authored illustrations, not production extracts, captured runs, or
executable tests. Dates and identifiers have no operational meaning.

**Demonstration only. Not for regulatory submission.**

## 1. EDQM Reference Monitor

### Illustrative inputs

| Publication | Reference ID | Reference title | Change |
|---|---|---|---|
| DEMO-PUBLICATION-A | DEMO-REF-A | Example Substance Alpha | Revision |
| DEMO-PUBLICATION-A | DEMO-REF-B | Example Substance Beta | New entry |

Interest list: `DEMO-REF-A`. Previously processed publications: none.

### Illustrative result

```text
New publication: DEMO-PUBLICATION-A
General notification: publication available for review
Relevant match: DEMO-REF-A / Example Substance Alpha
Targeted notification: assess the source change
```

On a subsequent run with that publication recorded as processed, the same
publication would not be treated as new. This illustration does not test
notification delivery or failure recovery.

## 2. USP Update Review Assistant

### Illustrative export rows

| Name | Document type | Revision type | Date |
|---|---|---|---|
| Example Substance Alpha | Monograph | Revision | 2030-01-15 |
| Example Substance Beta | Monograph | New entry | 2030-01-15 |
| Example General Topic | Chapter | Revision | 2030-01-15 |

Interest list: `Example Substance Alpha`. Previously observed records: none.

### Illustrative result

```text
Rows supplied: 3
Monograph candidates: 2
Relevant matches: 1
Match: Example Substance Alpha / exact name
Next action: reviewer checks the source listing
```

The chapter row is outside the illustrated filter. The nonmatching monograph
can still be recorded as observed. No real portal export or reference text is used.

## 3. FDA Annual Report Composer

For an actual runnable example with two invented amendments, see the
[report demo](../demos/README.md). The single-amendment preview below remains a
manually authored illustration, not its expected output.

### Illustrative candidate fields

| Field | Invented value |
|---|---|
| Product label | Example Material Alpha |
| Dossier reference | DEMO-DOSSIER-A |
| Reporting period | 2030 |
| Candidate amendment | DEMO-SEQUENCE-B: illustrative administrative update |
| Confirmation | Required before generation |

### Illustrative draft preview

```text
DEMONSTRATION ONLY - NOT FOR REGULATORY SUBMISSION

Draft annual report overview
Product: Example Material Alpha
Dossier: DEMO-DOSSIER-A
Reporting period: 2030

Amendments for reviewer confirmation:
- DEMO-SEQUENCE-B: illustrative administrative update

Companion output: draft cover letter
Review status: not approved
```

These deliberately nonoperational identifiers do not model a valid submission
schema. The preview is not a regulatory template or an actual generated file.

## 4. RIMS Archive Preparation Assistant

### Illustrative input set

```text
demo-package/
  submission-index.xml
  acknowledgement.pdf
  dossier.pdf
```

### Illustrative prepared output

```text
demo-archive/
  submission-index.xml       retained source
  archive-note.pdf           1 page
  index-rendering.pdf        2 pages
  acknowledgement.pdf       1 page
  dossier.pdf               6 pages
  merged-archive.pdf         10 pages, with bookmarks
```

Illustrative page-count check: `1 + 2 + 1 + 6 = 10`.

These are conceptual filenames, not files included in this repository.
Matching totals only illustrate the assembly check; a reviewer must still inspect
content, ordering, legibility, and bookmarks. RIMS upload and workflow updates
remain manual.
