# log — append-only journal

New entries at the bottom; never rewrite history. Format `## [YYYY-MM-DD] <event>`.

## [2026-10-23] Harness set up

Right-sized from two harnesses: context-pages (served-tree rules, PII gate, inbox-is-not-
approval, deterministic `verify.py` gate with `--live`, STATE + log portability) and
second-brain (resume contract with an act-on-top-item rule, contract-first requirements
with verification methods, no-fabricated-data rule, builder never grades itself, ≤4-line
chat replies, delegation tiers). Left out as oversized for a small dashboard: the
seven-phase iteration loop, rubrics and composite scores, graph.json/monitor, benchmarks.
Add them back only if the dashboard grows to need them.

Decisions (owner): repo private, despite Pages-on-private needing a paid plan; noindex
for now. Deploy via a GitHub Actions workflow that publishes `site/` only, so root
harness files are never served. `robots.txt` omitted: a project site under
`/resilafrica/` cannot have its robots.txt honored, so the per-page meta is the mechanism.

## [2026-10-23] Repo created; Pages blocked by plan

`gh repo create jramirezv/resilafrica --private`. Enabling Pages (`POST /pages`,
build_type=workflow) returned HTTP 422: the account's plan does not support Pages on a
private repo. Pushed anyway; CI run 39996347697 shows `gate` green on GitHub's runner
(Python 3.9) and `deploy` failing 404 (Pages not enabled). Open gate for the owner: GitHub
Pro or a public repo.

## [2026-10-23] Repo public; Pages live; H1 done

The owner: "I want you to make jramirezv/resilafrica public, enable Pages, redeploy and run
verify.py --live." Visibility → public; `POST /pages` build_type=workflow (accepted);
workflow_dispatch run 39996644145: gate 15s + deploy 10s, green. `verify.py --live`
13/13: live index 200, byte-identical to `site/index.html`, noindex meta present.
Consequence: the whole repo is now public, not just `site/`. CLAUDE.md and README still
describe it as private; flagged to the owner rather than edited (modification needs their
explicit approval).

## [2026-10-23] PII gate extended to the whole repo; history rewritten

The owner: "I want you to update CLAUDE.md and README.md to reflect that the repo is
public, extending the PII gate to the whole repo." Done: CLAUDE.md rules 1–2 now cover
every tracked file, commit messages and history; README updated. `verify.py` scans every
`git ls-files` entry for emails and phones (new check `git-tracked-files`); gitignored
`raw/` stays out of scope. Owner decisions: tracked files refer to "the owner", never a
name (SPEC, STATE, log and verify.py comments redacted once, including earlier log
entries); commits move to a repo-local GitHub noreply identity, and the three existing
commits are rewritten to it (`git filter-branch --env-filter`, dates preserved) and
force-pushed. Known residue: earlier file versions in the rewritten commits still contain
the owner's first name, since the rewrite changes identities, not file contents.

## [2026-10-23] History squashed to one commit

The owner: "I want you to squash the resilafrica history into a single clean commit and
force-push main." The rewritten history still carried the owner's first name in earlier
file versions. `main` replaced by one root commit holding the current tree (noreply
identity), force-pushed. Superseded commits may remain reachable on GitHub by exact SHA
until GitHub garbage-collects them; a purge before then needs a GitHub Support request.
