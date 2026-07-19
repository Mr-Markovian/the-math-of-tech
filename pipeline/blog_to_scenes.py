"""
blog_to_scenes.py — Step 3 of the pipeline.
Parses a blog .md file containing fenced ```scene blocks (YAML) and
emits a scenes.json spec used by generate_scripts.py.

Blog format: normal markdown prose (this IS your blog post / narration
script), with scene blocks embedded wherever a visual should appear:

    ```scene
    type: equation_reveal
    id: softmax
    title: "Softmax"
    tex:
      - "\\mathrm{softmax}(x_i) = \\frac{e^{x_i}}{\\sum_j e^{x_j}}"
    narration_en: "Softmax turns scores into probabilities."
    narration_hi: "Softmax scores ko probabilities mein badal deta hai."
    duration: 10
    reel: true        # include in the Instagram cut
    ```

Usage:
    python pipeline/blog_to_scenes.py content/example/attention.md
"""
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCENE_BLOCK = re.compile(r"```scene\s*\n(.*?)```", re.DOTALL)

REQUIRED = {"type", "id"}
KNOWN_TYPES = {"concept_title", "equation_reveal", "equation_annotated",
               "equation_steps", "transform", "graph", "graph_morph",
               "tokens_to_vectors", "neural_net",
               "attention_matrix", "matrix_multiply", "softmax_build",
               "multi_head", "table", "split_relate", "bullet_points"}


def parse_blog(md_path: Path) -> dict:
    text = md_path.read_text(encoding="utf-8")
    title_m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    scenes, errors = [], []
    for i, m in enumerate(SCENE_BLOCK.finditer(text)):
        try:
            spec = yaml.safe_load(m.group(1))
        except yaml.YAMLError as e:
            errors.append(f"block {i}: YAML error: {e}")
            continue
        missing = REQUIRED - set(spec)
        if missing:
            errors.append(f"block {i}: missing {missing}")
            continue
        if spec["type"] not in KNOWN_TYPES:
            errors.append(f"block {i} ({spec['id']}): unknown type "
                          f"'{spec['type']}'. Known: {sorted(KNOWN_TYPES)}")
            continue
        spec.setdefault("duration", 8)
        spec.setdefault("reel", False)
        spec["order"] = i
        scenes.append(spec)
    if errors:
        raise SystemExit("Blog parse errors:\n  " + "\n  ".join(errors))
    return {
        "source": str(md_path),
        "video_title": title_m.group(1) if title_m else md_path.stem,
        "scenes": scenes,
    }


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    md_path = Path(sys.argv[1])
    project = parse_blog(md_path)
    out_dir = ROOT / "build" / md_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "scenes.json"
    out.write_text(json.dumps(project, indent=2, ensure_ascii=False),
                   encoding="utf-8")
    n_reel = sum(s["reel"] for s in project["scenes"])
    total = sum(s["duration"] for s in project["scenes"])
    print(f"OK: {len(project['scenes'])} scenes "
          f"({n_reel} marked for reel), ~{total}s planned -> {out}")


if __name__ == "__main__":
    main()
