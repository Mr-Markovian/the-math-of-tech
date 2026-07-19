# CONFIGURATION.md — the configurable setup, in one place

The mental model: **one edit surface per kind of change.** Find the row that
matches what you want to improve; edit only that file.

| You want to change…                                   | Edit this                | Then run |
|-------------------------------------------------------|--------------------------|----------|
| Wording, narration, conceptual clarity, scene order    | `content/<name>/<name>.md` | `python main.py … --only=<ids>` |
| The worked example: numbers, tokens, matrices, ranges  | the `scene` block's spec fields in the .md | same |
| Durations, what's in the reel, highlights              | `duration:` / `reel:` / `highlight:` fields | same |
| A table / new instance of an EXISTING visual form      | add a `scene` block with that `type:` | same |
| A visual form that does not exist yet                  | `templates/scene_library.py` (+ 2 registries, see below) | full render |
| Colors, fonts, watermark, tags, intro/outro text       | `config/channel.yaml`      | full render |
| Background (procedural wave ⇄ your own images)         | `config/channel.yaml` `background:` | full render |
| Stage motion: wave speed/shape, camera pitch/drift     | `templates/base_scene.py` constants | full render |
| How the LLM writes blogs/scene blocks (steps 1–2)      | `PROMPTS.md`               | re-run TASK blog/annotate |

Rule of thumb: **content lives in the .md; capability lives in the code;
brand lives in channel.yaml.** If an improvement needs no new *kind* of
visual, you never touch code.

---

## 1. The .md file — yes, you edit it directly

`content/<name>/<name>.md` is the single source of truth: blog post,
narration script, and animation spec in one file. Editing it directly is the
designed workflow, not a workaround. Prose between scene blocks is your blog;
each fenced ```scene block (YAML) becomes one rendered clip.

Required fields in every block:

```yaml
type: matrix_multiply        # one of the archetypes below
id: scores_matmul            # unique snake_case; this is the --only handle
narration_en: "…"            # both narration tracks, always
narration_hi: "…"
```

Optional common fields: `title:` (running head), `duration:` (seconds,
default 8), `reel: true` (include in the Instagram cut), `shimmer:
true|false` (equation scenes only — overrides the brand-wide
`style.equation_shimmer` toggle per scene).

Hard rules (enforced by the parser or by painful experience — see
`logs/LESSONS.md`):
- LaTeX in YAML needs **double backslashes**: `"\\frac{a}{b}"` (L-1).
- `id`s unique, snake_case; 4–7 blocks marked `reel: true` forming a
  self-contained 45–90s story.
- On-screen text English; both narration languages present.
- Validate cheaply after editing: `python pipeline/blog_to_scenes.py
  content/<name>/<name>.md` (step 3 alone, instant).

## 2. Templates do NOT change dynamically — and that's the point

Each `type:` maps to a **static, parametrized class** (an "archetype") in
`templates/scene_library.py`. The .md block's YAML is injected as that
class's `spec` dict at generate time (step 4 writes a tiny .py per scene).
Same template + different spec = different scene. Nothing about the template
mutates at render time.

So for your three improvement cases:
- **Conceptual clarity** → rewrite prose/narration/titles in the .md. No code.
- **Different example** → change spec data (`tokens:`, `a:`/`b:` matrices,
  `scores:`, `points:` …). No code.
- **A table** → `type: table` exists (see catalog). A block like:

```yaml
type: table
id: rnn_vs_transformer
title: "RNN vs Transformer"
headers: ["", "RNN", "Transformer"]
rows:
  - ["training", "sequential", "parallel"]
  - ["BLEU (EN-DE)", "24.6", "28.4"]
