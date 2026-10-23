# resilafrica — project rules

Read this file first, then `STATE.md` (the resume contract: act on its top item), then
`SPEC.md` (the requirements as given so far). `README.md` explains layout and commands;
`log.md` is the append-only journal, consulted on demand and appended to always. The
workspace rules in `~/Code/CLAUDE.md` hold above this file and outrank it.

**What this is.** A small, static dashboard served by GitHub Pages from `site/`. Specs
arrive from the owner incrementally; each lands in `SPEC.md` as a numbered requirement
with a verification method before any code for it is written.

## ABSOLUTE RULES (restate verbatim in every agent brief)

1. **The repo is public, and so is everything in it** (owner's decision, 2026-10-23):
   every tracked file, every commit message, and all git history, not only the served
   site. Nothing is committed that is not fit to be public. `site/` is the served tree; a
   push to `main` IS the deploy.
2. **PII gate, repo-wide.** No person names, email addresses, or phone numbers in any
   tracked file or commit message. This includes the owner: tracked files say "the owner",
   never a name. Allowed: organization names, nameless role titles, place names,
   program/product names, formal literature citations ("X et al. YYYY"), and the GitHub
   handle `jramirezv` where it is functional (repo and Pages URLs). A hit means redact
   (org-anchored descriptors, meaning preserved) and re-scan to zero, or it is not
   committed. `verify.py` blocks the mechanical part (emails, phones) across all tracked
   files; the name scan is a reading duty, never skipped. Commits use the repo-local
   GitHub noreply identity; never override it.
3. **No fabricated data.** Every number on the dashboard traces to a file in `site/data/`
   that is registered in `site/data/manifest.json` with its source and retrieval date.
   Unknown means "not stated", never an estimate. Placeholder or synthetic data is labeled
   as such on the page itself.
4. **`raw/` is an inbox, not an approval.** Source files the owner drops there are
   gitignored and stay local: never commit, modify, or quote them into tracked files.
   Derived data goes to `site/data/` only through a script in `tools/` that can be rerun.
5. **Specs before code.** No feature without a `SPEC.md` entry that says how it is
   verified. A feature is done when its verification passes and the result is recorded in
   `SPEC.md`, never on the builder's feel.

## Stack constraints

- Static HTML/CSS/JS, no build step, no framework unless a spec requires one. Libraries
  are vendored into `site/vendor/` at a pinned version, not loaded from CDNs, so the page
  makes no third-party requests on view. `verify.py` enforces this; an exception needs the
  owner's approval and an entry in `ALLOWED_HOSTS`.
- `tools/` is Python 3.9 stdlib-only, run with `/usr/bin/python3`. No venv, no pip.
- Pages URL: `https://jramirezv.github.io/resilafrica/`. All links in `site/` are
  relative, since the site lives under the `/resilafrica/` subpath.

## Serving facts

- Deploy: `.github/workflows/pages.yml` runs the gate, then publishes `site/` as the Pages
  artifact (Pages build_type = workflow). Root harness files are not served, but they are
  readable in the public repo.
- Noindex (owner, 2026-10-23): every HTML page carries
  `<meta name="robots" content="noindex, nofollow">`. Pages cannot set headers, and a
  `robots.txt` is only honored at the domain root, so the meta tag is the only lever.
  `verify.py` enforces it while `REQUIRE_NOINDEX = True`. Noindex keeps the site out of
  search results; it does not hide the public repo.

## Working style

- **State lives on disk.** Overwrite `STATE.md` (≤40 lines) before ending any turn where
  state changed; append to `log.md` at each milestone (a spec received, a feature done, a
  decision). A new session resumes from `CLAUDE.md` + `STATE.md` + `SPEC.md` alone.
- **Chat replies ≤4 lines by default**: outcome · current · next · gates. Detail goes to
  the files, not chat.
- **Deterministic scripts before agents.** `tools/verify.py` is the evaluator; agents run
  and interpret it, they do not re-implement it. Visual checks use the preview server
  (`.claude/launch.json`, name `site`) and are recorded in `SPEC.md`.
- **Delegation by tier.** Haiku: running checks, mechanical edits. Sonnet: implementing a
  written spec. Fable/Opus: spec interpretation, data provenance, the PII sign-off, changes
  to `tools/verify.py`. The builder never grades its own work.
- **Human gates (stop and ask the owner):** a new external dependency or host; any change
  to the absolute rules; committing data whose source or licence is unclear; lifting
  noindex; rewriting published git history.

## Gate

Green before every commit (CI runs the same command before deploying):

```
/usr/bin/python3 tools/verify.py
```

After every deploy: `/usr/bin/python3 tools/verify.py --live`. Record result and date in
`STATE.md`.

## Commit discipline

Scoped `git add <paths>` only, never `git add -A`. Message prefix `resilafrica:`. A
feature commit carries its `SPEC.md` status change and its `log.md` entry. Commit
messages fall under the PII gate.
