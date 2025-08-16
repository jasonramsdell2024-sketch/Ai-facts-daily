# scripts/generate_post.py — builds /docs and posts a daily AI fact with affiliate link
# No keys, no external APIs. Pure local generation + GitHub Actions scheduler.

import os, json, random, datetime, html, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
POSTS_DIR = DOCS / "posts"
DATA = ROOT / "data"
STATE = DATA / "state.json"
FACTS = DATA / "facts.txt"

# ---- Customize monetization here if needed ----
AMAZON_TAG = "aitoolsvault-20"  # Jason's tag
AFFILIATE_URL = f"https://www.amazon.com/s?k=artificial+intelligence+books&tag={AMAZON_TAG}"
DISCLOSURE = "Disclosure: As an Amazon Associate I earn from qualifying purchases."

SITE_TITLE = "AI Facts Daily"
SITE_DESC  = "One short AI fact every day. Simple, snackable, and useful."

CSS = """
:root { --bg:#0b0c10; --card:#121418; --text:#e6e8eb; --muted:#9aa3ab; --link:#7dd3fc; --accent:#4ade80; }
*{box-sizing:border-box} body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Inter,Arial,sans-serif;background:var(--bg);color:var(--text);line-height:1.6}
a{color:var(--link);text-decoration:none} a:hover{text-decoration:underline}
.wrap{max-width:860px;margin:0 auto;padding:24px}
.nav{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}
.brand{font-weight:700;font-size:20px}
.card{background:var(--card);border-radius:16px;padding:20px;margin:12px 0;box-shadow:0 10px 20px rgba(0,0,0,.25)}
.meta{color:var(--muted);font-size:14px;margin-bottom:8px}
.title{font-size:22px;margin:0 0 10px 0}
.btn{display:inline-block;background:var(--accent);color:#0b0c10;padding:10px 14px;border-radius:999px;font-weight:700}
.footer{color:var(--muted);font-size:13px;margin-top:30px}
ul.posts{list-style:none;padding:0;margin:0} ul.posts li{margin:10px 0}
hr{border:none;border-top:1px solid #223}
"""

def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"last_index": -1}

def save_state(st):
    STATE.write_text(json.dumps(st, indent=2))

def load_facts():
    lines = [ln.strip() for ln in FACTS.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return lines

def ensure_dirs():
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

def today_slug():
    return datetime.date.today().isoformat()

def build_post_html(date_str, title, fact):
    fact_html = html.escape(fact)
    title_html = html.escape(title)
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title_html} — {SITE_TITLE}</title>
<meta name="description" content="{html.escape(SITE_DESC)}">
<style>{CSS}</style></head>
<body>
<div class="wrap">
  <div class="nav"><div class="brand">{SITE_TITLE}</div><a class="btn" href="../index.html">Home</a></div>
  <article class="card">
    <div class="meta">{date_str}</div>
    <h1 class="title">{title_html}</h1>
    <p>{fact_html}</p>
    <p><a class="btn" href="{AFFILIATE_URL}" rel="sponsored nofollow noopener" target="_blank">Recommended AI Books</a></p>
    <p class="meta">{html.escape(DISCLOSURE)}</p>
  </article>
  <div class="footer">© {datetime.date.today().year} {SITE_TITLE}</div>
</div>
</body></html>"""

def build_index(posts):
    # posts: list of (date_str, filename, title)
    items = "\n".join(
        f'<li><a href="posts/{fn}">{html.escape(date)} — {html.escape(title)}</a></li>'
        for (date, fn, title) in posts
    )
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{SITE_TITLE}</title>
<meta name="description" content="{html.escape(SITE_DESC)}">
<style>{CSS}</style></head>
<body>
<div class="wrap">
  <div class="nav"><div class="brand">{SITE_TITLE}</div><a class="btn" href="{AFFILIATE_URL}" rel="sponsored nofollow noopener" target="_blank">AI Books</a></div>
  <div class="card">
    <h1 class="title">Latest Posts</h1>
    <ul class="posts">{items}</ul>
  </div>
  <div class="card">
    <h2 class="title">What is this?</h2>
    <p>{html.escape(SITE_DESC)}</p>
  </div>
  <div class="footer">© {datetime.date.today().year} {SITE_TITLE} • {html.escape(DISCLOSURE)}</div>
</div>
</body></html>"""

def main():
    ensure_dirs()
    facts = load_facts()
    if not facts:
        raise SystemExit("facts.txt is empty")

    st = load_state()
    idx = (st["last_index"] + 1) % len(facts)
    st["last_index"] = idx
    save_state(st)

    date_str = today_slug()
    title = f"AI Fact #{idx+1}"
    filename = f"{date_str}.html"

    post_html = build_post_html(date_str, title, facts[idx])
    (POSTS_DIR / filename).write_text(post_html, encoding="utf-8")

    # Build index from all posts (sorted desc)
    all_posts = []
    for fn in sorted(os.listdir(POSTS_DIR), reverse=True):
        if fn.endswith(".html"):
            date = fn.replace(".html","")
            # title is predictable; could parse file but we keep it simple
            num = "?"  # not essential
            all_posts.append((date, fn, f"AI Fact ({date})"))

    index_html = build_index(all_posts)
    (DOCS / "index.html").write_text(index_html, encoding="utf-8")

if __name__ == "__main__":
    main()
