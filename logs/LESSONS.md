# LESSONS.md — persistent issue & mistake log (append-only)

Read this FIRST every session. Append an entry BEFORE fixing any failure.
Entry format:

```
## L-<number> | <date> | <step: ingest|blog|annotate|parse|generate|render|other>
- Symptom: what broke / what was wrong
- Cause: root cause once known
- Fix: what resolved it
- Rule: one-line rule to prevent recurrence
```

---

## L-1 | 2026-07-12 | annotate
- Symptom: YAML parse errors on scene blocks containing LaTeX.
- Cause: single backslashes in `tex:` fields — YAML eats them.
- Fix: double-escape all backslashes in YAML LaTeX (`\\frac`, `\\mathrm`).
- Rule: every `tex:` string gets double backslashes; verify with step-3 parser before proceeding.

## L-2 | 2026-07-12 | render
- Symptom: (placeholder) content overflows frame in 9:16 Instagram format.
- Cause: layouts designed for 16:9 width.
- Fix: wrap the scene's root VGroup in `self.fit(...)` and use `S.ig_safe_shift`.
- Rule: any new archetype in scene_library.py must call `self.fit()` on its main group and respect IG safe areas.

## L-3 | 2026-07-12 | other (environment)
- Symptom: risk of polluting system Python / WSL with pip installs.
- Cause: pipeline originally documented bare `pip install`.
- Fix: dedicated conda env `tmot` (environment.yml); texlive-core inside env.
- Rule: NEVER run or install outside `conda activate tmot` / `conda run -n tmot`. Missing packages go into environment.yml, not ad-hoc pip.

## L-4 | 2026-07-12 | render
- Symptom: first real render (attention, scene 02_attention_equation) died with
  "latex failed but did not produce a log file". `latex -halt-on-error` on a
  minimal `standalone` doc aborted with `Can't locate mktexlsr.pl in @INC` and
  `can't find the format file 'latex.fmt'`; `kpsewhich standalone.cls` / `preview.sty`
  returned nothing.
- Cause: conda-forge `texlive-core` in the `tmot` env is broken — its Perl helper
  scripts (mktexfmt/fmtutil) can't find `mktexlsr.pl`, so no `latex.fmt` format is
  built, and it lacks standalone/preview classes. The env's `bin/latex` shadows a
  fully working system TeX Live 2021 (texlive-latex-extra etc.) already on the box.
- Fix: drop `texlive-core` from environment.yml and let manim use the system TeX
  (`/usr/bin/latex`, `/usr/bin/dvisvgm`). Concretely: `conda remove -n tmot texlive-core`
  so the conda latex no longer shadows the system one. System TeX compiles the
  manim template fine. (apt route not needed here — texlive already installed; sudo
  requires a password anyway.)
- Rule: LaTeX for this pipeline comes from SYSTEM TeX Live, not conda. Do not add
  `texlive-core` back to environment.yml. If a render needs a missing .sty/.cls,
  install it via system apt (`texlive-latex-extra`, `texlive-fonts-extra`), not conda.

## L-5 | 2026-07-12 | render (new archetype)
- Symptom: `equation_annotated` built with `MathTex(tex, substrings_to_isolate=[...])`
  silently DROPPED connective glyphs (the "= softmax( ... )", commas, superscripts)
  on the attention equation — only the isolated tokens and the \\frac survived.
- Cause: `substrings_to_isolate` re-tokenizes and breaks on nested
  `\\frac` / `\\!\\left( ... \\right)` boundaries; isolated pieces render but the
  spanning wrapper glyphs get mis-placed/hidden. Confirmed on a settled still.
- Fix: build the equation from an explicit list of latex chunks —
  `MathTex(*parts)` — and color/annotate parts by INDEX (spec: parts, color_idx,
  color_names, callout_idx, callout_text). Robust; renders full equation in 16:9
  and 9:16.
- Rule: never use substrings_to_isolate on equations containing \\frac or
  \\left(\\right). Split into author-controlled `parts` and address them by index.

