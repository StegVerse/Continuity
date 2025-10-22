# StegVerse Continuity (Guardian Mode)

Keeps StegVerse alive if the maintainer is unavailable. Health checks, self-heal, daily logs, and safe public signaling.

[![Mode](https://img.shields.io/badge/Mode-Guardian-green)](#)
[![License](https://img.shields.io/badge/License-StegVerse_Guardian-v1.0-blue)](LICENSE.md)

## Secrets Handling
Vault-first via **StegTV** (repo: `StegVerse/tv`) using GitHub **OIDC**. Fallback to GitHub Secrets only if Vault unavailable.

## Name-Resolution Tolerance
Before declaring a repo “down,” StegContinuity tries alternates:
- Org case: `StegVerse` = `Stegverse` = `stegverse`
- Repo transforms: hyphen vs camel (`StegVerse-Talk` ↔ `StegVerseTalk`), `StegVerse-` prefix, module vs repo name (`StegTalk` ↔ `talk`, `StegVerse-SCW` ↔ `stegverse-scw`)
- Alias map: `config/repo_aliases.json`

Set **Actions → Variables**:
- `ORG_GITHUB=StegVerse`
- `TV_BASE=YOUR_STEGTV_URL`
- `TV_AUDIENCE=stegtv`
- `TV_SECRET_IDS_JSON={"render":"deploy/render-hook","netlify":"deploy/netlify-hook","vercel":"deploy/vercel-hook"}`
- `API_BASE=https://scw-api.onrender.com`
- `UI_HEALTH=https://scw-ui.onrender.com/diag.html`
- `ADMIN_BOOTSTRAP_ROUTE=/v1/ops/config/bootstrap`
- `STATUS_COMMIT_AUTHOR=StegVerse Guardian Bot <guardian@stegverse.local>`
- `GUARDIAN_DAYS_NO_ACK=3`
- `PUBLIC_NOTE_ENABLED=false`
- `PUBLIC_NOTE_MD=` _(optional)_

Secrets (fallback only): `TRUSTED_PHRASE`, and optionally the three deploy hooks.
