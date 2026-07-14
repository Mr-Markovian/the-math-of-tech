# the_math_of_tech — animation pipeline

3blue1brown-style pipeline: research paper → blog/script (.md) → Manim scenes
→ one YouTube video (16:9) + one Instagram reel cut (9:16), from a single source file.

## Pipeline

```
0. Any source (markitdown .md) →  content/inbox/       (TASK ingest cleans it)
P. Source → STORY PLAN         →  plan.md              (TASK plan — GO/NO-GO GATE)
1. Plan + source → blog        →  blog post .md        (LLM, PROMPTS.md step 1)
2. Blog post   → scenes        →  scene-annotated .md  (LLM, PROMPTS.md step 2)
3. Parse    → scenes.json      (pipeline/blog_to_scenes.py)
4. Generate → scene .py files  (pipeline/generate_scripts.py)
5. Render   → YT + IG videos   (pipeline/render.py)
```

Outputs per project in `build/<name>/`: `scenes.json`, generated scene `.py`
files, `narration.md` (timestamped EN + Hinglish voiceover script), and
`<name>_youtube.mp4` + `<name>_instagram.mp4`.

The .md file is simultaneously your **blog post**, **narration script**, and
**animation spec** — one source of truth, three outputs.

**The storytelling law (why step P exists):** a video that tells facts in a
sensible order is still not a story. Every video is a chain of curiosity
questions — each scene answers the question on the table and raises the next.
Step P (the Question Ladder + Story Plan, from
`skills/visual-storytelling/SKILL.md`) turns the paper's claims into that
question chain BEFORE anything is written: a bad flow is stopped at a
one-page plan, not discovered in a rendered video. Steps 1–2 then execute
the approved plan; steps 3–5 render exactly what was approved.

## Workflow A — with Claude Code (full pipeline, steps 0–5)

Use this when starting from a paper/PDF/webpage: steps 0–2 are writing work
that needs an LLM. Details in `docs/AGENT_WORKFLOW.md`.

```
markitdown paper.pdf > content/inbox/lora.md   # any source → raw .md
conda activate tmot
claude                                          # in this folder
> run TASK full for lora
```

Claude Code auto-reads `CLAUDE.md`, follows `tasks.md`, and stops at **three
approval gates** — earliest is cheapest:

1. **plan.md** (go/no-go): is the question spine genuinely curiosity-driven,
   does each answer expose the next question? A failed flow test stops the
   pipeline here — restructure the spine, never execute a bad flow.
2. **blog.md**: voice check — are the spine questions being ANSWERED, or are
   facts being told?
3. **<name>.md**: scene choices, reel selection, durations, Hinglish, colors.

Then it runs steps 3–5 itself. It reads `logs/LESSONS.md` + `logs/STATE.md`
at session start and logs every failure/fix — so it resumes across sessions
instead of repeating mistakes. Individual tasks also work: `run TASK plan
for lora`, `run TASK build for lora`, `run TASK retro`, etc.

## Workflow B — without Claude Code (deterministic steps 3–5 only)

Use this once the annotated `content/<name>/<name>.md` exists — e.g. you're
tweaking durations, LaTeX, or narration by hand and just want to re-render.
No LLM involved:

```
conda activate tmot
python main.py content/example/attention.md              # parse + generate + preview render
python main.py content/example/attention.md --final      # production quality
python main.py content/example/attention.md --no-render  # parse + generate only
python main.py content/example/attention.md --yt-only    # or --ig-only
python main.py content/example/attention.md --only=softmax_row  # partial re-render (see below)
```

Or run the three steps individually (same thing main.py chains):

```
python pipeline/blog_to_scenes.py content/example/attention.md
python pipeline/generate_scripts.py build/attention/scenes.json
python pipeline/render.py build/attention --preview
```

You can also write the scene-annotated .md entirely by hand (schema in
`PROMPTS.md`) and never touch an LLM — Workflow B is the whole pipeline then.
If something breaks, append what you learned to `logs/LESSONS.md` so agent
sessions benefit too.

