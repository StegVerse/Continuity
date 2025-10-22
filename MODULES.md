# StegVerse Modules & Integration Matrix

This document outlines the current and planned modules of the StegVerse ecosystem, their canonical naming conventions, and continuity/vault integration status.

_Last updated: 2025-10-22_

| Canonical Name | Repo Path | Primary Function | Continuity Integration | Vault (StegTV) | AI Entities / Roles | Notes |
|----------------|------------|------------------|------------------------|----------------|---------------------|-------|
| **StegContinuity** | `StegVerse/continuity` | Guardian mode for autonomous self-healing, monitoring, and safe handoff | ✅ Active (v5 Guardian) | ✅ Reads hooks from StegTV | `guardian`, `watchdog` | Central coordinator for all modules |
| **StegTV** | `StegVerse/tv` | Token Vault — secure secret & credential management | ✅ Trusted via OIDC | ✅ Root of trust | `vault-keeper`, `issuer` | Issues short-lived tokens to Actions & services |
| **StegSCW** | `StegVerse/stegverse-SCW` | Core FastAPI backend / sandbox code writer | ✅ Monitored | ✅ Fetches secrets from StegTV | `engine`, `api-guardian` | SCW runs diagnostics, builds sandbox code |
| **StegSite** | `StegVerse/site` | Front-facing informational portal (Cloudflare) | ✅ Auto-redeploy via hooks | — | `messenger`, `publisher` | Outward presence for public & partners |
| **StegTalk** | `StegVerse/stegtalk` _(planned)_ | Encrypted peer-to-peer messaging | ⚙️ Pending Guardian onboarding | ✅ Planned (key exchange) | `relay`, `privacy-node` | Central to user comms & sovereign messaging |
| **StegWallet** | `StegVerse/wallet` _(planned)_ | Income flow & token distribution | ⚙️ Pending | ✅ Planned (Vault custody) | `economist`, `ledger` | Will integrate with ETH wallet 0xa9CE…cdEB |
| **StegHealer** | `StegVerse/healer` | Repo-wide repair agent | ✅ Passive observer | ✅ Pulls update keys | `healer`, `observer` | Performs macro/micro repairs across modules |
| **HybridCollabBridge** | `StegVerse/hybrid-collab-bridge` | Cross-AI collaboration layer (Claude ↔ StegVerse) | ⚙️ Partial | ✅ Required | `bridge`, `translator` | Connects StegAI with external models |
| **FREE-DOM** | `StegVerse/FREE-DOM` | Factual reconstruction project | ⚙️ Optional continuity link | — | `archivist` | Open factual archive; non-operational module |

---

## 🔗 Naming & Discovery Rules
StegContinuity automatically recognizes alternate repo naming patterns:
- **Case-insensitive:** `StegVerse`, `Stegverse`, `stegverse`
- **Hyphen/camel-swap:** `StegVerse-Talk` ↔ `StegVerseTalk`
- **Prefix optional:** `StegTalk` ↔ `Talk`, `StegVerse-SCW` ↔ `stegverse-scw`
- **Alias registry:** `config/repo_aliases.json`

---

## 🚀 Guardian Coordination Roadmap (2025-2026)
| Phase | Objective | Description |
|-------|------------|-------------|
| **I. Stabilization** | Complete integration of StegTV ↔ StegContinuity | OIDC trust + short-lived secret exchange |
| **II. Self-Healing Web** | StegHealer monitors & patches all active modules | Autonomous PR generation + patch rotation |
| **III. AI Workforce** | Deploy autonomous dev AIs per module | PolySan AI & AI Collab Bridge manage coding tasks |
| **IV. Sovereign Apps** | Launch user-facing modules (StegTalk, Wallet, Learn) | Federated onboarding + decentralized identity |
| **V. Guardian Epoch 2** | Expand continuity logic to human & AI succession | Legal + technical inheritance framework |

---

## 🧭 Governance
All modules are bound by the **StegVerse Guardian License (v1.0)**  
Custody, decision-making, and data control remain under Rigel Randolph or verified successor with the **Trusted Phrase**.

---

## 🧩 Future Additions
| Planned Name | Purpose | Guardian Status |
|---------------|----------|-----------------|
| **StegLearn** | Education and knowledge sharing | Planned |
| **StegBusiness** | Legal, licensing, and partnership frameworks | Planned |
| **StegAppStore** | Decentralized distribution of Steg-based apps | Planned |
| **StegAppDev** | Developer SDKs & plug-in builders | Planned |

---

_This document evolves as the Guardian system expands. Updates auto-commit through continuity pipeline._
