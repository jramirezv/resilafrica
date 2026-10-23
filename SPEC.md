# SPEC — requirements as given

The owner supplies the specs incrementally. Each one lands here as a numbered requirement
before any code for it is written: what he asked (his wording where it matters), how it
will be verified, and its status. Requirements are never silently rewritten: a change is a
new line in the change log at the bottom, and the requirement is edited to match.

Status: `pending` · `in_progress` · `done` (verification passed, evidence recorded) ·
`broken` · `dropped`.

## Purpose

[TBD — owner to state: who the dashboard is for, the question it answers, the data behind it.]

## Requirements

| ID | Requirement | Verify by | Status | Evidence |
|---|---|---|---|---|
| H1 | Harness: repo, gate, Pages deploy of a placeholder page | `verify.py` green locally and in CI; `verify.py --live` green | done | 2026-10-23: CI run 39996644145 green; `--live` 13/13 |

## Change log

- 2026-10-23 — H1 added (harness setup).
- 2026-10-23 — H1 done (repo made public on the owner's instruction; Pages live).
