# Agent workflow — how to drive this pipeline with Claude Code

## One-line usage

Drop any .md (e.g. `markitdown paper.pdf > content/inbox/lora.md`), open
Claude Code in this folder, and say:

> run TASK full for lora

Claude Code reads `CLAUDE.md` automatically, follows `tasks.md`, and pauses
for your approval after the blog draft and after scene annotation.

## The flow

```
content/inbox/<name>.md        ← anything markitdown can produce (PDF, arXiv, blog URL)
        │  TASK ingest  (clean, fix LaTeX, keep the substance)
content/<name>/source.md
        │  TASK plan    (Question Ladder → story plan; GO/NO-GO gate)
content/<name>/plan.md         ← question spine + beat sheet + scene map
        │  TASK blog    (PROMPTS.md step 1 — answers to the spine, in order)
content/<name>/blog.md         ← your blog post, publishable as-is
        │  TASK annotate (PROMPTS.md step 2 — ```scene blocks, EN+HI narration)
content/<name>/<name>.md       ← blog + script + animation spec in one file
        │  TASK build   (scripts: parse → generate → preview render)
build/<name>/                  ← scenes.json, scene .py files, narration.md,
                                 <name>_youtube.mp4, <name>_instagram.mp4
```

## Cross-session memory (logs/)

Things WILL break and refine over time. Two files make that cumulative
instead of circular:

- **`logs/LESSONS.md`** — append-only log of every failure, cause, fix, and
  the rule that prevents it. Agents must read it at session start and write
  to it before fixing anything. Over time this becomes the pipeline's real
  documentation.
- **`logs/STATE.md`** — per-project checkpoint (last completed step, next
  action). Any session, any machine: resume from here instead of restarting.

If an agent misbehaves, the correction you give it belongs in LESSONS.md —
say "log that" and it becomes permanent.

## Approval gates

TASK full pauses three times, earliest is cheapest:
1. after `plan.md` — the GO/NO-GO gate: is the question spine genuinely
   curiosity-driven, does each answer expose the next question? A bad flow
   stops here; scenes executed on a bad flow have no impact.
2. after `blog.md` — editorial voice check (are the questions being
   ANSWERED, or are facts being told?).
3. after `<name>.md` — scene choices, reel selection, Hinglish quality.
Everything downstream is deterministic scripts, so these reviews are where
your judgment matters most.