highlight: [1, 2]      # row, col into rows (0-indexed)
```

Only a **new kind** of visual (e.g. an animated tree diagram) means code: one
new class + registration (section 4).

## 3. Archetype catalog (type: → spec fields)

| type | what it shows | spec fields (beyond title/duration/reel/narration) |
|------|---------------|-----------------------------------------------------|
| `concept_title` | title card | `subtitle` |
| `equation_reveal` | equations written line by line | `tex` (list), `highlight` (index) |
| `equation_annotated` | one equation, color-coded parts + callout arrow | `parts` (list of latex chunks), `color_idx`, `color_names`, `callout_idx`, `callout_text` |
| `equation_steps` | derivation chain, steps morph into each other | `steps` (list), `labels`, `anchor` (dimmed general form), `color_map` {tex: color}, `isolate` |
| `transform` | equation A morphs to B | `tex_from`, `tex_to` |
| `graph` | function plot | `function` (numpy expr in x), `x_range`, `y_range`, `label` |
| `graph_morph` | functions morphing in sequence on persistent axes | `functions` (list of numpy exprs in x), `labels`, `captions`, `colors`, `x_range`, `y_range`, `fill` (bool) |
| `tokens_to_vectors` | sentence → token chips → spin vectors → stacked matrix X | `text`, `max_toks`, `seed`, `decimals`, `show_matrix` |
| `neural_net` | layered net + forward-pass pulse | `layers` (e.g. [3,5,2]) |
| `attention_matrix` | token×token heatmap | `tokens`, `weights` (real, row-stochastic), `focus_row` |
| `matrix_multiply` | A×B=C with real numbers, row walk | `a`, `b` (2D lists), `a_label`, `b_label`, `c_label`, `decimals`, `highlight_row` |
| `softmax_build` | bars: scores → exp → normalized | `scores`, `labels`, `decimals` |
| `multi_head` | h heads → concat → W^O | `n_heads` |
| `table` | Tufte table, staged rows, cell highlight | `headers`, `rows`, `highlight` [r,c], `align` ('center'/'left') |
| `split_relate` | two panels (L/R on 16:9, stacked on reels) with animated links referencing their parts | `left`, `right` (each `{kind: matrix\|list\|vectors\|graph\|tex, …}`), `left_label`, `right_label`, `links` [{from,to,color,label}] |
| `bullet_points` | staged text points (use sparingly) | `points` |

Color names accepted wherever a color is a parameter: `blue`, `yellow`,
`red`, `green`, `purple`, `text` — these are ROLES from `channel.yaml`, not
literal colors (today: neon blue / white / neon red / light blue / deep blue
/ white). Rebrand the palette and every scene follows.

## 4. Adding a new archetype (the only "template change")

1. Write a class in `templates/scene_library.py` subclassing `TMOTScene`,
   parametrized ONLY via `self.spec` — no scene-specific constants.
2. Register it in **three** places (all three, or step 3/4/5 rejects it):
   `SCENE_TYPES` (scene_library.py), `KNOWN_TYPES` (pipeline/blog_to_scenes.py),
   `CLASS_MAP` (pipeline/generate_scripts.py). If any spec field carries
   LaTeX, ALSO add it to `latex_jobs()` in `pipeline/check_tex.py` — that
   map mirrors scene_library, and an unmapped field silently skips the
   step-3.5 tex check. Document the type in PROMPTS.md's schema + the
   catalog above.
3. House rules inside `construct()`:
   - call `self.add_watermark()` first; `self.title_bar(...)` for headers
   - `self.fit(group)` + `S.ig_safe_shift(group, self.fmt)` on the main
     group so one layout survives 16:9 AND 9:16 (L-2)
   - colors ONLY via `S.BLUE / S.RED / …` — never hex (rebrand safety)
   - text/number swaps use `FadeTransform`, never `Transform` (L-11)
   - entrances: `FadeIn(group, shift=OUT * 3)`; the exit is automatic
     (`tear_down` recedes everything into depth)
4. Smoke-test it standalone in a scratch .md before using it in a real video;
   verify frames from the rendered mp4, not `manim -s` (L-9).

## 5. The fix-one-scene loop (mature workflow)

```
1. edit the scene block(s) in content/<name>/<name>.md
2. python pipeline/blog_to_scenes.py content/<name>/<name>.md   # validate YAML
3. python pipeline/storyboard.py build/<name> --only=<id1,id2>  # seconds/scene:
   composed still per scene — check layout/LaTeX/colors BEFORE animating
4. python main.py content/<name>/<name>.md --only=<id1,id2>     # ~30s/scene
   (main.py auto-runs pipeline/check_tex.py first — bad LaTeX fails in
    seconds here, before any manim startup; --skip-tex to bypass)
5. check the re-stitched mp4s in build/<name>/
```

`--only` re-renders just those ids, reuses every other clip and the branding
segments, and re-stitches both cuts. Reuse is manifest-guarded (renders/
<fmt>/manifest.json): a reused scene whose block changed since its stamp,
a missing stamp, or a quality-mode mismatch each abort with a clear message
instead of stitching a stale clip. Caveats: needs one prior full render; if
ids were added/removed/renamed do `rm -rf build/<name>` + full render
(L-6/L-13). Full details in README → "Reworking only specific scenes".

## 6. channel.yaml — every brand/config knob

- `colors:` — the role palette (background/text/5 accents/grid/muted).
  Scenes reference roles, so this is the ONE place to rebrand.
- `style:` — motion-graphic toggles. `equation_shimmer: true` draws a thin
  neon frame + slow traveling glint around hero equations in
  equation_reveal / equation_annotated / transform, AFTER the equation
  settles (clarity first: thin stroke, no fill, generous margin; per-scene
  override with `shimmer: false` in the block; equation_steps is exempt —
  its chain morphs, a fixed frame would fight it).
- `fonts:` — heading/body/code + Devanagari fallback.
- `background:` — `mode: procedural` (wireframe wavefunction stage) or
  `mode: image` + `image_youtube:`/`image_instagram:` paths to your own art
  (auto-scaled to cover each frame).
- `branding:` — intro/outro text, taglines, CTAs, and `segments:` per format
  (reels default to outro-only; a cold open wins for short-form).
- `formats:` — resolutions, fps, IG safe areas, target durations.
- `tags:` — upload metadata per platform.
- `channel:` — name/handle/watermark.

Stage motion knobs live as class constants in `templates/base_scene.py`:
`WAVE_SPEED`, `WAVE_K1`, `WAVE_K2` (wave field), camera pitch/drift in
`setup()`. The wave wraps on its exact x-period, so the drift is seamless
regardless of speed.

## 7. Session hygiene

After any failure or notable fix, append to `logs/LESSONS.md`; before ending
a session, update `logs/STATE.md`. These are the cross-session memory —
the reason repeat mistakes don't happen twice.
