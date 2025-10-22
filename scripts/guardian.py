# ──────────────────────────────────────────────────────────────
#  Licensed under the StegVerse Guardian License v1.0 (2025)
#  © 2025 Rigel Randolph and the StegVerse Project
#  Purpose: To maintain StegVerse continuity, stability, and ethics.
#  See LICENSE.md for details.
# ──────────────────────────────────────────────────────────────
import os, json, datetime, textwrap, subprocess, itertools
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT = os.path.dirname(os.path.dirname(__file__))
STATUS_DIR = os.path.join(ROOT, "docs", "status")
CONFIG_DIR = os.path.join(ROOT, "config")
os.makedirs(STATUS_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

def http_get(url, timeout=20, headers=None):
    try:
        req = Request(url, headers=headers or {"User-Agent":"guardian-bot"})
        with urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return None, str(e)

def http_head_ok(url, timeout=12):
    # Use GET but only read headers quickly; GitHub will 200/301 for existing repos
    try:
        code, _ = http_get(url, timeout=timeout)
        return bool(code and 200 <= code < 400)
    except Exception:
        return False

def http_post(url, timeout=20, headers=None, data=None):
    try:
        payload = None
        if data is not None:
            if isinstance(data,(bytes,bytearray)):
                payload = data
            else:
                payload = json.dumps(data).encode("utf-8")
        hdrs = {"User-Agent":"guardian-bot","Content-Type":"application/json"}
        if headers: hdrs.update(headers)
        req = Request(url, data=payload, headers=hdrs, method="POST")
        with urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return None, str(e)

# ---------- Repo Name Resolver --------------------------------

class RepoNameResolver:
    def __init__(self, org_hint="StegVerse", aliases_path=None):
        self.org_hint = org_hint
        self.aliases = {
            "org": {"canonical": org_hint, "alternates": [org_hint.lower(), org_hint.title()]},
            "repos": {},
            "rules": {"try_cases": ["as_is","lower","title"], "try_prefixes":["","StegVerse-"], "try_hyphens":["-",""]}
        }
        p = aliases_path or os.path.join(CONFIG_DIR, "repo_aliases.json")
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    merged = json.load(f)
                # merge cautiously
                for k in ("org","repos","rules"):
                    if k in merged: self.aliases[k] = merged[k]
            except Exception:
                pass

    def _case_variants(self, s):
        yield s
        yield s.lower()
        yield s.title()

    def _hyphen_variants(self, s):
        # swap hyphenless and hyphenated between words (e.g., StegVerse-Talk <-> StegVerseTalk)
        yield s
        if "-" in s:
            yield s.replace("-", "")
        else:
            # insert hyphen before capital runs (Simple heuristic)
            out = []
            for ch in s:
                if ch.isupper() and out:
                    out.append("-")
                out.append(ch)
            hyph = "".join(out)
            if hyph != s:
                yield hyph

    def _prefix_variants(self, s):
        for pref in self.aliases["rules"].get("try_prefixes",["","StegVerse-"]):
            yield f"{pref}{s}"

    def candidates(self, repo_hint):
        # 1) Start with explicit alias list if present
        base_list = [repo_hint]
        alt_map = self.aliases.get("repos", {})
        base_key = repo_hint.lower()
        for k,v in alt_map.items():
            if base_key == k or repo_hint in ([k]+v):
                base_list = [k] + v + [repo_hint]
                break

        # 2) Build permutations within constraints (bounded)
        seen = set()
        for base in base_list:
            for c in self._case_variants(base):
                for h in self._hyphen_variants(c):
                    for p in self._prefix_variants(h):
                        key = p
                        if key not in seen:
                            seen.add(key)
                            yield key

    def org_candidates(self):
        o = self.aliases.get("org",{})
        all_orgs = [o.get("canonical","StegVerse")] + o.get("alternates",[])
        # normalize duplicates
        seen = set()
        for org in all_orgs:
            for v in self._case_variants(org):
                if v not in seen:
                    seen.add(v)
                    yield v

    def resolve(self, repo_hint):
        """
        Try combinations of {org_variant}/{repo_variant} on github.com
        Return first URL that exists, else None.
        """
        for org in self.org_candidates():
            for r in self.candidates(repo_hint):
                url = f"https://github.com/{org}/{r}"
                if http_head_ok(url, timeout=8):
                    return {"org": org, "repo": r, "url": url}
        return None

# ---------- Guardian Core -------------------------------------

def write_status(lines):
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    with open(os.path.join(STATUS_DIR, f"{today}.md"),"w",encoding="utf-8") as f:
        f.write(f"# Guardian Status — {today} UTC\n\n```\n" + "\n".join(lines) + "\n```")

def main():
    lines = []
    API_BASE = (os.getenv("API_BASE") or "").rstrip("/")
    UI_HEALTH = os.getenv("UI_HEALTH","")
    ADMIN_BOOTSTRAP_ROUTE = os.getenv("ADMIN_BOOTSTRAP_ROUTE","/v1/ops/config/bootstrap")

    # Repo resolver (used for cross-repo coordination/log links)
    resolver = RepoNameResolver(org_hint=os.getenv("GITHUB_ORG","StegVerse"))
    for key in ["continuity","talk","tv","stegverse-scw"]:
        hit = resolver.resolve(key)
        lines.append(f"RepoResolve[{key}]: {'FOUND ' + hit['org'] + '/' + hit['repo'] if hit else 'not found'}")

    # Health checks
    ui_code, ui_body = http_get(UI_HEALTH) if UI_HEALTH else (None,"no UI_HEALTH")
    ui_ok = bool(ui_code and 200 <= ui_code < 400 and ("OK" in (ui_body or "").upper() or "healthy" in (ui_body or "").lower()))
    lines.append(f"UI: {UI_HEALTH} code={ui_code} ok={ui_ok}")

    api_code, api_body = http_get(API_BASE + "/whoami") if API_BASE else (None,"no API_BASE")
    api_ok = bool(api_code and 200 <= api_code < 400)
    lines.append(f"API: {API_BASE}/whoami code={api_code} ok={api_ok}")

    # ADMIN bootstrap (idempotent server-side)
    if API_BASE and not api_ok:
        boot_url = API_BASE + ADMIN_BOOTSTRAP_ROUTE
        p_code, p_body = http_post(boot_url, data={"reason":"guardian-autoboot"})
        lines.append(f"ADMIN bootstrap: code={p_code} msg={(p_body or '')[:160]}")
    else:
        lines.append("ADMIN bootstrap: not needed")

    # Redeploy if needed (Vault-first handled in existing version; keep as-is)
    def load_hooks():
        out = {"render":"","netlify":"","vercel":""}
        tv_file = os.getenv("TV_SECRETS_FILE")
        if tv_file and os.path.exists(tv_file):
            try:
                data = json.load(open(tv_file,"r"))
                out.update({k: data.get(k,"") for k in out})
            except Exception:
                pass
        # Fallbacks
        out["render"] = out["render"] or os.getenv("RENDER_DEPLOY_HOOK","")
        out["netlify"] = out["netlify"] or os.getenv("NETLIFY_DEPLOY_HOOK","")
        out["vercel"]  = out["vercel"]  or os.getenv("VERCEL_DEPLOY_HOOK","")
        return out

    hooks = load_hooks()
    if not ui_ok or not api_ok:
        if hooks["render"]:
            rc, _ = http_post(hooks["render"])
            lines.append(f"Render redeploy: code={rc}")
        if hooks["netlify"]:
            nc, _ = http_post(hooks["netlify"])
            lines.append(f"Netlify redeploy: code={nc}")
        if hooks["vercel"]:
            vc, _ = http_post(hooks["vercel"])
            lines.append(f"Vercel redeploy: code={vc}")

    # Dead-man switch (unchanged summary version)
    TRUSTED_PHRASE = os.getenv("TRUSTED_PHRASE","")
    NO_ACK_DAYS = int(os.getenv("GUARDIAN_DAYS_NO_ACK","3"))
    days = 9999
    try:
        subprocess.check_call(["gh","--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        out = subprocess.check_output(["gh","issue","list","--limit","100","--state","all","--json","title,updatedAt,number,body"])
        data = json.loads(out.decode())
        latest = None
        from datetime import datetime, timezone
        for it in data:
            txt = (it.get("title","") + "\n" + it.get("body",""))
            if TRUSTED_PHRASE and TRUSTED_PHRASE in txt:
                ts = datetime.fromisoformat(it["updatedAt"].replace("Z","+00:00"))
                d = datetime.now(timezone.utc) - ts
                if latest is None or d.days < latest:
                    latest = d.days
        if latest is not None:
            days = latest
    except Exception:
        pass
    triggered = days >= NO_ACK_DAYS
    lines.append(f"Dead-man: days_since_ack={days} threshold={NO_ACK_DAYS} triggered={triggered}")

    write_status(lines)

if __name__ == "__main__":
    main()
