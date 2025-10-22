# ──────────────────────────────────────────────────────────────
#  Licensed under the StegVerse Guardian License v1.0 (2025)
#  © 2025 Rigel Randolph and the StegVerse Project
#  Purpose: To maintain StegVerse continuity, stability, and ethics.
#  See LICENSE.md for details.
# ──────────────────────────────────────────────────────────────
import os, json, datetime, subprocess
from urllib.request import Request, urlopen

ROOT = os.path.dirname(os.path.dirname(__file__))
STATUS_DIR = os.path.join(ROOT, "docs", "status")
CONFIG_DIR = os.path.join(ROOT, "config")
os.makedirs(STATUS_DIR, exist_ok=True)

def http_get(url, timeout=20, headers=None):
    req = Request(url, headers=headers or {"User-Agent":"guardian-bot"})
    try:
        with urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return None, str(e)

def http_post(url, timeout=20, headers=None, data=None):
    payload = None
    if data is not None:
        if isinstance(data,(bytes,bytearray)):
            payload = data
        else:
            payload = json.dumps(data).encode("utf-8")
    hdrs = {"User-Agent":"guardian-bot","Content-Type":"application/json"}
    if headers: hdrs.update(headers)
    try:
        req = Request(url, data=payload, headers=hdrs, method="POST")
        with urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return None, str(e)

class RepoNameResolver:
    def __init__(self, org_hint="StegVerse"):
        self.org_hint = org_hint
        self.aliases = {
            "org": {"canonical": org_hint, "alternates": [org_hint.lower(), org_hint.title()]},
            "repos": {},
            "rules": {"try_cases": ["as_is","lower","title"], "try_prefixes":["","StegVerse-"], "try_hyphens":["-",""]}
        }
        p = os.path.join(CONFIG_DIR, "repo_aliases.json")
        if os.path.exists(p):
            try:
                self.aliases = json.load(open(p,"r"))
            except Exception:
                pass

    def _case_variants(self, s):
        yield s; yield s.lower(); yield s.title()

    def _hyphen_variants(self, s):
        yield s
        if "-" in s:
            yield s.replace("-", "")
        else:
            out=[]; 
            for ch in s:
                if ch.isupper() and out: out.append("-")
                out.append(ch)
            hy="".join(out)
            if hy!=s: yield hy

    def _prefix_variants(self, s):
        for pref in self.aliases["rules"].get("try_prefixes",["","StegVerse-"]):
            yield f"{pref}{s}"

    def candidates(self, repo_hint):
        alt_map = self.aliases.get("repos", {})
        base_list = [repo_hint]
        key = repo_hint.lower()
        for k, v in alt_map.items():
            if key == k or repo_hint in ([k]+v):
                base_list = [k] + v + [repo_hint]
                break
        seen=set()
        for base in base_list:
            for c in self._case_variants(base):
                for h in self._hyphen_variants(c):
                    for p in self._prefix_variants(h):
                        if p not in seen:
                            seen.add(p); yield p

    def org_candidates(self):
        o = self.aliases.get("org",{})
        all_orgs = [o.get("canonical","StegVerse")] + o.get("alternates",[])
        seen=set()
        for org in all_orgs:
            for v in self._case_variants(org):
                if v not in seen:
                    seen.add(v); yield v

    def url_exists(self, url):
        code, _ = http_get(url, timeout=8)
        return bool(code and 200 <= code < 400)

    def resolve(self, repo_hint):
        for org in self.org_candidates():
            for r in self.candidates(repo_hint):
                u = f"https://github.com/{org}/{r}"
                if self.url_exists(u):
                    return {"org": org, "repo": r, "url": u}
        return None

def write_status(lines):
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    with open(os.path.join(STATUS_DIR, f"{today}.md"),"w",encoding="utf-8") as f:
        f.write(f"# Guardian Status — {today} UTC\n\n```\n" + "\n".join(lines) + "\n```\n")

