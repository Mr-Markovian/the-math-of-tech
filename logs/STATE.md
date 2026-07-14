# STATE.md — where each project stands (update before ending every session)

Format: one section per project.

## repo / infrastructure (2026-07-14)
- Git repo initialized in manim-pipeline/. .gitignore ships the pipeline only:
  content/ and build/ (+ any renders/mp4s) are ignored; logs/ IS tracked
  (Roy approved). 15 top-level items tracked.
- skills/ MOVED INTO the repo: `manim-pipeline/skills/visual-storytelling/
  SKILL.md` (was ../skills/ at My Academy root). All references updated to
  the new path (README, CLAUDE.md, tasks.md, PROMPTS.md; STATE refs were
  already relative). Verified: parse runs clean (19 scenes), skills/ tracked,
  content/build ignored. Next: Roy commits + pushes (gh repo create).

## attention (REBUILD — content/attention/, 2026-07-13)
- Full-pipeline rebuild from the paper, replacing the example as the flagship.
  Steps 0–2 DONE: content/attention/source.md (paper facts verified against
  ar5iv 1706.03762), blog.md, attention.md (scene-annotated, 19 scenes, 6 reel,
  ~482s YT / 77s reel; token_embedding scene added 2026-07-13 — learned
  embeddings, E-gradient update, one-static-row-per-token trap). Written under skills/visual-storytelling/SKILL.md:
  beat sheet + color registry + carry_in/carry_out on every scene; new depth
  scenes: variance derivation (Var(q·k)=d_k), shapes/projections, multi-head
  dims, complexity O(n²d) vs O(n d²), positional encodings.
- Last completed step: 2 (annotate). Next action: steps 3–5 —
  `conda activate tmot && python main.py content/attention/attention.md`
  (Cowork session 2026-07-13 could not run these: sandbox couldn't mount the
  WSL folder). NOTE: this build dir name collides with the old example
  (build/attention) and will overwrite it — intended.
- Also this session: BrandedIntro/BrandedOutro now stitched by render.py per
  channel.yaml branding.segments (see LESSONS L-12) — first render of this
  project will be the first with intro/outro.
- NEW ARCHETYPE (2026-07-13, NOT YET RENDER-TESTED): `equation_steps` in
  scene_library.py — derivation chains morphing via TransformMatchingTex,
  with anchor (dimmed general form on top), labels (move names, FadeTransform
  per L-11), color_map (symbol identity via substrings_to_isolate +
  set_color_by_tex), isolate (extra match substrings). Registered in
  generate_scripts.py CLASS_MAP + blog_to_scenes.py KNOWN_TYPES + PROMPTS.md
  schema. First consumer: variance_growth scene in content/attention/
  attention.md. On first render, watch for: (a) overlapping isolate
  substrings breaking LaTeX (test tex in isolation per CLAUDE.md rule),
  (b) match quality between steps — tune `isolate` if parts fade instead of
  morphing.
- NEW (2026-07-13, NOT YET RENDER-TESTED): universal `question:` field on any
  scene — base_scene.tear_down renders it (yellow, bottom) before the recede;
  `tokens_to_vectors` archetype — sentence → tokens → seeded random-direction
  spin vectors → stacked matrix X (declutter built in: chips dim, spins
  absorbed into rows). Registered in CLASS_MAP + KNOWN_TYPES + PROMPTS.md.
  attention.md now 20 scenes ~507s: new text_to_vectors scene + question:
  on 7 scenes.
- NEW ARCHETYPE (2026-07-13, NOT YET RENDER-TESTED): `graph_morph` —
  functions morphing in sequence on persistent axes (labels/captions
  cross-fade per L-11; optional per-stage colors; fill: true shades area,
  morphed along). Registered in CLASS_MAP + KNOWN_TYPES + PROMPTS.md.
  Built for distribution shifts (prior→posterior etc.) and future
  quant/physics curves. Archetype roadmap (add ON DEMAND when a video needs
  them, keep generic): sample_paths (seeded random walks/GBM — quant),
  histogram_vs_pdf (samples→distribution bridge), vector_field /
  phase_portrait (dynamics), wave_evolution (updater-based). Rule: recurring
  visual pattern → new archetype in scene_library.py + CLASS_MAP +
  KNOWN_TYPES + PROMPTS.md schema, all four or the pipeline rejects it;
  one-off visual → hand-written .py dropped into build/<name>/scenes/.

## attention (example project)
- Last completed step: 5 (render) — wavefunction background baked into both
  cuts on 2026-07-13 (preview quality). Now 18 scenes, 6 reel.
