"""
storyboard.py — Step 4.5 (audit): one composed PNG still per scene, so you
can eyeball every scene BEFORE paying for a full animation render.

How: `manim -s` renders only the LAST frame (animations are computed but
never rasterized — seconds per scene, not minutes), with TMOT_STORYBOARD=1
so TMOTScene.tear_down() keeps content on stage and shows the `question:`
statically (without the flag the recede leaves an empty last frame — L-9).

Usage (inside the tmot conda env; scenes must be generated first, step 4):
    python pipeline/storyboard.py build/attention                # 16:9 stills
    python pipeline/storyboard.py build/attention --ig           # 9:16 stills
    python pipeline/storyboard.py build/attention --only=softmax_row,hook

Output: build/<name>/storyboard/<NN>_<id>.png  +  index.html — a contact
sheet with type/duration/reel/question/narration per scene: the audit view
(read THIS instead of the .md). Or via main.py:
    python main.py content/<name>/<name>.md --storyboard

Note: a still shows the scene's final COMPOSED state — layout, LaTeX,
colors, overflow — not motion quality. If ids change, `rm -rf
build/<name>/storyboard` first (same reasoning as L-6).
"""
import html
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def scene_class_name(py_file: Path) -> str:
    for line in py_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("class "):
            return line.split("class ")[1].split("(")[0]
    raise ValueError(f"no class in {py_file}")


def newest_png(media: Path, cls: str):
    hits = list(media.rglob(f"{cls}*.png"))
    return max(hits, key=lambda p: p.stat().st_mtime) if hits else None


def render_stills(build_dir: Path, project: dict, fmt: str, only: set):
    scenes_dir = build_dir / "scenes"
    if not scenes_dir.exists():
        sys.exit(f"no generated scenes in {scenes_dir} — run steps 3–4 first "
                 f"(python main.py content/<name>/<name>.md --no-render)")
    out_dir = build_dir / "storyboard"
    media = out_dir / "_media"
    out_dir.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "TMOT_FORMAT": fmt, "TMOT_STORYBOARD": "1"}
    made, skipped = [], 0
    # iterate scenes.json, NOT scenes/*.py — the dir may hold stale files
    # from earlier annotate iterations (L-6), which must not be audited
    for s in project["scenes"]:
        sid = s["id"]
        py = scenes_dir / f"{s['order']:02d}_{sid}.py"
        if not py.exists():
            sys.exit(f"missing generated file {py.name} — re-run step 4 "
                     f"(and if ids changed, rm -rf {build_dir} first, L-6)")
        if only and sid not in only:
            skipped += 1
            continue
        cls = scene_class_name(py)
        cmd = ["manim", "-s", "-qh", "--media_dir", str(media), str(py), cls]
        print(">>", " ".join(cmd), f"(TMOT_FORMAT={fmt}, storyboard)")
        subprocess.run(cmd, check=True, env=env)
        png = newest_png(media, cls)
        if png is None:
            sys.exit(f"no still produced for {sid} ({cls})")
        dest = out_dir / f"{py.stem}.png"
        shutil.copy2(png, dest)
        made.append(dest)
    if skipped:
        print(f"({skipped} scenes outside --only kept as-is)")
    return out_dir, made


def write_index(build_dir: Path, out_dir: Path, fmt: str):
    project = json.loads(
        (build_dir / "scenes.json").read_text(encoding="utf-8"))
    by_id = {s["id"]: s for s in project["scenes"]}
    cards, t = [], 0
    for s in project["scenes"]:
        img = f"{s['order']:02d}_{s['id']}.png"
        have = (out_dir / img).exists()
        mm, ss = divmod(int(t), 60)
        t += s.get("duration", 0)
        reel = ('<span style="background:#ff2b4a;color:#fff;padding:1px 8px;'
                'border-radius:9px;font-size:12px">REEL</span> '
                if s.get("reel") else "")
        q = (f'<div style="color:#ffd75e;margin-top:6px">Q: '
             f'{html.escape(str(s["question"]))}</div>'
             if s.get("question") else "")
        imgtag = (f'<a href="{img}"><img src="{img}" loading="lazy" '
                  f'style="width:100%;border:1px solid #223;border-radius:6px">'
                  f'</a>' if have else
                  '<div style="padding:2em;color:#889">no still (outside '
                  '--only?)</div>')
        cards.append(f"""
<div style="background:#0d1117;border:1px solid #1c2733;border-radius:10px;padding:12px">
{imgtag}
<div style="margin-top:8px"><b>[{mm:02d}:{ss:02d}] {s['order']:02d} · {html.escape(s['id'])}</b>
 {reel}<span style="color:#7fd4ff">{html.escape(s['type'])}</span>
 · {s.get('duration', '?')}s</div>{q}
<div style="color:#aab;margin-top:6px">EN: {html.escape(s.get('narration_en', ''))}</div>
<div style="color:#889;margin-top:4px">HI: {html.escape(s.get('narration_hi', ''))}</div>
</div>""")
    n = len(by_id)
    doc = f"""<!doctype html><meta charset="utf-8">
<title>{html.escape(project.get('video_title', build_dir.name))} — storyboard</title>
<body style="background:#05070a;color:#dde;font:15px/1.55 system-ui;margin:0;padding:24px">
<h1 style="font-weight:500">{html.escape(project.get('video_title', build_dir.name))}
 — storyboard <span style="color:#889;font-size:16px">({fmt}, {n} scenes,
 ~{t}s planned)</span></h1>
<p style="color:#889">Audit stills: each is the scene's final composed frame
(layout, LaTeX, colors, overflow) — not motion. Fix a scene in the source
.md, then re-run with <code>--only=&lt;id&gt;</code>.</p>
<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:16px">
{''.join(cards)}
</div></body>"""
    idx = out_dir / "index.html"
    idx.write_text(doc, encoding="utf-8")
    return idx


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    build_dir = Path(sys.argv[1])
    args = set(sys.argv[2:])
    fmt = "instagram" if "--ig" in args else "youtube"
    only = None
    for a in list(args):
        if a.startswith("--only="):
            only = {s.strip() for s in a.split("=", 1)[1].split(",")
                    if s.strip()}
    project = json.loads(
        (build_dir / "scenes.json").read_text(encoding="utf-8"))
    if only:
        known = {s["id"] for s in project["scenes"]}
        unknown = only - known
        if unknown:
            sys.exit(f"--only: unknown scene id(s) {sorted(unknown)}. "
                     f"Known: {sorted(known)}")
    out_dir, made = render_stills(build_dir, project, fmt, only)
    idx = write_index(build_dir, out_dir, fmt)
    print(f"\nstoryboard: {len(made)} stills -> {out_dir}\naudit view -> {idx}")


if __name__ == "__main__":
    main()
