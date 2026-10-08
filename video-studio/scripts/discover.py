"""Scan a project so the video is about what the product really is.

    python discover.py <project-dir> [--out brief]
    python discover.py https://example.com [--out brief]

Writes <out>/discovery.json and prints a readable summary: name and pitch, stack,
features (README sections and bullets), screens/routes/commands, brand colours
(ranked; named brand/primary/accent variables first), fonts, and visual assets
(logos, icons, screenshots). For a URL: title, meta/social-preview tags, headings,
calls to action, colours and fonts from the page and its stylesheets, image URLs.
Secrets (.env, keys, credential files) are never read. It is a starting point: read
the README and the main UI files (or the rendered site) yourself afterwards, then
confirm the product brief with the user. Standard library only.
"""
import sys
import argparse
import collections
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):          # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SKIP = {"node_modules", ".git", ".venv", "venv", "env", "dist", "build", "out", ".next", ".nuxt", "target",
        "__pycache__", ".cache", "coverage", "data", ".idea", ".vscode", "vendor", "Pods", ".turbo", ".expo"}
TEXT = {".md", ".json", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".css", ".scss", ".sass", ".less", ".html",
        ".vue", ".svelte", ".py", ".toml", ".yaml", ".yml", ".dart", ".swift", ".kt", ".go", ".rs", ".astro"}
# Never read: anything on screen may be posted publicly (references/discovery.md section 7).
SECRET = re.compile(r"(^\.env($|\.)|\.(pem|key|p12|pfx|keystore|jks)$|^id_(rsa|ed25519|ecdsa)|service[-_]?account.*\.json$|"
                    r"credential|secret|^\.npmrc$|^\.pypirc$|^\.netrc$|-lock\.(json|yaml)$|\.lock$)", re.I)
IMG = {".png", ".svg", ".jpg", ".jpeg", ".webp", ".gif", ".ico"}
STACK = {
    "react": "React", "next": "Next.js", "vue": "Vue", "nuxt": "Nuxt", "svelte": "Svelte", "@sveltejs/kit": "SvelteKit",
    "electron": "Electron", "@tauri-apps/api": "Tauri", "react-native": "React Native", "expo": "Expo",
    "tailwindcss": "Tailwind", "three": "three.js", "framer-motion": "Framer Motion", "motion": "Motion",
    "express": "Express", "fastify": "Fastify", "astro": "Astro", "remotion": "Remotion",
    "fastapi": "FastAPI", "django": "Django", "flask": "Flask", "streamlit": "Streamlit", "torch": "PyTorch",
}


def walk(root, limit=6000):
    n = 0
    for p in root.rglob("*"):
        if any(part in SKIP or SECRET.search(part) for part in p.relative_to(root).parts):
            continue
        if p.is_file():
            n += 1
            if n > limit:
                return
            yield p


def read(p, cap=400_000):
    try:
        if p.stat().st_size > cap:
            return ""
        return p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def readme_info(root):
    for name in ("README.md", "readme.md", "README.MD", "Readme.md"):
        p = root / name
        if not p.exists():
            continue
        lines, fence = [], False
        for ln in read(p).splitlines():                     # drop fenced code: its "# comments" aren't headings
            if ln.strip().startswith("```"):
                fence = not fence
                continue
            if not fence:
                lines.append(ln)
        txt = "\n".join(lines)
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", txt, re.S)
        title = (re.sub(r"<[^>]+>", "", h1.group(1)).strip() if h1 else
                 next((ln.lstrip("# ").strip() for ln in lines if ln.startswith("# ")), ""))
        clean = lambda b: re.sub(r"[*_`>]|<[^>]+>", "", b).strip()   # noqa: E731
        paras = [clean(b) for b in re.split(r"\n\s*\n", txt)
                 if b.strip() and not b.strip().startswith(("#", "<", "!", "[", "|", "-", "*"))]
        sections = [ln.lstrip("# ").strip() for ln in lines if re.match(r"^#{2,3} ", ln)]
        bullets = [clean(ln.strip()[2:]) for ln in lines if re.match(r"^\s*[-*] \*\*", ln)][:25]
        return {"title": title, "pitch": " ".join(paras[0].split())[:400] if paras else "",
                "sections": sections[:40], "key_bullets": bullets}
    return {}


