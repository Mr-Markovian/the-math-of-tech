"""
render.py — Step 5 of the pipeline.
Renders every generated scene in BOTH formats, then stitches each cut
into a single video with ffmpeg.

  YouTube cut  : all scenes, 16:9 1920x1080
  Instagram cut: only scenes with reel: true, 9:16 1080x1920

Usage:
    python pipeline/render.py build/attention [--preview] [--yt-only|--ig-only]
                                              [--only=<id1,id2,...>]

--only=softmax_row,attention_full re-renders JUST those scene ids and reuses
every other scene's existing mp4 from build/<name>/renders/, then re-stitches
both cuts. Requires one prior full render (the reused files must exist).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# which branded segments to stitch into each cut; overridable via
# branding.segments in config/channel.yaml. Reels default to outro-only:
# a 2.5s intro before the hook kills short-form retention (cold open wins).
DEFAULT_SEGMENTS = {"youtube": ["intro", "outro"], "instagram": ["outro"]}


def available_formats() -> set:
    """Formats actually configured in channel.yaml — a format commented out
    there (e.g. instagram during fast iteration) is skipped, not crashed on."""
    try:
        import yaml
        cfg = yaml.safe_load(
            (ROOT / "config" / "channel.yaml").read_text(encoding="utf-8"))
        return set((cfg.get("formats") or {}).keys())
    except Exception:
        return {"youtube", "instagram"}


def branding_segments(fmt: str) -> list:
    try:
        import yaml
        cfg = yaml.safe_load(
            (ROOT / "config" / "channel.yaml").read_text(encoding="utf-8"))
        segs = (cfg.get("branding") or {}).get("segments") or DEFAULT_SEGMENTS
    except Exception as e:
        print(f"(branding.segments unreadable, using defaults: {e})")
        segs = DEFAULT_SEGMENTS
    return list(segs.get(fmt, []))


def newest(out_root: Path, cls: str):
    """Most recent rendered mp4 for a scene class, or None."""
    hits = list(out_root.rglob(f"{cls}.mp4"))
    return max(hits, key=lambda p: p.stat().st_mtime) if hits else None


def render_branding(which: str, fmt: str, quality: str, out_root: Path,
                    reuse: bool = False):
    """Render BrandedIntro/BrandedOutro straight from scene_library.py.
    With reuse=True, skip rendering when a previous mp4 exists."""
    cls = {"intro": "BrandedIntro", "outro": "BrandedOutro"}[which]
    if reuse:
        c = newest(out_root, cls)
        if c is not None:
            print(f"(reusing branding {which}: {c.name})")
            return c
    lib = ROOT / "templates" / "scene_library.py"
    env = {**os.environ, "TMOT_FORMAT": fmt}
    cmd = ["manim", f"-q{quality}", "--media_dir", str(out_root),
           str(lib), cls]
    print(">>", " ".join(cmd), f"(TMOT_FORMAT={fmt}, branding {which})")
    subprocess.run(cmd, check=True, env=env)
    c = newest(out_root, cls)
    if c is None:
        print(f"(warning: no output found for branding {which})")
    return c


def scene_class_name(py_file: Path) -> str:
    for line in py_file.read_text(encoding="utf-8").splitlines():
        if line.startswith("class "):
            return line.split("class ")[1].split("(")[0]
    raise ValueError(f"no class in {py_file}")


def render(build_dir: Path, fmt: str, quality: str, reel_ids: set,
           only: set = None):
    scenes_dir = build_dir / "scenes"
    out_root = build_dir / "renders" / fmt
    out_root.mkdir(parents=True, exist_ok=True)
    clips = []
    for py in sorted(scenes_dir.glob("*.py")):
        sid = py.stem.split("_", 1)[1]
        if fmt == "instagram" and sid not in reel_ids:
            continue
        cls = scene_class_name(py)
        if only and sid not in only:
            # selective mode: reuse this scene's existing render untouched
            c = newest(out_root, cls)
            if c is None:
                raise SystemExit(
                    f"--only: no existing {fmt} render for scene '{sid}' "
                    f"(expected under {out_root}). Run one full render "
                    f"first, or add '{sid}' to --only.")
            print(f"(reusing {sid}: {c.name})")
            clips.append(c)
            continue
        env = {**os.environ, "TMOT_FORMAT": fmt}
        cmd = ["manim", f"-q{quality}", "--media_dir", str(out_root),
               str(py), cls]
        print(">>", " ".join(cmd), f"(TMOT_FORMAT={fmt})")
        subprocess.run(cmd, check=True, env=env)
        c = newest(out_root, cls)
        if c:
            clips.append(c)

    # branded intro/outro (fixes: defined in base_scene but never rendered);
    # in selective mode they are reused, not re-rendered
    segs = branding_segments(fmt)
    if "intro" in segs:
        c = render_branding("intro", fmt, quality, out_root,
                            reuse=bool(only))
        if c:
            clips.insert(0, c)
    if "outro" in segs:
        c = render_branding("outro", fmt, quality, out_root,
                            reuse=bool(only))
        if c:
            clips.append(c)
    return clips


def stitch(clips, out_file: Path):
    if not clips:
        print(f"(no clips for {out_file.name})")
        return
    lst = out_file.with_suffix(".txt")
    # absolute paths so ffmpeg's concat demuxer resolves them regardless of
    # the list file's location or the invoking cwd (it resolves relative
    # entries against the list dir, not cwd — see logs/LESSONS.md L-7).
    lst.write_text("".join(f"file '{c.resolve().as_posix()}'\n" for c in clips),
                   encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                    "-i", str(lst.resolve()), "-c", "copy",
                    str(out_file.resolve())], check=True)
    print(f"final -> {out_file}")


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    build_dir = Path(sys.argv[1])
    args = set(sys.argv[2:])
    quality = "l" if "--preview" in args else "h"
    only = None
    for a in list(args):
        if a.startswith("--only="):
            only = {s.strip() for s in a.split("=", 1)[1].split(",")
                    if s.strip()}
            args.discard(a)
    project = json.loads((build_dir / "scenes.json").read_text(encoding="utf-8"))
    reel_ids = {s["id"] for s in project["scenes"] if s.get("reel")}
    if only:
        known = {s["id"] for s in project["scenes"]}
        unknown = only - known
        if unknown:
            raise SystemExit(f"--only: unknown scene id(s) {sorted(unknown)}. "
                             f"Known ids: {sorted(known)}")
    name = build_dir.name

    fmts = available_formats()
    for fmt, skip_flag in (("youtube", "--ig-only"), ("instagram", "--yt-only")):
        if skip_flag in args:
            continue
        if fmt not in fmts:
            print(f"({fmt} not configured in channel.yaml formats — skipping)")
            continue
        clips = render(build_dir, fmt, quality, reel_ids, only)
        stitch(clips, build_dir / f"{name}_{fmt}.mp4")


if __name__ == "__main__":
    main()
