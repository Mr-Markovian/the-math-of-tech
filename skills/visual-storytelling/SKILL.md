---
name: visual-storytelling
description: Turn math/AI explainer videos into visual stories with step-by-step pedagogical continuity AND real mathematical depth, for the manim-pipeline (the_math_of_tech). Use this skill whenever Roy asks to write a video, blog post, script, storyboard, scene annotation, reel, or explainer; whenever running pipeline steps 1-2 (blog writing or scene annotation); whenever converting a paper into scenes; or whenever he says animations feel like "moving elements" instead of a story, or too shallow. It enforces two laws - nothing appears on screen suddenly, and derive-don't-declare (every formula earned, every constant explained) - plus narrative structure and scene-to-scene handoffs.
---

# Visual Storytelling — pedagogical continuity for the_math_of_tech

## The problem this skill solves

A pipeline can render beautiful scenes that still feel like a slideshow: elements
fade in, move, fade out — but nothing *follows from* anything. A good explainer
feels like one continuous thought unfolding. The viewer should never wonder
"where did that come from?" — every object on screen should feel *inevitable*,
because the story demanded it one beat earlier.

This skill applies to pipeline Steps 1–2 (blog writing and scene annotation in
`manim-pipeline/`, per PROMPTS.md). Steps 3–5 render whatever you wrote — so
storytelling quality is decided entirely here, at writing time.

**The failure mode this file exists to prevent: telling facts.** A video that
states true things in a sensible order is still not a story. A story is a
chain of live questions — each scene ANSWERS the question currently on the
table and RAISES the next one. If no question is open, whatever appears next
is a fact, and facts don't carry viewers across cuts. Hence the two stages
below, which come BEFORE any writing: interrogate the source (Question
Ladder), then plan the flow and get it approved (Story Plan gate). Writing
scenes on top of a bad flow wastes every downstream hour — a wrong flow is a
no-go, not a note.

## Step −2 — The Question Ladder: interrogate the source before writing

Never summarize `source.md` — interrogate it. Three passes:

1. **Extract the claims.** List the 8–15 concrete things the paper actually
   establishes (results, design choices, constants, failure modes). One line
   each, with a pointer into source.md.
2. **Convert every claim into curiosity questions.** A claim is an answer
   wearing a disguise; recover the question(s) it answers. Use the taxonomy —
   each row is a different story role:

   | Question form | Story role |
   |---|---|
   | *Why…? Why does this matter? Why could this impact…?* | stakes / payoff |
   | *What is different here? What did everyone do before?* | novelty, context |
   | *Why was this required? What breaks without it?* | necessity — earns every constant |
   | *What leads us here?* | history/setup — the naive idea |
   | *How can this be realized? How do we solve this?* | mechanism — the derivation |
   | *How could this be fixed?* | the turn — insight as repair |
   | *What is still missing?* | honesty beat / sequel hook |
   | *Why is this more important than the alternative?* | comparison, judgment |

   A claim usually yields 2–3 questions of different forms; write them all.
