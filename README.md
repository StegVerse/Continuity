# StegVerse Continuity (Guardian Mode)

This repository keeps StegVerse alive if the maintainer is unavailable.  
It checks health, self-heals via redeploy hooks, logs status, and raises a safe public signal without transferring custody or funds.

[![Status](https://img.shields.io/badge/Mode-Guardian-green)](#)
[![License](https://img.shields.io/badge/License-StegVerse_Guardian-v1.0-blue)](LICENSE.md)

---

## ✨ What it does
- **Health checks:** UI diag page and API `/whoami`
- **Self-heal:** Triggers Render/Netlify/Vercel redeploys if unhealthy
- **Daily logs:** Writes `docs/status/YYYY-MM-DD.md`
- **Dead-man signal:** Raises attention via GitHub Issue if no trusted human ACK
- **Guardrails:** No custody or funds move without the Trusted Phrase

---

## 🔐 Secrets Handling (Vault-first)
This repository retrieves deploy hooks **on demand** from **StegTV (Token Vault)** using GitHub **OIDC** (no long-lived secrets in GitHub).  
If Vault is temporarily unavailable, it falls back to (optional) GitHub encrypted secrets.

### Configure Token Vault Trust
In StegTV, create a trust rule:
- **Issuer:** `https://token.actions.githubusercontent.com`
- **Subject:** `repo:StegVerse/Continuity:ref:refs/heads/main` (adjust as needed)
- **Audience:** `stegtv`
- **Scopes:** `secrets:get`
- **TTL:** 10–30 minutes per token

Expose an endpoint (example): `POST /v1/oidc/exchange` → `{ "access_token": "<short-lived>" }`

### GitHub → Actions → Variables (non-secret)
- `TV_BASE` — e.g., `https://stegtv.example.com`
- `TV_AUDIENCE` — e.g., `stegtv`
- `TV_SECRET_IDS_JSON` — JSON mapping:
  ```json
  {"render":"deploy/render-hook","netlify":"deploy/netlify-hook","vercel":"deploy/vercel-hook"}

### Name-Resolution Tolerance
Before declaring a repo “down,” StegContinuity attempts alternate name conventions:

- **Org case:** `StegVerse` = `Stegverse` = `stegverse`
- **Repo transformations:** hyphen vs camel (`StegVerse-Talk` ↔ `StegVerseTalk`), “StegVerse-” prefix, module name vs repo name (`StegTalk` ↔ `talk`, `StegVerse-SCW` ↔ `stegverse-scw`)
- **Alias map:** see `config/repo_aliases.json`

Only after all permutations fail will it classify a repo as unresolved.