### Reworking only specific scenes (partial re-render)

When only a few scenes are wrong, don't re-render the whole video. Fix the
scene block(s) in the .md, then pass their `id:`s to `--only`:

```
python main.py content/example/attention.md --only=softmax_row,attention_full
# or, skipping parse+generate:
python pipeline/render.py build/attention --preview --only=softmax_row,attention_full
```

What happens: manim runs ONLY for the listed scene ids (in both formats);
every other scene — and the branded intro/outro — is reused as-is from
`build/<name>/renders/`, and both final videos are re-stitched. A 1-scene
rework takes ~30s instead of minutes. Scene ids are the `id:` fields in the
.md (also visible in `build/<name>/scenes.json`; a wrong id prints the full
list). Combine with `--yt-only` / `--ig-only` to restitch just one cut, and
with `--final` (via main.py) for production quality.

Notes:
- `--only` needs one prior full render (it reuses those files; a missing
  reused scene aborts with a clear error).
- Keep the SAME quality mode as the existing renders (all `--preview` or all
  `--final`) so reused and fresh clips match.
- If you add/remove/rename scenes (ids change), do a full re-render after
  `rm -rf build/<name>` — stale scene files would otherwise get stitched in
  (see LESSONS L-6).
- Under the hood manim also caches unchanged animations, so even a full
  re-render is cheaper than it looks — `--only` just skips the per-scene
  manim startup entirely.

## Setup (WSL + conda — recommended)

Everything lives in a dedicated `tmot` env; nothing touches system Python:

```
conda env create -f environment.yml
conda activate tmot
python -c "import manim; print(manim.__version__)"   # sanity check
```

ffmpeg, cairo, pango, and LaTeX (texlive-core) all come from conda-forge
inside the env. If a render fails with a missing LaTeX package
(`standalone.cls` / `preview.sty` are the usual ones), either add it via
`tlmgr install standalone preview` or do the one-time system fallback:
`sudo apt install texlive texlive-latex-extra dvisvgm`.

Fonts (user-level, no sudo): CMU Serif/Sans (cm-unicode) and Noto Sans
Devanagari into `~/.local/share/fonts`, then `fc-cache -f`.

**Every pipeline command below assumes `conda activate tmot` first** (or
prefix with `conda run -n tmot`).

## Setup (Windows native, alternative)

```
pip install -r requirements.txt
# LaTeX: install MiKTeX (miktex.org). ffmpeg: winget install ffmpeg
# Fonts: CMU Serif/Sans (cm-unicode), Noto Sans Devanagari
```

Test render of a single scene, IG format:

```
set TMOT_FORMAT=instagram
manim -ql build/attention/scenes/02_attention_equation.py S02AttentionEquation
```

## Structure

```
config/channel.yaml      # brand, palette, fonts, formats, tags — edit here first
styles/tmot_style.py     # loads config, exposes colors + helpers
templates/base_scene.py  # TMOTScene: watermark, intro/outro, YT/IG layout
templates/scene_library.py  # scene archetypes (13+; add your own here)
pipeline/                # steps 3–5 (scripts)
main.py                  # one-command runner for steps 3–5 (Workflow B)
skills/visual-storytelling/  # SKILL.md — Question Ladder, Story Plan gate,
                         # Continuity Law (governs all writing in steps P–2)
content/                 # inbox/ (raw markitdown) + per-project source/plan/blog/annotated .md  [git-ignored]
CLAUDE.md + tasks.md     # Claude Code instructions + runnable tasks (Workflow A)
PROMPTS.md               # LLM prompts for steps 1–2
logs/                    # LESSONS.md (failure→fix log) + STATE.md (per-project checkpoint)
docs/AGENT_WORKFLOW.md   # Workflow A in detail
docs/CONFIGURATION.md    # what to edit for which change: .md vs templates vs
                         # channel.yaml, archetype catalog, new-archetype recipe
```

## Extending

