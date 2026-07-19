# CLAUDE.md — the_math_of_tech animation pipeline

You are operating the video pipeline for the channel **the_math_of_tech**
(3blue1brown-style math/AI explainers, Indian audience, English visuals +
Hinglish narration). Tasks are defined in `tasks.md`. Style rules and prompt
templates are in `PROMPTS.md`. Human docs: `README.md`, `docs/AGENT_WORKFLOW.md`.
Edit-surface map (what to change where: .md vs scene_library vs channel.yaml,
archetype catalog, partial re-render loop): `docs/CONFIGURATION.md`.

## Environment — non-negotiable

ALL python/manim commands run inside the conda env **`tmot`**
(created from `environment.yml`). Never install into or run with system
Python. Before the first command of any session:

```
conda activate tmot        # or prefix every command with: conda run -n tmot
```

If the env is missing: `conda env create -f environment.yml`. If a package
is missing, add it to `environment.yml` and `conda env update -f
environment.yml --prune` — never bare `pip install` outside the env.

## Session protocol — ALWAYS do this first

1. **Read `logs/LESSONS.md` before doing anything else.** It contains known
   failure modes, fixes, and where previous sessions stopped. Never repeat a
   mistake that is already logged.
2. Check `logs/STATE.md` for in-progress projects and resume from the recorded
   step rather than restarting.

## Session protocol — ALWAYS do this last (and on every failure)

- On ANY error, broken render, wrong output, or user correction: append an
  entry to `logs/LESSONS.md` (format defined at the top of that file) BEFORE
  attempting the fix, then update the entry with the fix once found.
- Before ending a session: update `logs/STATE.md` with project name, last
  completed step (1–5), and next action.
- These logs are the shared memory across all sessions. Skipping them is the
  one unforgivable mistake.

## Pipeline (5 steps, per project)

```
00. Fetch   python pipeline/ingest.py <arxiv-id|url> --name <name>
            (math-faithful .md into content/inbox/ — prefer this over
            markitdown for arXiv papers and math blogs; PDF = last resort)
0. Ingest   content/inbox/<name>.md → source.md + equations.md (registry)
1. Blog     → content/<name>/blog.md            (LLM: PROMPTS.md step 1)
2. Annotate → content/<name>/<name>.md          (LLM: PROMPTS.md step 2 — scene blocks)
3. Parse    python pipeline/blog_to_scenes.py content/<name>/<name>.md
3.5 TexChk  python pipeline/check_tex.py build/<name>/scenes.json
            (compiles every tex: in isolation — main.py runs it automatically)
4. Generate python pipeline/generate_scripts.py build/<name>/scenes.json
5. Render   python pipeline/render.py build/<name> --preview
```

Steps 1–2 are YOUR job (writing, per PROMPTS.md). Steps 3–5 are scripts —
run them, read their output, fix inputs if they fail.

For steps 1–2, ALSO read and follow `skills/visual-storytelling/SKILL.md`
(beat sheet first, Continuity Law — nothing appears suddenly, carry_in/
carry_out scene handoffs, color registry, pre-parse checklist). A build that
passes parsing but fails that checklist is not done.

## Hard rules

- On-screen text: English only. Narration fields: `narration_en` AND
  `narration_hi` (Hinglish) always both present.
- LaTeX inside YAML `tex:` fields needs double-escaped backslashes.
- Scene `id`s: unique snake_case. Mark 4–7 scenes `reel: true` forming a
  self-contained 45–90s story.
- Never edit generated files in `build/*/scenes/` to fix systematic problems —
  fix `templates/scene_library.py` or the source .md, then regenerate.
- Branding/colors/tags: edit only `config/channel.yaml`.
- Verify each script step succeeded (read stdout) before starting the next.
- LaTeX in scene blocks is COPIED from `content/<name>/equations.md` (built
  by TASK ingest, verified against the paper) — never re-typed from memory.
- If a render fails on LaTeX, test the offending `tex:` string in isolation
  first — `python pipeline/check_tex.py --tex '<string>'` — and log the
  pattern in LESSONS.md. (Step 3.5 should have caught it; if it didn't,
  extend `latex_jobs()` in check_tex.py for that field.)
