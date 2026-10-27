# Publication checklist

[Back to portfolio](README.md)

This checklist supports a deliberate release review. It is not a certification
that a repository is safe to publish.

## Current scope

This showcase was authored separately from operational projects. It contains
high-level case studies, invented examples, and a newly authored generic report
demo and offline reference monitor, not copied operational implementation files
or production outputs.
Generated local outputs and the development environment are ignored; upload only
the reviewed source and fixture set, not the whole working directory.
The published baseline is available at
[regulatory-workflow-automation](https://github.com/dbstudioai/regulatory-workflow-automation).
New local changes, including additional demos, require their own review before upload.
Local environments, installation metadata, caches, and generated outputs are
excluded from that publication set.

## Before the first public upload

### Ownership and permissions

- [ ] Confirm permission to disclose the workflow descriptions and project concepts.
- [ ] Confirm ownership and publication rights before adding any code or assets.
- [ ] Do not select an open-source license until the rights to license material
      are established. No license is supplied with this initial showcase.
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
- [ ] Start with fresh Git history inside this showcase folder; do not import
      operational repositories or their history.
- [ ] Use an appropriate privacy-preserving Git author identity. Review all
      authors, email addresses, trailers, commit messages, remotes, and branch names.
- [ ] Review the actual staged diff and use an approved local secret scanner
      where available. Automated scanning does not replace manual disclosure review.

### Accuracy and release

- [ ] Keep synthetic examples clearly labeled and do not present them as test results.
- [ ] Do not claim measured savings, validated operation, completeness, compliance,
      authority endorsement, or production readiness without supporting evidence.
- [ ] Preserve the distinction between document preparation and human approval.
- [ ] Perform the initial review in a private repository if permitted, then
      obtain any required approval before changing visibility.
- [ ] Inspect the final GitHub rendering, links, diagrams, and downloadable files.

## For runnable demos

Build a standalone example from synthetic fixtures rather than publishing a
redacted copy of production code. Give it explicit inputs, expected outputs,
tests, and documented limitations. Do not require live accounts, private
services, or real regulatory records.

The ignore rules are only a safety net. They do not inspect content, remove
already tracked files, or establish publication permission.
