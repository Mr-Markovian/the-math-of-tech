"""
main.py — one-command runner for the DETERMINISTIC steps (3–5).

Steps 1–2 (ingest → blog → scene annotation) are LLM work: run them via
Claude Code ("run TASK full for <name>", see tasks.md). Once the annotated
.md exists, this script does everything else:

    conda activate tmot
    python main.py content/example/attention.md              # parse+generate+preview
    python main.py content/example/attention.md --final      # production render
    python main.py content/example/attention.md --no-render  # parse+generate only
    python main.py content/example/attention.md --yt-only | --ig-only
    python main.py content/example/attention.md --only=softmax_row,hook_title
        # rework specific scene ids only; all other scenes are reused from
        # build/<name>/renders/ and the final videos are re-stitched
    python main.py content/example/attention.md --skip-tex
        # skip the step-3.5 LaTeX pre-compile check (pipeline/check_tex.py)
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(cmd):
    print("\n== " + " ".join(cmd))
    r = subprocess.run(cmd, cwd=ROOT)
    if r.returncode != 0:
        sys.exit(f"FAILED (exit {r.returncode}): {' '.join(cmd)}\n"
                 f"-> log the failure in logs/LESSONS.md before fixing.")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    md = Path(sys.argv[1])
    flags = set(sys.argv[2:])
    if not md.exists():
        sys.exit(f"not found: {md}")

    py = sys.executable
    build = ROOT / "build" / md.stem

    run([py, "pipeline/blog_to_scenes.py", str(md)])
    if "--skip-tex" not in flags:
        run([py, "pipeline/check_tex.py", str(build / "scenes.json")])
    run([py, "pipeline/generate_scripts.py", str(build / "scenes.json")])

    if "--no-render" in flags:
        print(f"\nDone (no render). Scenes: {build/'scenes'} | "
              f"Narration: {build/'narration.md'}")
        return

    render_cmd = [py, "pipeline/render.py", str(build)]
    if "--final" not in flags:
        render_cmd.append("--preview")
    for f in flags:
        if f in ("--yt-only", "--ig-only") or f.startswith("--only="):
            render_cmd.append(f)
    run(render_cmd)
    print(f"\nDone. Videos in {build}/")


if __name__ == "__main__":
    main()
