"""
check_tex.py — Step 3.5: compile every LaTeX string in a project BEFORE any
render, so a bad `tex:` fails in seconds at parse time instead of minutes
into step 5. This automates the CLAUDE.md hard rule "test the offending
tex: string in isolation" — and runs it for every string, up front.

Compilation goes through manim's own MathTex (the exact render-time path,
including `substrings_to_isolate` for equation_steps, which can itself
break otherwise-valid LaTeX). Compiled tex is cached by manim in
<build>/texcheck/, so re-checks are near-instant.

Usage (inside the tmot conda env):
    python pipeline/check_tex.py build/attention/scenes.json
    python pipeline/check_tex.py content/attention/attention.md   # parses first
    python pipeline/check_tex.py --tex "\\frac{QK^T}{\\sqrt{d_k}}"

Exit 0 = every string compiles. Exit 1 = failures listed with scene id,
field, and the offending string. main.py runs this automatically after
step 3 (skip with --skip-tex).

NOTE: strings in scenes.json / --tex are POST-YAML (single backslashes).
If a string passes here but the YAML block fails at step 3, the problem is
escaping (LESSONS L-1), not the LaTeX.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "pipeline"))


def latex_jobs(spec):
    """Yield (field, mathtex_args, mathtex_kwargs) for every author-supplied
    LaTeX string this scene type sends through MathTex at render time.
    Mirrors templates/scene_library.py — update both when a new archetype
    gains a latex-bearing spec field."""
    t = spec["type"]
    if t == "equation_reveal":
        for i, s in enumerate(spec.get("tex") or []):
            yield f"tex[{i}]", [s], {}
    elif t == "transform":
        for f in ("tex_from", "tex_to"):
            if spec.get(f):
                yield f, [spec[f]], {}
    elif t == "graph":
        if spec.get("label"):
            yield "label", [spec["label"]], {}
    elif t == "equation_annotated":
        parts = [p for p in (spec.get("parts") or [])]
        if parts:
            yield "parts", parts, {}
    elif t == "equation_steps":
        iso = list(spec.get("color_map") or {}) + list(spec.get("isolate") or [])
        kw = {"substrings_to_isolate": iso or None}
        for i, s in enumerate(spec.get("steps") or []):
            yield f"steps[{i}]", [s], kw
        if spec.get("anchor"):
            yield "anchor", [spec["anchor"]], kw
    elif t == "graph_morph":
        for i, s in enumerate(spec.get("labels") or []):
            if s:
                yield f"labels[{i}]", [s], {}
    elif t == "split_relate":
        for side in ("left", "right"):
            p = spec.get(side) or {}
            kind = p.get("kind")
            if kind == "tex" and p.get("tex"):
                yield f"{side}.tex", [p["tex"]], {}
            elif kind == "graph" and p.get("label"):
                yield f"{side}.label", [p["label"]], {}
            elif kind == "vectors":
                for i, s in enumerate(p.get("labels") or []):
                    if s:
                        yield f"{side}.labels[{i}]", [s], {}


def load_mathtex(media_dir: Path):
    media_dir.mkdir(parents=True, exist_ok=True)
    from manim import MathTex, config
    config.verbosity = "ERROR"
    config.media_dir = str(media_dir)
    return MathTex


def compile_one(MathTex, args, kwargs):
    """Return None on success, short error text on failure."""
    try:
        MathTex(*args, **kwargs)
        return None
    except Exception as e:  # manim raises ValueError with the latex log
        msg = " ".join(str(e).split())
        return msg[:300] + ("…" if len(msg) > 300 else "")


def main():
    argv = sys.argv[1:]
    if not argv:
        raise SystemExit(__doc__)

    if argv[0] == "--tex":
        if len(argv) < 2:
            raise SystemExit("--tex needs a string argument")
        MathTex = load_mathtex(ROOT / "build" / "texcheck")
        err = compile_one(MathTex, [argv[1]], {})
        if err:
            sys.exit(f"FAIL: {argv[1]}\n  {err}")
        print(f"OK: {argv[1]}")
        return

    path = Path(argv[0])
    if not path.exists():
        sys.exit(f"not found: {path}")
    if path.suffix == ".md":
        from blog_to_scenes import parse_blog
        project = parse_blog(path)
        media_dir = ROOT / "build" / path.stem / "texcheck"
    else:
        project = json.loads(path.read_text(encoding="utf-8"))
        media_dir = path.parent / "texcheck"

    jobs = [(s["id"], field, args, kw)
            for s in project["scenes"]
            for field, args, kw in latex_jobs(s)]
    if not jobs:
        print("check_tex: no latex fields found — nothing to do")
        return

    print(f"check_tex: compiling {len(jobs)} latex strings "
          f"from {len(project['scenes'])} scenes …")
    MathTex = load_mathtex(media_dir)
    failures = []
    for sid, field, args, kw in jobs:
        err = compile_one(MathTex, args, kw)
        if err:
            failures.append((sid, field, args, err))
            print(f"  FAIL {sid}.{field}")

    if failures:
        print(f"\ncheck_tex: {len(failures)}/{len(jobs)} strings FAILED:\n")
        for sid, field, args, err in failures:
            shown = args[0] if len(args) == 1 else " | ".join(args)
            print(f"  {sid}.{field}\n    tex: {shown}\n    err: {err}\n")
        sys.exit("Fix the tex in the source .md (remember YAML double-"
                 "escaping, L-1), then re-run. For equation_steps, also "
                 "check color_map/isolate substrings — isolation itself "
                 "can break valid LaTeX.")
    print(f"check_tex: OK — all {len(jobs)} strings compile")


if __name__ == "__main__":
    main()
