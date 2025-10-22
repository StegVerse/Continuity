# ──────────────────────────────────────────────────────────────
#  Licensed under the StegVerse Guardian License v1.0 (2025)
#  © 2025 Rigel Randolph and the StegVerse Project
#  Purpose: To maintain StegVerse continuity, stability, and ethics.
#  See LICENSE.md for details.
# ──────────────────────────────────────────────────────────────
import os, json, datetime, textwrap, subprocess
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT = os.path.dirname(os.path.dirname(__file__))
STATUS_DIR = os.path.join(ROOT, "docs", "status")
os.makedirs(STATUS_DIR, exist_ok=True)

def http_get(url, timeout=20, headers=None):
    try:
        req = Request(url, headers=headers or {"User-Agent":"guardian-bot"})
        with urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return None, str(e)

def http_post(url, timeout=20, headers=None, data=None):
    try:
        payload = None if data is None else (json.dumps(data).encode("utf-8") if not isinstance(data,(bytes,bytearray)) else data)
        hdrs = {"User-Agent":"guardian-bot","Content-Type":"application/json"}
        if headers: hdrs.update(headers)
        req = Request(url, data=payload, headers=hdrs, method="POST")
        with urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", errors="ignore")
    except Exception as e:
        return None, str(e)

def read_tv_hooks():
    path = os.getenv("TV_SECRETS_FILE")
    out = {"render":"","netlify":"","vercel":""}
    if path and os.path.exists(path):
        try:
            data = json.load(open(path,"r"))
            out.update({
                "render": data.get("render",""),
                "netlify": data.get("netlify",""),
                "vercel": data.get("vercel",""),
            })
        except Exception:
            pass
    # Fallbacks
    out["render"] = out["render"] or os.getenv("RENDER_DEPLOY_HOOK","")
    out["netlify"] = out["netlify"] or os.getenv("NETLIFY_DEPLOY_HOOK","")
    out["vercel"]  = out["vercel"]  or os.getenv("VERCEL_DEPLOY_HOOK","")
    return out

def write_status(lines):
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    with open(os.path.join(STATUS_DIR, f"{today}.md"),"w",encoding="utf-8") as f:
        f.write(f"# Guardian Status — {today} UTC\n\n```\n" + "\n".join(lines) + "\n```")

def main():
    lines = []
    API_BASE = (os.getenv("API_BASE") or "").rstrip("/")
    UI_HEALTH = os.getenv("UI_HEALTH","")
    ADMIN_BOOTSTRAP_ROUTE = os.getenv("ADMIN_BOOTSTRAP_ROUTE","/v1/ops/config/bootstrap")

    # Health checks
    ui_code, ui_body = http_get(UI_HEALTH) if UI_HEALTH else (None,"no UI_HEALTH")
    ui_ok = bool(ui_code and 200 <= ui_code < 400 and ("OK" in (ui_body or "").upper() or "healthy" in (ui_body or "").lower()))
    lines.append(f"UI: {UI_HEALTH} code={ui_code} ok={ui_ok}")

    api_code, api_body = http_get(API_BASE + "/whoami") if API_BASE else (None,"no API_BASE")
    api_ok = bool(api_code and 200 <= api_code < 400)
    lines.append(f"API: {API_BASE}/whoami code={api_code} ok={api_ok}")

    # ADMIN bootstrap (idempotent server-side)
    if API_BASE:
        boot_url = API_BASE + ADMIN_BOOTSTRAP_ROUTE
        # Heuristic: try bootstrap if API unhealthy
        if not api_ok:
            p_code, p_body = http_post(boot_url, data={"reason":"guardian-autoboot"})
            lines.append(f"ADMIN bootstrap: code={p_code} msg={(p_body or '')[:160]}")
        else:
            lines.append("ADMIN bootstrap: not needed")

    # Redeploy if needed
    hooks = read_tv_hooks()
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

    # Dead-man switch (simple: based on TRUSTED_PHRASE presence in Issues via gh)
    TRUSTED_PHRASE = os.getenv("TRUSTED_PHRASE","")
    NO_ACK_DAYS = int(os.getenv("GUARDIAN_DAYS_NO_ACK","3"))
    days = 9999
    try:
        subprocess.check_call(["gh","--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        out = subprocess.check_output(["gh","issue","list","--limit","100","--state","all","--json","title,updatedAt,number,body"])
        data = json.loads(out.decode())
        latest = None
        for it in data:
            txt = (it.get("title","") + "\n" + it.get("body",""))
            if TRUSTED_PHRASE and TRUSTED_PHRASE in txt:
                from datetime import datetime, timezone
                ts = datetime.fromisoformat(it["updatedAt"].replace("Z","+00:00"))
                d = datetime.now(timezone.utc) - ts
                latest = d.days if latest is None or d.days < latest else latest
        if latest is not None:
            days = latest
    except Exception:
        pass
    triggered = days >= NO_ACK_DAYS
    lines.append(f"Dead-man: days_since_ack={days} threshold={NO_ACK_DAYS} triggered={triggered}")

    write_status(lines)

if __name__ == "__main__":
    main()
