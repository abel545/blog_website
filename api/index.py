from flask import Flask, render_template, abort
import os
import re
from datetime import datetime

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)

POSTS_DIR = os.path.join(os.path.dirname(__file__), "../posts")

def parse_post(filename):
    filepath = os.path.join(POSTS_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 간단한 프론트매터 파싱 (--- 로 구분)
    meta = {"title": filename, "date": "", "summary": ""}
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    meta[key.strip()] = val.strip()
            body = parts[2].strip()

    # 간단한 마크다운 → HTML 변환
    body = re.sub(r"^### (.+)$", r"<h3>\1</h3>", body, flags=re.MULTILINE)
    body = re.sub(r"^## (.+)$", r"<h2>\1</h2>", body, flags=re.MULTILINE)
    body = re.sub(r"^# (.+)$", r"<h1>\1</h1>", body, flags=re.MULTILINE)
    body = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", body)
    body = re.sub(r"\*(.+?)\*", r"<em>\1</em>", body)
    body = re.sub(r"`(.+?)`", r"<code>\1</code>", body)
    body = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', body)
    # 빈 줄을 <p> 태그로
    paragraphs = re.split(r"\n\n+", body)
    body = "".join(
        p if p.strip().startswith("<") else f"<p>{p.strip()}</p>"
        for p in paragraphs if p.strip()
    )

    slug = filename.replace(".md", "")
    return {"slug": slug, "body": body, **meta}

def get_all_posts():
    if not os.path.exists(POSTS_DIR):
        return []
    files = sorted(
        [f for f in os.listdir(POSTS_DIR) if f.endswith(".md")],
        reverse=True
    )
    return [parse_post(f) for f in files]

@app.route("/")
def index():
    posts = get_all_posts()
    return render_template("index.html", posts=posts)

@app.route("/post/<slug>")
def post(slug):
    filename = f"{slug}.md"
    filepath = os.path.join(POSTS_DIR, filename)
    if not os.path.exists(filepath):
        abort(404)
    post_data = parse_post(filename)
    return render_template("post.html", post=post_data)

@app.route("/about")
def about():
    return render_template("about.html")

@app.errorhandler(404)
def not_found(e):
    return render_template("base.html", content="<h2>404 - 페이지를 찾을 수 없습니다</h2>"), 404
