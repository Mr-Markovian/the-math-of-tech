# tasks.md — runnable tasks for Claude Code

Invoke as: "run TASK <n> for <name>" (e.g. "run TASK full for attention").
Every task starts by reading `logs/LESSONS.md` + `logs/STATE.md` and ends by
updating them (see CLAUDE.md session protocol).

**All commands run inside the `tmot` conda env** — `conda activate tmot`
first, or prefix with `conda run -n tmot` (see CLAUDE.md Environment).

---

## TASK ingest — raw .md → clean source + equation registry
**Input:** `content/inbox/<name>.md`. PREFER creating it with
`python pipeline/ingest.py <arxiv-id-or-url> --name <name>` — it fetches the
actual LaTeX (arXiv e-print source, or TeX embedded in blog/ar5iv HTML) so
math survives verbatim. markitdown on a PDF is the LAST resort: a PDF stores
glyphs, not LaTeX, so math arrives mangled — reconstruct with extra care.
**Do:**
1. Read the file. Strip navigation junk, references section, author affiliations, page artifacts (if fetched via the ar5iv fallback, also strip `\hspace{0pt}` noise inside equations).
2. Keep: abstract, core method sections, key equations (fix any mangled LaTeX), results tables that matter, limitations.
3. Write cleaned version to `content/<name>/source.md` with a header block: title, authors, year, link/DOI, one-line summary.
4. Write `content/<name>/equations.md` — the EQUATION REGISTRY: every equation the video could plausibly need, numbered (E1, E2, …), in verified LaTeX (single backslashes — it's markdown, not YAML), each checked against the paper (ar5iv view). Downstream steps COPY equations from this registry — never re-derive LaTeX from memory.
**Done when:** source.md reads as coherent standalone text with valid LaTeX AND equations.md lists every key equation, verified against the paper.

## TASK plan — source → story plan (question ladder, GO/NO-GO gate)
**Input:** `content/<name>/source.md`
**Do:** Apply `skills/visual-storytelling/SKILL.md` Steps −2 and −1: extract the paper's claims, convert them to curiosity questions (taxonomy table), rank by curiosity, select the 5–9 question spine, write the beat sheet with every beat phrased AS its question, and the scene-by-scene map (answers / raises / archetype / carry object). Run the flow test. Write `content/<name>/plan.md`.
**Done when:** plan.md passes the flow test AND Roy has approved it. **A failed flow test is a NO-GO: restructure the spine — do not proceed to blog.** This gate exists because scenes executed on a bad flow have no impact and waste every downstream hour.

## TASK blog — plan + source → blog post
**Input:** `content/<name>/plan.md` (approved) + `content/<name>/source.md`
**Do:** Apply PROMPTS.md **Step 1** exactly. Write `content/<name>/blog.md` as the ANSWERS to the plan's spine questions, in the plan's order (900–1400 words, hook = spine Q1, intuition → picture → formalism, `[VISUAL: ...]` markers, honest limitations).
**Done when:** blog.md exists, reads aloud naturally, has ≥4 [VISUAL] markers, and every spine question is answered in order.

## TASK annotate — blog → scene-annotated md
**Input:** `content/<name>/blog.md`
**Do:** Apply PROMPTS.md **Step 2** exactly. Write `content/<name>/<name>.md` — same prose, with ```scene YAML blocks replacing/augmenting [VISUAL] markers. Both narration languages, 4–7 `reel: true` scenes, durations summing to 480–900s (YouTube) with reel subset 45–90s.
**Done when:** `python pipeline/blog_to_scenes.py content/<name>/<name>.md` exits OK **and** `python pipeline/check_tex.py content/<name>/<name>.md` reports all strings compile (every tex copied from `equations.md`, per PROMPTS.md step 2 rules).

## TASK build — parse + generate + preview render
**Input:** `content/<name>/<name>.md`
**Do:**
```
python pipeline/blog_to_scenes.py content/<name>/<name>.md
python pipeline/check_tex.py build/<name>/scenes.json
python pipeline/generate_scripts.py build/<name>/scenes.json
python pipeline/render.py build/<name> --preview
```
Read stdout of each before running the next. On failure: log to LESSONS.md, fix the *source* (md or templates, not generated files), retry.
**Done when:** `build/<name>/<name>_youtube.mp4` and `_instagram.mp4` exist.

## TASK final — production render
**Do:** `python pipeline/render.py build/<name>` (no --preview). Then report file paths, total durations, and the narration script location.

## TASK full — everything
**Do:** TASK ingest → **plan (STOP for approval — go/no-go)** → blog (pause for approval) → annotate (pause for approval) → build. Three gates, earliest is cheapest: a flow fix at the plan gate costs minutes; the same fix after build costs a re-render.

## TASK retro — log maintenance
**Do:** Review this session's errors/corrections. Append anything unlogged to `logs/LESSONS.md`; deduplicate/merge stale entries; update `logs/STATE.md`.
