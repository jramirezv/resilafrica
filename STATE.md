# STATE — the resume contract (overwrite, never append; keep ≤40 lines)

> New session, post-compaction, or "go": read CLAUDE.md, then THIS file, then act on the
> top next action. No questions unless an open gate says so.

**Harness live, repo public, PII gate repo-wide · awaiting first dashboard spec · 2026-10-23**

## In flight
- Nothing.

## Next actions (in order)
1. Wait for the owner's first spec. On arrival: record it in SPEC.md (purpose + numbered
   requirements, each with a verify method) BEFORE writing code.
2. Ask for data sources if the spec does not name them; register each in
   `site/data/manifest.json` as it lands.

## Open gates
- None.

## Last verification
- 2026-10-23 · local gate 11/11 (repo-wide PII scan added; negative test: planted email +
  phone in a tracked file caught, gitignored `raw/` correctly not scanned).
- 2026-10-23 · after the squash: CI run 39997757548 green (gate 17s, deploy 29s);
  `verify.py --live` 14/14; remote history = 1 commit, noreply identity.

## Standing context
- Repo `jramirezv/resilafrica`, public since 2026-10-23 (owner's instruction). Pages
  build_type = workflow; deploys from `.github/workflows/pages.yml` on push to `main`.
- Commit identity: repo-local `user.email` = the GitHub noreply address. Keep it.
- History squashed 2026-10-23 into one root commit (owner's instruction, force-push);
  every earlier SHA is superseded. Never rewrite published history again without asking.
- Preview: `preview_start` name `site` (port 8765).
