import os, json, datetime, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
POSTS_DIR = DOCS / "posts"
DATA = ROOT / "data"
STATE = DATA / "state.json"
FACTS = DATA / "facts.txt"

AMAZON_TAG = "aitoolsvault-20"
AFFILIATE_URL = f"https://www.amazon.com/s?k=artificial+intelligence+books&tag={AMAZON_TAG}"
DISCLOSURE = "Disclosure: As an Amazon Associate I earn from qualifying purchases."

SITE_TITLE = "AI Facts Daily"
SITE_DESC  = "One short AI fact every day."

CSS = "body{font-family:sans-serif;max-width:700px;margin:40px auto;padding:0 10px;} .card{background:#f4f4f4;padding:20px;border-radius:12px;margin-bottom:20px;} a{color:#0077cc;}"

def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"last_index": -1}

def save_state(st):
    STATE.write_text(json.dumps(st))

def load_facts():
    return [ln.strip() for ln in FACTS.read_text().splitlines() if ln.strip()]

def ensure_dirs():
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

def today_slug():
    return datetime.date.today().isoformat()

def build_post_html(date_str, title, fact):
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>{title} — {SITE_TITLE}</title><style>{CSS}</style></head><body>
<div class="card"><h1>{title}</h1><p>{fact}</p>
<p><a href="{AFFILIATE_URL}" target="_blank">Recommended AI Books</a></p>
<p><small>{DISCLOSURE}</small></p></div></body></html>"""

def build_index(posts):
    items = "".join([f"<li><a href='posts/{fn}'>{date} — {title}</a></li>" for date, fn, title in posts])
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>{SITE_TITLE}</title><style>{CSS}</style></head><body>
<h1>{SITE_TITLE}</h1><p>{SITE_DESC}</p><ul>{items}</ul><p><small>{DISCLOSURE}</small></p></body></html>"""

def main():
    ensure_dirs()
    facts = load_facts()
    st = load_state()
    idx = (st["last_index"] + 1) % len(facts)
    st["last_index"] = idx
    save_state(st)

    date_str = today_slug()
    title = f"AI Fact #{idx+1}"
    filename = f"{date_str}.html"
    (POSTS_DIR / filename).write_text(build_post_html(date_str, title, facts[idx]), encoding="utf-8")

    all_posts = []
    for fn in sorted(os.listdir(POSTS_DIR), reverse=True):
        if fn.endswith(".html"):
            date = fn.replace(".html","")
            all_posts.append((date, fn, f"AI Fact {date}"))
    (DOCS / "index.html").write_text(build_index(all_posts), encoding="utf-8")

if __name__ == "__main__":
    main()