3. **Rank by curiosity, not by importance.** The test for each question:
   *would a smart viewer who just heard it pause the video wanting the
   answer?* Discard questions only an author finds interesting ("what
   section does this appear in") and questions whose answer is a definition.
   Keep 5–9 — these are the **spine**. Order them so each answer naturally
   exposes the next question (necessity → mechanism → repair → impact is the
   usual gradient). That ordering IS the video.

## Step −1 — The Story Plan: plan before execution (go/no-go gate)

Write `content/<name>/plan.md` BEFORE the blog and BEFORE any scene block:

```
# STORY PLAN — <name>
## Spine (ranked curiosity questions, in narrative order)
Q1 …   Q2 …   (5–9 questions from the ladder)
## Beat sheet (every beat phrased AS its question)
1. QUESTION → Q1 verbatim (the hook)
2. STAKES   → why-it-matters question …
   … (the 8 beats, each mapped to a spine question)
## Scene-by-scene map
scene_id | answers (which Q) | raises (which Q) | archetype | carry object
## Flow test (all must pass — any failure = STOP and restructure)
[ ] every scene answers a question already on the table (no orphan answers)
[ ] every scene except the last raises the next question
[ ] no scene exists only to state a fact (cut it or find its question)
[ ] removing any scene breaks the chain (if not, it's decoration)
[ ] the reel subset alone still forms a question→answer→question chain
```

**The gate:** the plan is reviewed (by Roy) before TASK blog runs. If the
flow test fails, STOP — restructure the spine; do not write the blog, do not
annotate, do not render. Everything downstream (blog → scenes → render) is
execution of this plan; a flaw here multiplies into hours there. The blog is
then written as the answers to the spine questions in order, and every
beat-driving question goes ON SCREEN via `question:` fields — so the plan
survives verbatim into the final render.

## Step 0 — Write the beat sheet BEFORE any scene blocks

Never annotate scenes directly from a blog. First write a beat sheet at the top
of the annotated .md (as an HTML comment so the parser ignores it):

```
<!-- BEAT SHEET
1. QUESTION   what puzzle opens the video? (this is the hook)
2. STAKES     why should the viewer care before any math appears?
3. FIRST IDEA the naive/intuitive attempt (it should almost work)
4. TENSION    where the naive idea breaks — make the viewer feel the gap
5. TURN       the key insight, stated in one sentence
6. FORMALISM  the equation, earned piece by piece
7. PAYOFF     the opening question answered with the new machinery
8. CALLBACK   reuse the opening image/example one final time
-->
```

Every scene must serve exactly one beat. If a scene doesn't advance the beat
sheet, cut it — a scene that "shows something cool" but answers no live
question is decoration, not story.

## The Continuity Law: nothing appears suddenly

Every new visual object must enter through one of four legal doors:

1. **Transformation** — it morphs from an object already on screen
   (`transform` archetype; `TransformMatchingTex` carries meaning through
   motion). Prefer this above all others: A becoming B *is* the explanation.
2. **Foreshadowing** — narration names it 1–2 seconds before it appears
   ("...and that weight? watch —" → weight appears). Sound leads sight.
3. **Assembly** — it is built from parts already on screen (equation assembled
   term by term, each term pointed at the picture it came from).
4. **Established context** — it arrives through the scene's existing spatial
   logic (the pipeline's depth-stage: objects arrive from depth via
   `shift=OUT`, recede at scene end — an arrival the viewer already expects).

If an object can't enter through any of these doors, the *story* is missing a
step — fix the narrative, don't just pick a prettier fade.

The same law applies to exits: objects leave because the story is done with
them (absorbed into the next object, receded to the background), not because
the screen needed space.

## Scene handoffs — the carry object

Scenes are rendered separately and hard-cut together, so continuity must be
authored. Rule: **the first thing seen in scene N+1 is something remembered
from scene N** — same concept, same color, same visual form.

Annotate every scene block with carry comments (YAML comments — the parser
ignores them, but they force you to design the handoff):

```yaml
# carry_in: the yellow score bars from softmax_row (same 3 bars, same order)
# carry_out: normalized green bars -> become the attention row in next scene
```

If you cannot write a truthful `carry_in` for a scene, you have a hard cut in
the story — insert a bridging beat or restructure.

## Chain-of-thought pedagogy — the fixed ordering

Within any concept, this order is non-negotiable, because each stage creates
the *need* for the next:

**question → intuition → picture → name/symbol → formula → consequence**

Concretely:
- No symbol before its referent. The viewer must SEE the thing (bars, arrows,
  a matrix row) before the letter that names it appears. "This spread of
  scores" (picture) → "call it $x$" (symbol) → formula using $x$.
- Equations are earned, never dropped. Build with `equation_annotated` parts
  or successive `transform`s; each new term gets one sentence of narration
  explaining why the previous form was insufficient.
- One idea per scene stays law — but the idea must be a *step in an argument*,
  answering the question the previous scene raised, and raising the next one.
- **Questions are content — SHOW them.** A curiosity question the viewer only
  hears is half a question. Every beat-driving question goes ON SCREEN: use
  the scene's `question:` field (rendered at scene end, just before the
  content recedes — the pipeline supports this on every scene type) and
  phrase `concept_title` cards as questions. The visible question is what
  carries a viewer across the cut to the next scene; it's also what makes a
  paused screenshot shareable.