def style_scan(txt, info, hexes):
    for h in re.findall(r"#(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b", txt):
        hexes[h.lower() if len(h) == 7 else "#" + "".join(c * 2 for c in h[1:]).lower()] += 1
    for m in re.finditer(r"(--[\w-]*(?:brand|primary|accent|secondary|background|foreground|bg|fg)[\w-]*)\s*:\s*([^;]+);", txt):
        info["named_colors"][m.group(1)] = m.group(2).strip()[:60]
    for m in re.finditer(r"""(?:brand|primary|accent|secondary)\w*\s*:\s*["'](#[0-9a-fA-F]{3,8})["']""", txt):
        info["named_colors"].setdefault(m.group(0).split(":")[0].strip(), m.group(1))


def font_scan(txt, info):
    for m in re.finditer(r"""font-family\s*:\s*([^;}{]+)""", txt):
        first = m.group(1).split(",")[0].strip().strip("'\"")
        if first and not first.startswith(("var(", "inherit", "system-ui", "-apple", "sans-serif", "serif", "monospace")):
            info["fonts"].add(first)
    for m in re.finditer(r"fonts\.googleapis\.com/css2?\?family=([^&\"']+)", txt):
        info["fonts"].add(urllib.parse.unquote(m.group(1)).split(":")[0].replace("+", " "))
    for f in re.findall(r"import\s*{([^}]+)}\s*from\s*['\"]next/font/google", txt):
        info["fonts"].update(x.strip().replace("_", " ") for x in f.split(","))


def fetch(url, cap=2_000_000):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (video-studio discover)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read(cap).decode(r.headers.get_content_charset() or "utf-8", errors="ignore")


def page_copy(html):
    """Title, meta/social tags, headings and calls to action of one HTML page."""
    text = lambda frag: " ".join(re.sub(r"<[^>]+>", " ", frag).split())   # noqa: E731
    meta = {}
    for m in re.finditer(r"<meta\b[^>]*>", html, re.I):
        tag = m.group(0)
        k = re.search(r"""(?:name|property)\s*=\s*["']([^"']+)""", tag, re.I)
        v = re.search(r"""content\s*=\s*["']([^"']*)""", tag, re.I)
        if k and v and re.match(r"(description|og:|twitter:|theme-color)", k.group(1), re.I):
            meta[k.group(1).lower()] = v.group(1)[:300]
    title = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    heads = [text(h) for h in re.findall(r"<h[1-3][^>]*>(.*?)</h[1-3]>", html, re.I | re.S)]
    ctas = [text(c) for c in re.findall(r"<(?:button|a)\b[^>]*>(.*?)</(?:button|a)>", html, re.I | re.S)]
    visible = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.I | re.S)
    return {"title": text(title.group(1)) if title else "", "meta": meta, "sections": [h for h in heads if h][:40],
            "ctas": sorted({c for c in ctas if 1 < len(c) < 40})[:30], "body_chars": len(text(visible))}


