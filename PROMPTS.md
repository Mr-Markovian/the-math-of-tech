# LLM prompts — the_math_of_tech pipeline (Steps 1 & 2)

Steps 1–2 are LLM-driven (use Claude/Cowork); steps 3–5 are the Python scripts.

> **REQUIRED READING for steps 1–2:** `skills/visual-storytelling/SKILL.md`
> — the visual-storytelling rules (beat sheet before scenes, the Continuity
> Law "nothing appears suddenly", carry_in/carry_out handoffs, color registry,
> pre-parse checklist). Both prompts below are executed UNDER those rules;
> run its pre-parse checklist before step 3.

---

## Step 0 — Source → story plan (RUNS FIRST; go/no-go gate)

> Read content/<name>/source.md. Do NOT summarize it — interrogate it, per
> SKILL.md Steps −2/−1 (Question Ladder + Story Plan):
> 1. List the 8–15 concrete claims the paper establishes.
> 2. Convert each claim into curiosity questions using the taxonomy (why /
>    what's different / why required / what leads here / how realized /
>    how fixed / what's missing / why more important / why impact).
> 3. Rank by the pause-test ("would a smart viewer pause wanting the
>    answer?"); keep a 5–9 question spine, ordered so each answer exposes
>    the next question.
> 4. Write content/<name>/plan.md: spine, beat sheet (every beat AS its
>    question), scene-by-scene map (answers / raises / archetype / carry),
>    flow test checked.
> STOP after writing plan.md and wait for approval. A failed flow test =
> restructure; never continue to Step 1 on a bad flow.

## Step 1 — Approved plan + source → blog post

> You are writing for **the_math_of_tech**, a 3blue1brown-style channel for an
> Indian audience (undergrads, JEE/GATE aspirants, early ML engineers).
>
> Input: content/<name>/plan.md (approved) + content/<name>/source.md
>
> Write a blog post in markdown that:
> 0. Is structured as the ANSWERS to the plan's spine questions, in the
>    plan's order — the reader should feel questions being answered, never
>    facts being listed. Raise each next question before answering it.
> 1. Opens with a **hook** — spine question Q1, concrete and surprising
>    (first 3 seconds decide retention).
> 2. Builds ONE core idea from intuition → picture → formalism, in that order.
>    Never introduce a symbol before the intuition for it.
> 3. Uses inline LaTeX ($...$) for all math; display math in $$...$$.
> 4. Keeps prose spoken-word friendly — it doubles as the narration script.
> 5. Flags [VISUAL: ...] wherever a picture would replace a paragraph.
> 6. States honestly what the paper does NOT show (limitations).
> 7. Length: 900–1400 words (≈ 8–12 min video).

## Step 2 — Blog → scene-annotated .md (the pipeline input format)

> Take the blog post below. For every [VISUAL: ...] marker (and anywhere else
> a visual is essential), insert a fenced ```scene block choosing from these
> types: `concept_title`, `equation_reveal`, `equation_annotated`,
> `equation_steps`, `transform`, `graph`, `neural_net`, `attention_matrix`,
> `matrix_multiply`, `softmax_build`, `multi_head`, `bullet_points`.
> For any DERIVATION (a chain of equations in one logical progression),
> use `equation_steps` — the chain morphs step into step, never pops.
>
> Rules:
> - Every scene needs `type`, `id` (snake_case, unique), `duration` (seconds),
>   `narration_en`, and `narration_hi` (Hinglish: Hindi sentence structure,
>   English technical terms — e.g. "Gradient descent har step pe loss ko
>   thoda kam karta hai").
> - LaTeX in `tex:` fields must double-escape backslashes for YAML.
> - Mark `reel: true` on the 4–7 scenes that form a self-contained 45–90s
>   story: hook → one equation/visual → punchline. A reel must make sense
>   with zero context.
> - Total YouTube runtime: sum of durations ≈ 480–900s.
> - Prefer `transform` over two separate `equation_reveal`s when equation B
>   derives from equation A — motion carries the meaning.

## Scene block schema (reference)

```
type: equation_reveal | concept_title | equation_annotated | equation_steps | transform | graph | graph_morph | tokens_to_vectors | neural_net | attention_matrix | matrix_multiply | softmax_build | multi_head | bullet_points
id: unique_snake_case
title: "on-screen title (optional)"
question: "curiosity question SHOWN at scene end, sets up the next scene (optional — any type)"
duration: 10
reel: true|false
narration_en: "..."
narration_hi: "..."
# type-specific fields:
#   equation_reveal: tex: [list], highlight: index
#   equation_steps:  steps: [list of latex, morphed in order],
#                    labels: [move names, "" to skip], anchor: latex (dimmed
#                    general form on top), color_map: {tex_substring: color},
#                    isolate: [extra substrings for match tracking]
#                    NOTE: shared subexpressions must be byte-identical
#                    between consecutive steps or matching breaks.
#   transform:       tex_from, tex_to
#   tokens_to_vectors: text (sentence), max_toks, seed, decimals,
#                    show_matrix — text splits into tokens, each becomes a
#                    random-direction spin vector, spins stack into matrix X
#   graph:           function ("np.sin(x)"), x_range, y_range, label
#   graph_morph:     functions: [list of exprs, morphed in order on
#                    persistent axes], labels: [latex per stage],
#                    captions: [move names], colors: [per stage],
#                    x_range, y_range, fill: true|false (shade area —
#                    use for probability: constant area IS the point)
#   neural_net:      layers: [3,5,2]
#   attention_matrix: tokens: [list of strings]
#   matrix_multiply: a, b (2D lists), a_label, b_label, c_label, decimals,
#                    highlight_row
#   softmax_build:   scores: [list], labels: [list], decimals
#   multi_head:      n_heads: int
#   bullet_points:   points: [list of strings]
```