- End scenes on questions where possible. "So the scores explode — how do we
  tame them?" is a scene ending; "these are the scores" is not.

## Clutter budget — one bright thing at a time

Depth needs room. Keep at most ~3 live elements on screen, only ONE of them
bright: when a new element enters, its predecessor dims (opacity ~0.35) or is
absorbed into the newcomer — dimming says "still relevant, not the focus";
absorption says "this became that". Never leave an element at full
brightness after its moment has passed. Abstraction pipelines are the model:
text dims when its vectors appear; vectors are absorbed when the matrix
forms. Each abstraction level visibly *becomes* the next (that's the
Continuity Law), and only the current level holds the eye.

## Mathematical depth — derive, don't declare

Depth is what separates this channel from equation-flashing content. A formula
shown is a fact; a formula *derived* is a story. Depth and storytelling are the
same discipline: a derivation IS the Continuity Law applied to algebra — each
line enters by transformation from the previous line.

- **At least one genuine derivation per video** (2–4 lines). Use successive
  `transform`s or an `equation_reveal` sequence where each line follows from
  the last by one named move ("expand the sum", "take the variance"). If the
  video contains zero derivations, it is a summary, not an explainer.
- **Every constant is earned.** If an expression contains a scale factor,
  normalizer, or bound (√d_k, 1/n, a log), either derive where it comes from
  or show what breaks without it — ideally both (derivation + failure graph).
  "It stabilizes training" is a caption, not an explanation.
- **State the assumptions when you use them.** Derivations rest on premises
  (independent components, mean 0, variance 1). Put them on screen at the
  moment they're invoked — this is what separates rigor from ritual, and it's
  exactly what the source paper does in its footnotes.
- **Dimension honesty.** Give every matrix/vector its shape at first
  appearance (X ∈ R^{n×d_model}, W^Q ∈ R^{d_model×d_k}) and walk one shape
  check on screen at least once per video. Shapes are where beginners get
  lost and where experts test whether you actually know the material.