def site_info(url):
    """A website as the input: what a plain fetch can see (JS-rendered pages need a browser)."""
    html = fetch(url)
    pc = page_copy(html)
    meta = pc["meta"]
    info = {"project": url, "readme": {"title": pc["title"], "pitch": meta.get("description", ""),
            "sections": pc["sections"], "key_bullets": []},
            "meta": meta, "ctas": pc["ctas"], "names": [], "stack": set(),
            "routes": [], "screens": [], "commands": [], "colors": [], "named_colors": {}, "fonts": set(), "images": [],
            "body_chars": pc["body_chars"]}
    hexes = collections.Counter()
    css = [html] + re.findall(r"<style[^>]*>(.*?)</style>", html, re.I | re.S)
    for href in re.findall(r"""<link\b[^>]*rel\s*=\s*["']?stylesheet[^>]*href\s*=\s*["']([^"']+)""", html, re.I)[:6]:
        full = urllib.parse.urljoin(url, href)
        font_scan(full, info)                                    # a Google Fonts link names the families
        if "fonts.googleapis" not in full:
            try:
                css.append(fetch(full))
            except OSError:
                pass
    for t in css:
        style_scan(t, info, hexes)
        font_scan(t, info)
    imgs = re.findall(r"""<img\b[^>]*src\s*=\s*["']([^"']+)""", html, re.I)
    imgs += [v for k, v in meta.items() if k.endswith(":image")]
    imgs += re.findall(r"""<link\b[^>]*rel\s*=\s*["'][^"']*icon[^"']*["'][^>]*href\s*=\s*["']([^"']+)""", html, re.I)
    for src in dict.fromkeys(imgs):
        low = src.lower()
        kind = "logo" if "logo" in low else "icon" if "icon" in low else "screenshot" if any(
            k in low for k in ("hero", "screen", "shot", "og", "preview")) else "image"
        info["images"].append({"path": urllib.parse.urljoin(url, src), "kind": kind, "bytes": 0})
    return info, hexes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--out", default="brief")
    a = ap.parse_args()
    url = a.project if re.match(r"https?://", a.project) else (
        "https://" + a.project if not Path(a.project).exists() and re.match(r"^[\w-]+(\.[\w-]+)+(/|$)", a.project) else None)
    if url:
        info, hexes = site_info(url)
        root = Path(urllib.parse.urlparse(url).netloc)
    else:
        root = Path(a.project).resolve()
        info, hexes = scan_project(root)
    finish(info, hexes, root, Path(a.out))


def scan_project(root):
    info = {"project": str(root), "readme": readme_info(root), "names": [], "stack": set(), "routes": [],
            "screens": [], "commands": [], "colors": [], "named_colors": {}, "fonts": set(), "images": []}
    hexes = collections.Counter()
    for p in walk(root):
        ext = p.suffix.lower()
        rel = str(p.relative_to(root)).replace("\\", "/")
        if ext in IMG:
            if p.stem.isdigit():                             # a rendered frame sequence: list the folder once
                seq = str(p.parent.relative_to(root)).replace("\\", "/")
                if not any(i["path"] == seq for i in info["images"]):
                    info["images"].append({"path": seq, "kind": "sequence", "bytes": 0})
                continue
            low = rel.lower()
            kind = ("logo" if "logo" in low else "icon" if ("icon" in low or "favicon" in low) else
                    "screenshot" if any(k in low for k in ("screenshot", "screen", "shot", "preview", "hero", "docs/img", "og")) else "image")
            if kind != "image" or len(info["images"]) < 60:
                info["images"].append({"path": rel, "kind": kind, "bytes": p.stat().st_size})
            continue
        if ext not in TEXT:
            continue
        txt = read(p)
        if not txt:
            continue
        if p.name == "package.json":
            try:
                pkg = json.loads(txt)
                info["names"].append({"file": rel, "name": pkg.get("name"), "description": pkg.get("description")})
                for dep in {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}:
                    if dep in STACK:
                        info["stack"].add(STACK[dep])
                    if dep.startswith("@fontsource/"):
                        info["fonts"].add(dep.split("/")[1].replace("-", " ").title())
            except json.JSONDecodeError:
                pass
        if p.name in ("pyproject.toml", "requirements.txt", "Cargo.toml", "pubspec.yaml"):
            m = re.search(r'^\s*name\s*[=:]\s*"?([^"\n]+)"?', txt, re.M)
            d = re.search(r'^\s*description\s*[=:]\s*"?([^"\n]+)"?', txt, re.M)
            if m:
                info["names"].append({"file": rel, "name": m.group(1), "description": d.group(1) if d else None})
            for key, label in STACK.items():
                if re.search(rf"^\s*{re.escape(key)}\b", txt, re.M | re.I):
                    info["stack"].add(label)
            if p.name == "pubspec.yaml":
                info["stack"].add("Flutter")
        # screens, routes, commands
        if re.search(r"(Screen|Page|View|Panel|Modal|Dialog)\.(jsx|tsx|vue|svelte|dart|swift|kt)$", p.name):
            info["screens"].append(rel)
        if re.search(r"/(pages|app|routes)/", "/" + rel) and ext in (".jsx", ".tsx", ".vue", ".svelte", ".astro") and not p.name.startswith("_"):
            info["routes"].append(rel)
        for m in re.finditer(r"""(?:path\s*[:=]\s*|<Route[^>]*path=)["'`](/[^"'`]*)["'`]""", txt):
            info["routes"].append(m.group(1))
        for m in re.finditer(r"""add_parser\(\s*["']([\w-]+)["'](?:[^)]*help=["']([^"']+))?""", txt):
            info["commands"].append(f"{m.group(1)}: {m.group(2) or ''}".strip(": "))
        for m in re.finditer(r"""@(?:\w+\.)?command\(\s*(?:["']([\w-]+)["'])?""", txt):
            if m.group(1):
                info["commands"].append(m.group(1))
        if ext in (".css", ".scss", ".sass", ".less", ".html", ".vue", ".svelte", ".astro") or re.search(r"tailwind|theme|color|palette|token", p.name, re.I):
            style_scan(txt, info, hexes)
        font_scan(txt, info)

    index = root / "index.html"                            # a static site: its page copy is the voice of the product
    if index.exists():
        pc = page_copy(read(index))
        info["meta"], info["ctas"] = pc["meta"], pc["ctas"]
        r = info["readme"] = info["readme"] or {"title": pc["title"], "pitch": pc["meta"].get("description", ""),
                                                "sections": [], "key_bullets": []}
        r.setdefault("sections", [])
        info["page_headings"] = pc["sections"]
    return info, hexes