- Partial re-render supported (2026-07-13): `--only=<id1,id2>` on render.py
  and main.py re-renders just those scene ids, reuses all other scene +
  branding mp4s from build/<name>/renders/, re-stitches both cuts (~30s for
  1 scene). Documented in README "Reworking only specific scenes". Needs one
  prior full render; same quality mode; full re-render after id changes (L-6).
- `table` archetype added (2026-07-13): Tufte-style (headers + hairline, no
  gridlines), staged rows, [row,col] highlight, center/left align; registered
  in all 3 registries; smoke-tested in YT format. 13 types total.
- docs/CONFIGURATION.md added (2026-07-13): the edit-surface map (.md vs
  scene_library vs channel.yaml), full archetype catalog with spec fields,
  new-archetype recipe (3 registries + house rules), fix-one-scene loop.
  Linked from README structure section and CLAUDE.md header.
- Equation shimmer added (2026-07-13): channel.yaml style.equation_shimmer
  (default true) + per-scene `shimmer:` override. S.shimmer_frame() (thin
  rounded rect, blue→white→blue gradient stroke, no fill, width-clamped) +
  TMOTScene.shimmer_in() (dt-updater glint looping the perimeter, 4.5s/lap).
  Wired into equation_reveal, equation_annotated, transform — applied AFTER
  the equation settles; equation_steps exempt (morphing chain). Smoke-tested
  YT: glint verified moving across frames.
- render.py now skips formats absent from channel.yaml formats (IG currently
  commented out there → IG cut skipped with a notice instead of KeyError).
- WATCH: fonts.body in channel.yaml is "'URW Gothic" (stray leading quote) —
  probably a typo; manim will silently fall back if the name doesn't resolve.
- README Q&A section added (2026-07-13): "from research paper to final
  animated .md" — first-file creation (markitdown → ingest), skills for
  steps 1–2 (PROMPTS.md under skills/visual-storytelling), Roy's
  key-questions→voice→feedback flow mapped to beat sheet + question: field +
  the TASK full approval gates, and a QC table (concern → artifact → lever).
- QUESTION-DRIVEN STORYTELLING UPGRADE (2026-07-13, per Roy: "told like
  facts" = the failure mode): SKILL.md gained Step −2 Question Ladder
  (claims → curiosity questions via taxonomy: why / what's different / why
  required / what leads here / how realized / how fixed / what's missing /
  why more important / why impact; pause-test ranking; 5–9 question spine)
  and Step −1 Story Plan gate (content/<name>/plan.md: spine + beat-sheet-
  as-questions + scene map answers/raises + flow test; GO/NO-GO — failed
  flow = stop, restructure, never execute) + checklist item 16 (no orphan
  answers / no fact-scenes). New TASK plan in tasks.md; TASK full now
  ingest → plan(gate) → blog(gate) → annotate(gate) → build. PROMPTS.md
  Step 0 added; Step 1 rewritten to answer the spine in order.
  AGENT_WORKFLOW flow + gates and README Q&A updated to 3 gates.
- Next action: production render if desired:
  `python main.py content/example/attention.md --final`
- Outputs: build/attention/attention_youtube.mp4 (1920x1080, ~99.6s, 13 scenes),
  build/attention/attention_instagram.mp4 (1080x1920, ~49.3s, 6 reel scenes).
- Worked example (consistent across all numeric scenes): tokens river/bank/money,
  d_k=2, Q=[[2,0],[2,1],[0,2]], K=[[2,0],[1,1],[0,2]], V=[[1,0],[1,1],[0,1]];
  scores=QK^T=[[4,2,0],[4,3,2],[0,2,4]]; bank row softmax=[0.58,0.19-ish]→river.
- New archetypes added this session: equation_annotated, matrix_multiply,
  softmax_build, multi_head; attention_matrix now takes real `weights`+`focus_row`.
  All validated in 16:9 and 9:16. See LESSONS L-4..L-7.
- VISUAL IDENTITY (current, 2026-07-13): pure-black stage + grey wireframe
  wavefunction + neon red/blue/white text (config/channel.yaml). TMOTScene is
  a ThreeDScene — _wave_bg(): 30 depth rows of a superposed cos/sin wave
  (WAVE_K1 1.8, WAVE_K2 0.9), amplitude varying with depth, drifting sideways
  forever (WAVE_SPEED 0.35, seamless wrap every 2π/K2), camera pitch 11° with
  slow phi drift. Content flies in from depth and auto-recedes in tear_down.
  Tufte running-head titles + hairlines. Personal-image override still
  available via channel.yaml background.mode: image. Earlier stages (navy
  synthwave mountains, aubergine) superseded. See LESSONS L-8..L-11.
- Notes: safe to delete build/ and re-run. Env `tmot` (manim 0.20.1). LaTeX from
  SYSTEM TeX Live, not conda (L-4). `manim -s` stills are empty now (L-9) —
  verify frames from rendered mp4s.
