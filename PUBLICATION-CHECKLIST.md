# Publication checklist

[Back to portfolio](README.md)

This is a reusable review template, not a completed review or a certification
that the repository is safe to publish. Unchecked boxes do not record the status
of any particular release. Do not mark them complete solely because a scan or test
passed, because material is labeled synthetic, or because the repository is public.

## Current scope

This showcase was authored separately from operational projects. It contains
high-level case studies, invented examples, and a newly authored generic report
demo, offline reference monitor, and archive builder, not copied operational implementation files
or production outputs.
Generated local outputs and the development environment are ignored; upload only
the reviewed source and fixture set, not the whole working directory.
The public repository is available at
[regulatory-workflow-automation](https://github.com/dbstudioai/regulatory-workflow-automation).
Public availability does not establish permission to disclose the workflow concepts
or ownership of the material. Each proposed release or additional upload needs a
review of its exact contents and applicable permissions.
Local environments, installation metadata, caches, and generated outputs are
excluded from that publication set.

## Keep the approval record private

Before publishing a release or further material, maintain a separate record in
an approved private location outside this repository. This document does not
create that record or assert that approval already exists. The private record
should identify:

- The exact commit SHA and any separately distributed files, with their hashes.
- The release scope, intended audience, and applicable source/provenance evidence.
- The person or organization entitled to authorize disclosure of the code,
  assets, and underlying project concepts, and their actual decision and date.
- The reviewer, reviewed surfaces (including history and generated metadata),
  checks performed, findings, unresolved questions, and any limits or exceptions.
- The final publication decision and the version to which it applies.

Do not commit reviewer identities, private source references, employment or customer
details, correspondence, or the approval evidence to this public repository. A
public release note may describe the released scope and test results without
exposing the private record. If necessary rights or permissions are unconfirmed,
resolve that with the appropriate owner before publishing the affected material.
Do not infer consent or manufacture approval to complete the checklist.

## Checklist for each release

### Ownership and permissions

- [ ] Confirm permission to disclose the workflow descriptions and project concepts.
- [ ] Confirm ownership and publication rights before adding any code or assets.
- [ ] Do not select an open-source license until the rights to license material
      are established. This checklist grants no license or publication rights.
- [ ] Review applicable source-service terms before adding integrations or demos.

### Personal information and affiliations

- [ ] Check every file for names, usernames, email addresses, phone numbers,
      signatures, account IDs, local paths, and machine or tenant names.
- [ ] Remove employer and customer names, logos, domains, internal system labels,
      internal procedure references, and business-specific folder conventions.
- [ ] Consider combinations of details that could indirectly identify a business
      or person, even when individual details appear harmless.
- [ ] Check the public GitHub account, profile, repository owner, and repository
      description. File sanitization cannot hide a public account identity.

### Credentials and restricted material

- [ ] Exclude passwords, tokens, connection strings, authentication exports,
      browser profiles, cookies, and session storage.
- [ ] Exclude actual interest lists, submission identifiers, acknowledgments,
      reports, correspondence, and operational logs.
- [ ] Exclude subscription content, exported source tables, and third-party
      documents unless redistribution rights are explicitly established.
- [ ] If a secret has ever been published, revoke or rotate it; deleting a file
      is not sufficient remediation.

### Files, metadata, and history

- [ ] Inspect the exact files selected for upload, including hidden files.
- [ ] Inspect screenshots for browser profiles, tabs, paths, notifications,
      account avatars, and identifying background content.
- [ ] Inspect document properties, comments, tracked changes, embedded objects,
      image metadata, and PDF metadata before adding binary assets.
- [ ] Review all reachable Git history, branches, and tags selected for publication;
      do not import operational repositories or their history. Review accessible
      pull requests, issues, release attachments, and Actions logs/artifacts as
      separate publication surfaces. A current-tree scan does not cover them.
- [ ] Use an appropriate privacy-preserving Git author identity. Review all
      authors, email addresses, trailers, commit messages, remotes, and branch names.
- [ ] Review the actual staged diff and use the repository's automated disclosure
      checks and an approved local secret scanner where available. Automated checks
      do not replace manual content, provenance, or disclosure-permission review.

### Accuracy and release

- [ ] Keep synthetic examples clearly labeled and do not present them as test results.
- [ ] Do not claim measured savings, validated operation, completeness, compliance,
      authority endorsement, or production readiness without supporting evidence.
- [ ] Preserve the distinction between document preparation and human approval.
- [ ] Review new material in an appropriately private location if permitted, then
      obtain any required approval before uploading it or changing visibility.
- [ ] Inspect the final GitHub rendering, links, diagrams, and downloadable files.

## For runnable demos

Build a standalone example from synthetic fixtures rather than publishing a
redacted copy of production code. Give it explicit inputs, expected outputs,
tests, and documented limitations. Do not require live accounts, private
services, or real regulatory records.

## Automated checks and their limits

`publication-files.txt` lists the exact tracked file paths reviewed for this
text-only showcase. Review changes to that inventory as carefully as source
changes. The inventory check rejects unlisted or missing files, symbolic links,
submodules, non-UTF-8 or NUL-containing content, and unexpectedly large files.
It does not determine whether prose or example values are confidential.

Before committing, stage the intended files and inspect the actual index:

```text
git diff --cached
python scripts/check_publication.py --staged
```

For a committed revision, run `python scripts/check_publication.py --ref HEAD`.
The default checks committed blobs, not unstaged working-directory edits.

The **Publication safeguards** workflow checks that inventory and runs Gitleaks
8.30.1 against all fetched Git history with findings redacted. Its downloaded
scanner archive is verified against a fixed SHA-256. Run the same pinned scanner
locally before pushing: `gitleaks git --log-opts="--all" --redact --no-banner .`.
A passing scan does not establish disclosure rights or cover inaccessible old
history, external attachments, or every kind of confidential information. Do not
add broad suppressions; investigate each finding and narrowly document any
confirmed synthetic false positive.

The **Synthetic demo tests** workflow generates bundled fixtures and checks
expanded DOCX/XLSX content and reachable PDF objects for machine-identifying data.
It also fails if demo execution leaves tracked changes or unignored output.
These regressions cover the bundled examples; they do not sanitize arbitrary input.

A repository administrator should require the publication job and all synthetic
demo matrix jobs before merging, and require a review of changes to the workflows
and inventory. Adding workflow files alone does not enable branch protection.
Checks on an already public push cannot prevent that push from being disclosed;
review locally before uploading any new material.

The ignore rules are only a safety net. They do not inspect content, remove
already tracked files, or establish publication permission.