- **Worked numbers over abstract symbols — but never a toy that hides the
  phenomenon.** Pick the SMALLEST example in which the interesting behavior
  actually occurs, not the smallest example that parses. If the effect you're
  explaining depends on scale (variance growing with dimension, saturation,
  accumulation), a 2-D example *demonstrates the mechanics but cannot show
  the effect* — either size the example so the phenomenon visibly appears,
  or explicitly run the toy AND the real scale side by side and let the
  contrast be the point. A good example worked step by step beats a basic
  example worked completely. Verify every number you put on screen (compute
  it, don't estimate it) — real numbers are falsifiable; that's the
  channel's credibility.
- **Two tracks, no dumbing down.** Keep the general symbolic form on screen
  (dimmed, top of frame) while the concrete instance evaluates beneath it,
  step by step. The instance makes it graspable; the general form makes it
  honest. Show every step that changes *structure* (a substitution, a bound,
  an interchange of sum and expectation); compress only mechanical
  arithmetic a competent student would do in their head. Skipping a
  structural step is dumbing down; skipping 3×4=12 is pacing.
- **Fidelity to the source.** When building from a paper, verify each
  equation against the paper itself (fetch it; don't trust memory). Use the
  paper's exact hyperparameters (d_model=512-style specifics) — concrete
  numbers are free depth.
- **Depth ≠ clutter.** Depth comes from the length of the derivation chain,
  not the number of symbols per screen. One idea per scene still governs;
  a deep video is a LONGER chain of SMALL steps, never a denser screen.

## Symbol identity and equation choreography

Symbols are characters; equations are their scenes. Treat both with the same
continuity discipline as everything else on screen.

**A repeated symbol is one object, seen in many places.**
- First occurrence = the symbol's introduction (Continuity Law applies:
  picture before name). Every LATER occurrence must be visually descended
  from an existing one: animate a copy branching out from the live symbol to
  its new location (`TransformFromCopy` in Manim terms), in its registry
  color — never retype it as if it were new. The viewer should *see* that
  the d_k in the denominator is the same d_k from the variance line.
- When one symbol appears in several places at once (x in the numerator AND
  inside the sum), discussing it means highlighting ALL occurrences together
  — they pulse as one entity. If occurrences can't be highlighted
  consistently, the color registry has been violated somewhere upstream.
- Branching is a storytelling beat, not decoration: a symbol flowing from
  the general equation into a worked instance, or from a derivation line
  into the final formula, is exactly the "chain of thought made visible."

**Equations in the same logical chain morph or move — they never pop.**
- If equation B derives from, instantiates, or restructures equation A, then
  A must transform into B on screen (`TransformMatchingTex`) or physically
  slide aside while B grows out of it. A structurally-related equation
  appearing from nothing is a continuity violation, same as any object.
- Motion carries meaning — choose it semantically: a term *sliding across*
  the equals sign is algebra; a subexpression *shrinking into* a named
  symbol is abstraction; a symbol *expanding into* its definition is the
  reverse; fading is removal and means "the story is done with this."
  Random repositioning between steps says nothing and costs attention.
- A fresh equation may pop in (via the four doors) only when a NEW logical
  chain begins — i.e., at a new beat of the beat sheet, foreshadowed by
  narration.
- Practical Manim note: `TransformMatchingTex` tracks *identical tex
  substrings*. So author the .md deliberately — keep shared parts
  byte-identical between `tex_from`/`tex_to` (and across `tex:` list lines),
  and split `parts:` at the same boundaries the choreography needs. Matching
  is designed at writing time, not fixed at render time.
- If the choreography an idea needs can't be expressed by existing
  archetypes, extend `scene_library.py` or drop a hand-written scene into
  `build/<name>/scenes/` (see README "Extending") — do not downgrade the
  storytelling to fit the current template set.

## Color is identity

A concept keeps one color for the entire video. Declare the mapping in a
comment at the top of the annotated .md and never violate it:

```
<!-- COLOR REGISTRY: Q=blue  K=yellow  V=green  scores=red  output=purple -->
```

When a concept transforms (scores → probabilities), the color change IS the
event — animate it and let narration call it out. Random recoloring between
scenes silently destroys the viewer's mental model.

## Narration–visual lockstep

Narration and screen must move together — in both `narration_en` and
`narration_hi`:
- Never narrate what isn't on screen; never show what narration hasn't
  motivated (foreshadowing is the one legal exception, by design).
- Micro-pattern per reveal: **say → show → say again** (name what's coming,
  show it, then restate what it means now that it's visible).
- Write narration with explicit connective tissue: "so", "which means",
  "but notice", "remember the bars from before" — these words are the
  chain-of-thought made audible. A narration line that could be reordered
  without anyone noticing is a list, not a story.

## Archetype guidance (scene_library.py)

- `equation_steps` is the derivation workhorse: a chain of equations that
  MORPH step into step (TransformMatchingTex), with `anchor:` holding the
  dimmed general form/assumptions on top (two-track rule), `labels:` naming
  each move, and `color_map:` keeping symbol colors consistent across the
  whole chain (symbol identity). Use it for ANY derivation of 2+ steps;
  remember shared subexpressions must be byte-identical between steps.
- Prefer `transform` over two `equation_reveal`s whenever B derives from A
  in a single move; use `equation_steps` when there's more than one move.
- `graph_morph` is `equation_steps` for curves: functions morph in sequence
  on PERSISTENT axes (the axes are the carry object). Use it whenever a
  curve *changes* as part of the story — a distribution shifting or
  sharpening (prior→posterior, Gaussian widening with d_k), a potential
  deforming, a payoff curve under a new parameter. `fill: true` shades the
  area — for probability stories the invariant area IS the argument. A
  sequence of separate `graph` scenes for the same evolving curve is a
  continuity violation.
- The Continuity Law covers plots exactly as it covers equations: same
  quantity ⇒ same axes and same color across stages; a new curve pops in
  only at a new beat.
- `tokens_to_vectors` shows the text→numbers abstraction pipeline: a
  sentence splits into tokens, each token grows a tiny random-direction
  "spin" vector (the honest picture of an embedding at initialization),
  and the spins stack into the matrix X. Use it whenever raw input
  (paragraph, sentence) must become vectors/matrices — showing the
  abstraction beats asserting it. Fix `seed:` per video so re-renders are
  identical.
- `concept_title` cards pose the beat's QUESTION ("Why doesn't this
  explode?"), never a label ("Scaling"). A label is a hard cut in disguise.
- `bullet_points` is a last resort; if used, each point must still enter via
  foreshadowing in narration. Never open or close a video with it.
- `equation_annotated` exists so every part of a formula can be pointed at —
  use `callout_idx`/`callout_text` to tie the scariest term back to its
  picture.
- Reel scenes (`reel: true`) need the full arc in miniature: the 4–7 marked
  scenes must contain their own question, turn, and payoff, with carry
  objects intact when scenes between them are dropped from the IG cut. Check
  the reel subsequence separately: read ONLY the reel scenes in order and
  verify the Continuity Law still holds.

## Pre-parse checklist

Run this before `blog_to_scenes.py` (step 3). Any "no" means rewrite:

1. Beat sheet present; every scene maps to exactly one beat?
2. Every scene has truthful `# carry_in` / `# carry_out` comments?
3. Every new object enters via one of the four doors?
4. No symbol appears before its picture?
5. Color registry declared and never violated?
6. Every scene (except the last) ends raising the next scene's question?
7. Opening image/example returns as the callback near the end?
8. Reel subsequence read alone: still a complete, continuous story?
9. Narration (EN and HI) contains connective tissue, not reorderable facts?
10. Nothing on screen the narration ignores; nothing narrated that's unseen?
11. At least one genuine derivation, with its assumptions shown on screen?
12. Every constant earned (derived or failure-shown)? Shapes stated at first
    appearance? All worked numbers actually computed and correct?
13. Is the example the smallest one where the phenomenon actually SHOWS
    (not just the smallest that parses)? General form kept on screen while
    the instance runs?
14. Every repeated symbol visually branched from an earlier occurrence
    (never retyped)? Equations in one logical chain morph/move into each
    other (never pop)? Shared tex substrings byte-identical so matching
    works?
15. Every beat-driving question SHOWN on screen (`question:` field or a
    question-phrased title), not just narrated? Clutter budget respected —
    one bright element, predecessors dimmed or absorbed?
16. Story plan exists (`plan.md`), was approved BEFORE writing, and every
    scene still maps to its "answers / raises" row? No scene answers a
    question that was never raised (no orphan answers, no fact-scenes)?

## Worked micro-example (bad → good)

**Bad** (sequential elements, no story):
1. `concept_title` "Softmax" → 2. `equation_reveal` softmax formula →
3. `softmax_build` bars → 4. `bullet_points` "properties of softmax"

**Good** (same content as one thought):
1. `concept_title` — "How do you turn scores into beliefs?"
   (`# carry_out: three raw score bars appear under the question`)
2. `softmax_build` — bars first (picture), narration: "big scores should win,
   but gently — watch what exponentiating does" (intuition before formula)
   (`# carry_in: the three bars` / `# carry_out: green normalized bars, sum=1`)
3. `equation_annotated` — formula assembled ABOVE the green bars; each part
   (e^x, the sum) gets a callout to the bar behavior it caused
   (`# carry_in: green bars remain below` / `# carry_out: boxed formula`)
4. `transform` — boxed softmax morphs into the attention equation, answering
   "so where does this live in a transformer?" — the next video's hook.

Same archetypes, same renderer — the difference is entirely in entrances,
handoffs, and the question each scene leaves open.