New visual archetype = new class in `scene_library.py` + one entry in its
`SCENE_TYPES` dict + `CLASS_MAP` in `generate_scripts.py`. Keep archetypes
generic (parametrized by `spec`); one-off custom scenes can be hand-written
`.py` files dropped into `build/<name>/scenes/` — the renderer picks up
anything in that folder.

## India strategy — improvising over the base plan

**Language.** Hinglish narration with English on-screen text is the proven
sweet spot (it is what most large Indian STEM channels converge on): Hindi
sentence flow keeps it relatable, English technical terms keep it exam- and
industry-relevant, and English visuals keep the videos shareable outside
India too. Later, YouTube's multi-audio-track feature lets you add a pure
English track to the same video instead of re-uploading.

**Hook to exams and jobs.** Indian watch-intent clusters around JEE, GATE
(CS/DA), university syllabi, and ML job interviews. Map every abstract topic
to one of these in the title/description ("The matrix idea GATE keeps asking
about"). The `instagram_extra` tags in channel.yaml already include exam tags.

**Reels are your discovery engine.** In India, short-form is where new
audiences find you; YouTube long-form is where they stay. That's why the
pipeline forces you to mark `reel: true` scenes at *writing* time — the reel
is designed, not clipped as an afterthought. Keep reels 45–60s: hook (3s) →
one visual idea → punchline + follow CTA.

**Timing and cadence.** Post reels daily-ish if possible (the .md → video
pipeline makes short pieces cheap); long-form weekly/biweekly. Evening IST
(7–11 pm) and Sunday mornings perform well for study content.

**Data-light viewers.** Many viewers watch at 480p on mobile. The style
config uses thick strokes and large font sizes; resist dense screens — one
idea per scene (also a 3b1b principle).

**Local anchoring.** Open examples with Indian contexts — cricket run rates
for expected value, UPI fraud detection for classifiers, Mumbai local train
timetables for optimization. Costs nothing, doubles relatability.

**Monetization runway.** Indian CPMs are low; plan for course/mentorship
funnel (fits your Academy goal), channel memberships, and brand work with
ed-techs rather than AdSense alone.

## Notes

- Narration timing: `narration.md` gives planned timestamps; record VO per
  scene, then nudge `duration:` values and re-render (cheap at `-ql`).
- The `fit()` helper in `base_scene.py` is what makes one scene survive both
  aspect ratios; if a custom scene overflows on IG, wrap its root VGroup in
  `self.fit(...)`.
- Manim CE docs: https://docs.manim.community

## Q&A — from research paper to final animated .md (the authoring workflow)

### Q1. How do I create the very first markdown file?

You never write it by hand — you convert whatever you have:

```
conda activate markitdown         # or any env with markitdown
markitdown paper.pdf   > content/inbox/<name>.md    # a downloaded paper
markitdown https://arxiv.org/abs/1706.03762 > content/inbox/<name>.md
```

That inbox file is deliberately allowed to be messy (broken tables, page
artifacts, reference junk). **TASK ingest** (`run TASK ingest for <name>` in
Claude Code) cleans it into `content/<name>/source.md`: navigation junk and
references stripped, mangled LaTeX repaired, plus a header block (title,
authors, year, link, one-line summary). Facts should be verified against the
actual paper at this step — source.md is your ground truth for everything
downstream.

### Q2. Which skills turn it into the form the pipeline works with?

Three LLM steps (the only creative steps — 3–5 are deterministic scripts),
all governed by `skills/visual-storytelling/SKILL.md`:

1. **TASK plan** — the Question Ladder (SKILL.md Steps −2/−1): extract the
   paper's claims, convert each into curiosity questions (why / what's
   different / why required / what leads here / how realized / how fixed /
   what's missing / why impact), rank by the pause-test, keep a 5–9 question
   **spine**, and write `content/<name>/plan.md` — spine, beat sheet with
   every beat phrased AS its question, scene-by-scene answers/raises map,
   flow test. **This is the go/no-go gate: a bad flow stops here.**
2. **TASK blog** — applies `PROMPTS.md` **Step 1**: the post is written as
   the ANSWERS to the spine questions in the plan's order — hook = spine Q1,
   intuition → picture → formalism, spoken-word prose (it doubles as your
   narration), `[VISUAL: ...]` markers, honest limitations.
   Output: `content/<name>/blog.md`.
3. **TASK annotate** — applies `PROMPTS.md` **Step 2**: every visual moment
   becomes a fenced ```scene block (type from the archetype catalog,
   EN + Hinglish narration, durations, `reel:` flags), with each scene's
   `question:` field carrying the next spine question ON SCREEN.
   Output: `content/<name>/<name>.md` — the final file: blog, narration
   script, and animation plan in ONE artifact.

The skill's other laws still govern all writing: **nothing appears suddenly**
(carry_in/carry_out handoffs), **derive, don't declare** (every formula
earned), one **color registry** per video. Archetype catalog + spec fields:
`docs/CONFIGURATION.md`.

### Q3. My flow: I extract the key questions the paper answers, that becomes
### the voice, and with my feedback the .md becomes the final animation plan.
### Where does that fit?

Your key-questions step is now a first-class pipeline stage — **TASK plan**:

1. After **ingest**, run `TASK plan`: the Question Ladder interrogates
   `source.md` — claims are extracted, converted into curiosity questions
   ("why do dot products blow up with dimension?"), ranked by the pause-test,
   and chained into a 5–9 question spine in `content/<name>/plan.md`.
   Spine Q1 is your video hook; the ordering of the rest IS the video.
   You review this one-pager and approve (or restructure) — this is the
   cheapest possible place to fix direction, story, and impact.
2. **TASK blog** then writes the post AS the answers to the spine, in the
   plan's order — that's the "voice": the video is a conversation driven by
   your questions, not a summary of the paper's sections. Facts may only
   appear as answers to a question already on the table.
3. The scene schema carries the thread on screen: any scene block can take a
   `question: "..."` field — shown at scene end to set up the next scene.
   The plan's scene map (answers / raises columns) tells you exactly which
   question each scene carries, so the storytelling direction survives all
   the way into the render.
4. Your **feedback gates** are built into TASK full — it pauses three times:
   - after `plan.md` (**TASK plan**, the go/no-go gate): the Question Ladder
     turns the paper's claims into ranked curiosity questions; the story
     plan chains them. If the flow test fails, it stops HERE — nothing gets
     written, let alone rendered, on a bad flow.
   - after `blog.md`: judge voice, hook, whether questions are being
     answered (not facts told). Edit or redirect before any scene exists.
   - after `<name>.md`: judge scene choices, reel selection, durations,
     Hinglish register, color registry. This file is the complete animation
     plan — everything after it is deterministic rendering.

### Q4. Where do I quality-control each concern?

| Concern       | Artifact to review        | Lever if it's off |
|---------------|---------------------------|-------------------|
| Flow / conceptual progression | `plan.md` (spine + flow test) | restructure the spine at the plan gate — the ONLY acceptable place; a failed flow test is a no-go, nothing downstream runs |
| Facts         | `source.md` (vs the paper)| fix source.md, re-run plan/blog |
| Storytelling voice | `blog.md` vs the spine | rewrite at the blog gate — are questions answered, or facts told? |
| Direction     | `question:` chain + carry_in/carry_out in `<name>.md` vs plan's scene map | edit scene blocks; re-run parse to validate |
| Style         | `config/channel.yaml` (palette roles, fonts, background, shimmer) | one edit reskins every video |
| Scene quality | preview render frames     | edit that block, `python main.py … --only=<id>` (~30s/scene) |
| Recurring problems | `logs/LESSONS.md`    | log it once, never repeat it |

The economics: fixing the flow costs minutes at the plan gate, the voice an
hour at the blog gate, and anything after annotation a re-render — push your
judgment as early in the chain as possible. That is why TASK full stops and
waits for you at all three gates, and why steps 3–5 never improvise: what
you approved in the .md is exactly what renders. A scene that "shows
something true" but answers no live question is decoration; the plan gate
exists so decoration is cut on paper, never in a rendered video.