def finish(info, hexes, root, out):
    greys = {"#ffffff", "#000000", "#fff", "#000"}
    info["colors"] = [{"hex": h, "uses": n} for h, n in hexes.most_common(24) if h not in greys][:14]
    info["stack"] = sorted(info["stack"])
    info["fonts"] = sorted(info["fonts"])[:12]
    info["routes"] = sorted(set(info["routes"]))[:60]
    info["screens"] = sorted(set(info["screens"]))[:60]
    info["commands"] = sorted(set(info["commands"]))[:40]
    info["images"].sort(key=lambda i: ("logo", "icon", "screenshot", "sequence", "image").index(i["kind"]))

    out.mkdir(parents=True, exist_ok=True)
    (out / "discovery.json").write_text(json.dumps(info, indent=2), encoding="utf-8")

    r = info["readme"]
    print(f"# Discovery: {r.get('title') or root.name}")
    if r.get("pitch"):
        print(f"\nPitch (README): {r['pitch']}")
    for n in info["names"][:4]:
        print(f"- {n['file']}: {n['name']}" + (f" — {n['description']}" if n.get("description") else ""))
    for k, v in list(info.get("meta", {}).items())[:8]:
        print(f"- meta {k}: {v[:140]}")
    if info.get("page_headings"):
        print(f"index.html headings: {' · '.join(info['page_headings'][:16])}")
    if info.get("ctas"):
        print(f"Calls to action: {' · '.join(info['ctas'][:12])}")
    if info.get("body_chars", 1000) < 400:
        print("! Little text in the raw HTML: the page is probably rendered by JavaScript. Load it in a browser "
              "(dismiss overlays, scroll section by section) before planning.")
    print(f"\nStack: {', '.join(info['stack']) or 'unknown'}")
    if r.get("sections"):
        print(f"README sections: {' · '.join(r['sections'][:20])}")
    if r.get("key_bullets"):
        print("Feature bullets:\n" + "\n".join(f"  - {b[:110]}" for b in r["key_bullets"][:12]))
    for key in ("screens", "routes", "commands"):
        if info[key]:
            print(f"{key.title()} ({len(info[key])}): {', '.join(info[key][:15])}")
    if info["named_colors"]:
        print("Named colours: " + ", ".join(f"{k} {v}" for k, v in list(info["named_colors"].items())[:10]))
    if info["colors"]:
        print("Most-used colours: " + ", ".join(f"{c['hex']}×{c['uses']}" for c in info["colors"][:10]))
    print(f"Fonts: {', '.join(info['fonts']) or 'none declared'}")
    imgs = [i for i in info["images"] if i["kind"] != "image"][:12]
    if imgs:
        print("Visual assets: " + ", ".join(f"{i['path']} ({i['kind']})" for i in imgs))
    print(f"\n-> {out / 'discovery.json'}")


if __name__ == "__main__":
    main()