def main():
    lines=[]
    API_BASE=(os.getenv("API_BASE") or "").rstrip("/")
    UI_HEALTH=os.getenv("UI_HEALTH","")
    ADMIN_BOOTSTRAP_ROUTE=os.getenv("ADMIN_BOOTSTRAP_ROUTE","/v1/ops/config/bootstrap")

    resolver=RepoNameResolver(org_hint=os.getenv("ORG_GITHUB","StegVerse"))
    for key in ["continuity","talk","tv","stegverse-scw","site"]:
        hit=resolver.resolve(key)
        lines.append(f"RepoResolve[{key}]: {('FOUND ' + hit['org'] + '/' + hit['repo']) if hit else 'not found'}")

    ui_code, ui_body = http_get(UI_HEALTH) if UI_HEALTH else (None,"no UI_HEALTH")
    ui_ok = bool(ui_code and 200 <= ui_code < 400 and ("OK" in (ui_body or "").upper() or "healthy" in (ui_body or "").lower()))
    lines.append(f"UI: {UI_HEALTH} code={ui_code} ok={ui_ok}")

    api_code, api_body = http_get(API_BASE + "/whoami") if API_BASE else (None,"no API_BASE")
    api_ok = bool(api_code and 200 <= api_code < 400)
    lines.append(f"API: {API_BASE}/whoami code={api_code} ok={api_ok}")

    if API_BASE and not api_ok:
        boot_url = API_BASE + ADMIN_BOOTSTRAP_ROUTE
        p_code, p_body = http_post(boot_url, data={"reason":"guardian-autoboot"})
        lines.append(f"ADMIN bootstrap: code={p_code} msg={(p_body or '')[:160]}")
    else:
        lines.append("ADMIN bootstrap: not needed")

    hooks={"render":"","netlify":"","vercel":""}
    tv_file=os.getenv("TV_SECRETS_FILE")
    if tv_file and os.path.exists(tv_file):
        try:
            data=json.load(open(tv_file,"r")); hooks.update({k: data.get(k,"") for k in hooks})
        except Exception: pass
    hooks["render"]=hooks["render"] or os.getenv("RENDER_DEPLOY_HOOK","")
    hooks["netlify"]=hooks["netlify"] or os.getenv("NETLIFY_DEPLOY_HOOK","")
    hooks["vercel"]=hooks["vercel"] or os.getenv("VERCEL_DEPLOY_HOOK","")

    if not ui_ok or not api_ok:
        if hooks["render"]: rc,_=http_post(hooks["render"]); lines.append(f"Render redeploy: code={rc}")
        if hooks["netlify"]: nc,_=http_post(hooks["netlify"]); lines.append(f"Netlify redeploy: code={nc}")
        if hooks["vercel"]: vc,_=http_post(hooks["vercel"]); lines.append(f"Vercel redeploy: code={vc}")

    TRUSTED_PHRASE=os.getenv("TRUSTED_PHRASE","")
    NO_ACK_DAYS=int(os.getenv("GUARDIAN_DAYS_NO_ACK","3"))
    days=9999
    try:
        subprocess.check_call(["gh","--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        out=subprocess.check_output(["gh","issue","list","--limit","100","--state","all","--json","title,updatedAt,number,body"]).decode()
        data=json.loads(out); latest=None
        from datetime import datetime, timezone
        for it in data:
            txt=(it.get("title","") + "\\n" + it.get("body",""))
            if TRUSTED_PHRASE and TRUSTED_PHRASE in txt:
                ts=datetime.fromisoformat(it["updatedAt"].replace("Z","+00:00"))
                d=datetime.now(timezone.utc)-ts
                if latest is None or d.days < latest: latest=d.days
        if latest is not None: days=latest
    except Exception: pass
    triggered=days>=NO_ACK_DAYS
    lines.append(f"Dead-man: days_since_ack={days} threshold={NO_ACK_DAYS} triggered={triggered}")

    write_status(lines)

if __name__ == "__main__":
    main()