## L-6 | 2026-07-12 | build (stale scenes)
- Symptom: risk of an old scene .py polluting a re-render after the source .md's
  scene set changes (render.py globs ALL build/<name>/scenes/*.py).
- Cause: generate_scripts.py writes new files but never deletes removed ones.
- Fix: `rm -rf build/<name>` before re-running the pipeline when scene ids change.
- Rule: when scene ids/count change in a .md, delete build/<name> first so no
  orphaned scene files get stitched into the video.

## L-7 | 2026-07-12 | render (stitch)
- Symptom: `render.py build/attention --preview` rendered all 13 scenes fine but
  the final ffmpeg concat failed ("Error opening input file ...youtube.txt").
- Cause: passing a RELATIVE build dir made the concat list contain relative clip
  paths. ffmpeg's concat demuxer resolves `file '...'` entries relative to the
  LIST FILE's directory, not the cwd, so they weren't found. main.py avoided this
  by passing an absolute build dir; a direct relative call exposed it.
- Fix: render.py stitch() now writes `c.resolve().as_posix()` (absolute) into the
  concat list and passes absolute list/out paths to ffmpeg.
- Rule: concat list entries must be absolute. Either rely on main.py (absolute
  build dir) or keep render.py's resolve() in place.

## L-8 | 2026-07-12 | other (visual redesign)
- Symptom: (design change, plus one crash) after the Tufte redesign, scenes that
  position content with `next_to(title, ...)` inherited the title's new TOP-LEFT
  anchor and hugged the left edge; also base_scene.py crashed with
  `NameError: LEFT` (missing manim import).
- Cause: `title_bar()` changed from a centered heading to a top-left running
  head returning VGroup(text, hairline). Content that centers itself on the
  title must now recenter explicitly.
- Fix: import LEFT in base_scene.py; SoftmaxBuild does `formula.set_x(0)` after
  `next_to(title, DOWN)`.
- Rule: title_bar() is a top-left running head (Tufte). Never center content
  relative to it — position content on the frame (set_x(0), move_to) instead.
  Visual identity levers: palette in config/channel.yaml only; depth via
  S.shadow()/S.with_depth()/set_sheen(); hairlines via S.hairline().

## L-9 | 2026-07-12 | render (3D base scene)
- Symptom: after TMOTScene became a ThreeDScene (camera phi=11°, ambient phi
  drift): (a) world-space watermark clipped off the right edge; (b) grid-floor
  lines streaked ACROSS the content zone.
- Cause: (a) camera pitch reprojects world-space corner HUD out of frame;
  (b) the rotated NumberPlane extended to z > 0 — geometry at/behind the camera
  plane projects across the screen.
- Fix: (a) watermark via add_fixed_in_frame_mobjects (screen-pinned HUD);
  (b) floor pre-rotation y_range capped at -1 so all floor geometry stays at
  z <= -1 in front of the camera.
- Rule: in 3D scenes, HUD elements (watermark, anything corner-pinned) must be
  fixed-in-frame; any background geometry must stay strictly in front of the
  camera plane (z < 0). Content enters with FadeIn(shift=OUT*n) and TMOTScene.
  tear_down() auto-recedes it (shift IN*9 + fade) — stills via `manim -s` show
  an EMPTY final frame now; verify with mid-clip ffmpeg frames instead.

## L-10 | 2026-07-13 | render (background stage)
- Symptom: 2 failed layouts for the mountain/sky/tiles stage: (1) screen-pinned
  sky with a mid-frame horizon put bright gradient bands ACROSS the content
  zone; (2) moving sky+mountains into world space (z=-60/-28) made them project
  near/below the bottom edge — invisible (perspective math guessed wrong, and
  Mobject.rotate() pivots about the mobject CENTER, not the origin, silently
  misplacing rotated planes).
- Cause: mixing screen-space and world-space anchoring for elements that must
  visually meet on the horizon line is fragile; camera focal projection is hard
  to predict analytically.
- Fix: split by motion need — sky gradient + mountain silhouettes + horizon
  glow are ALL screen-pinned (fixed-in-frame, horizon at HORIZON_FRAC=0.66 of
  frame height, ramp brightens only in the 0.9 units above the glow); only the
  scrolling tile floor + star particles live in 3D world space. Floor scroll
  updater wraps every TILE=2.0 units (offset stays in [0, TILE), near edge
  z <= -1 always).
- Rule: pin anything that must align with the horizon line to the SCREEN;
  reserve world space for elements whose motion/parallax is the point. When
  rotating a plane into the floor, pass about_point=ORIGIN.

## L-11 | 2026-07-13 | render (label morphs)
- Symptom: SoftmaxBuild's per-stage label swaps (raw -> e^x -> prob) rendered
  as garbled glyph soup for the full 1.5s morph; also on IG the replacement
  labels/bars were positioned WITHOUT ig_safe_shift, landing 0.24 units off.
- Cause: Transform() point-morphs between unrelated MathTex/Text glyphs —
  mid-states are unreadable; and restage rebuilt targets in unshifted coords.
- Fix: FadeTransform (cross-fade) for all text/number swaps; keep swapped
  labels in a plain python list (vlabels[:] = new_labs) since FadeTransform
  replaces mobjects; re-apply S.ig_safe_shift to every rebuilt target; anchor
  bar re-heights to the bar's CURRENT bottom (get_bottom()), not raw coords.
- Rule: never Transform between different text/formula strings — use
  FadeTransform. Anything rebuilt mid-scene must get the same ig_safe_shift
  as the original (or be positioned relative to live mobjects).

## L-12 | 2026-07-13 | render (branding)
- Symptom: branded intro/outro never appeared in any stitched output, even
  though channel.yaml has a full `branding:` section (user-reported).
- Cause: branded_intro()/branded_outro() were defined on TMOTScene but no
  scene class ever called them, and render.py only rendered scenes.json
  scenes — dead code since day one.
- Fix: added BrandedIntro/BrandedOutro classes to scene_library.py;
  render.py now renders them directly from the library file and stitches
  per-format according to new `branding.segments` in channel.yaml
  (youtube: intro+outro; instagram: outro only — reels must cold-open).
- Rule: any capability defined in base_scene.py must have a caller in the
  generator or renderer, or it silently doesn't exist; grep for call sites
  when adding features.
