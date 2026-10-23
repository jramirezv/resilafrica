# resilafrica

Small static dashboard, published with GitHub Pages at
`https://jramirezv.github.io/resilafrica/` (noindexed). The repo is public: every tracked
file and all history fall under the PII gate, not only the served site.

## Layout

| Path | What |
|---|---|
| `site/` | The served tree: `index.html`, `assets/`, `vendor/` (pinned libraries), `data/` |
| `site/data/manifest.json` | Provenance register: one entry per data file (source, retrieval date) |
| `tools/verify.py` | The gate: deterministic checks on `site/` and all tracked files; `--live` checks the deployed site |
| `raw/` | Gitignored inbox for source files. Being in `raw/` is not approval to publish |
| `SPEC.md` | Requirements as given, each with a verification method and status |
| `STATE.md` | Resume contract: where things stand, next actions, open gates |
| `log.md` | Append-only journal |
| `.github/workflows/pages.yml` | CI: gate, then deploy `site/` to Pages on push to `main` |

## Commands

```bash
/usr/bin/python3 tools/verify.py          # gate (local)
/usr/bin/python3 tools/verify.py --live   # gate + deployed-site checks
/usr/bin/python3 -m http.server 8765 -d site   # local preview
```

## What the gate checks

- every HTML page has a `<title>` and the noindex meta
- every relative `src`/`href` resolves to a file inside `site/`
- no resource is loaded from a host outside `ALLOWED_HOSTS` (empty by default; vendor instead)
- every file in `site/data/` is registered in `manifest.json` with the required fields, and
  every entry points to a file that exists; JSON files parse
- no email addresses or phone-shaped strings in any tracked file (`git ls-files`) or in `site/`
- no file over 25 MB
- `--live`: the deployed `index.html` matches the local one byte for byte
