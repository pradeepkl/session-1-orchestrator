# Narrative Voice Directive — Problem-First Explanatory Style

## Status and relationship to other style documents

This file does not replace or override `style-guide.md` or `tone-reference.md`.
It sits alongside them and governs one specific dimension neither of them
makes explicit: **the causal shape of explanatory prose** — the order in
which a concept, its motivating problem, and its trade-offs are introduced.

`style-guide.md` governs mechanics: sentence length, prohibited words,
transitions, formatting. `tone-reference.md` demonstrates voice by example
(Chapter 1) without stating the mechanism behind it. This document states
that mechanism directly, so it can be applied deliberately to any chapter —
during first drafting or during a later editing pass — rather than
rediscovered by imitation each time.

Apply this directive to **connective prose only**: introductions,
transitions between sections, explanations that surround a listing, and
section or chapter conclusions. It never applies to listings, listing
titles, code, headings, or the technical content and decision hierarchy of
a chapter — those are fixed by the chapter's own planning documents and are
out of scope for a tone pass governed by this file.

---

## The core instruction

A reader should feel they are **following an argument**, not **walking
through a checklist**. Every tool, class, or technique earns its
introduction because something that came immediately before it was
insufficient — not because a table of contents says it comes next.

The test for any paragraph introducing a new concept: does the previous
sentence create a problem that this concept is the answer to? If the
concept could be swapped for a different one without any surrounding
sentence needing to change, the paragraph is taxonomy, not argument, and
needs rework.

---

## Rule 1 — Explanatory transitions, not declarative statements

Do not open a concept's introduction by stating what it provides. Open by
naming the cost or gap left by the previous tool, then introduce the new
one as the answer to that specific gap.

**Avoid:**
> "AtomicInteger provides lock-free coordination."

**Prefer:**
> "`synchronized` solved the counter problem, but it did so by forcing
> every thread to wait its turn. For a single number updated frequently,
> that guarantee is wider than the problem actually requires.
> `AtomicInteger` exists for that narrower case."

The same fact is present in both. Only the causal shape differs.

## Rule 2 — Problem before solution, every time

Introduce the situation a mechanism addresses before naming the mechanism.
A reader should meet the pain point first and the API second.

**Avoid:**
> "`volatile` provides visibility guarantees."

**Prefer:**
> "Sometimes threads do not need to coordinate access to a value. They
> need only to agree on what the current value is. A stop flag is one
> example. This is the problem `volatile` solves."

## Rule 3 — Story progression, not taxonomy

Section order in the chapter plan is fixed by the KPI document and does
not change. What changes is how the reader *experiences* that order. The
reader should feel a single line of reasoning:

```
race condition → remove the state → isolate the state →
coordinate the state → choose the smallest tool for what remains
```

The reader should never feel a list of independent options being surveyed
in sequence:

```
immutability → ThreadLocal → AtomicInteger → synchronized →
volatile → collections
```

Section headings and their order stay exactly as planned. Only the prose
connecting them is written to make each one feel necessitated by the one
before it, not merely adjacent to it.

## Rule 4 — Preserve emotional rhythm and memorable observations

Prefer a short, plain restatement of the real point over a purely factual
description, especially after a mechanism has just been built up across
several sentences. This mirrors the Teaching Rhythm already required by
`style-guide.md`, but the instruction here is about the *quality* of that
restatement, not just its frequency.

Benchmark lines from the style this directive targets:
- "`count++` looks atomic. It is not."
- "The safest lock is the one never required."
- "A bug that fails once in ten thousand runs survives every quality gate
  and waits for production to find it."
- "The problem is not the increment. The problem is the absence of
  coordination."

These are not decoration. They are the sentence a reader keeps after
forgetting the surrounding mechanism. Every major section should produce
at least one line with this quality, generated from the section's own
content — not reused or templated across sections.

## Rule 5 — Vary sentence length deliberately

Avoid a run of uniform short sentences and avoid unbroken long academic
paragraphs. Mix three registers within a section:
- **Short, punchy observations** — used to land a point after a longer
  explanation (see Rule 4).
- **Medium explanatory sentences** — the default working register.
- **Longer teaching sentences** — used to build up a mechanism before a
  short sentence lands its consequence.

This variation is what produces reading rhythm. A section that scores
"compliant" against `style-guide.md`'s 35-word cap and 3–6-sentence
paragraph rule can still read flat if every sentence lands at the same
length within those bounds — the cap is a ceiling, not a target.

## Rule 6 — Precision with warmth, not precision instead of warmth

The prose should read as "here is why this exists," never as "here is the
definition." This does not license imprecision. Every technical claim must
remain exactly as accurate as a documentation-style sentence would be —
only the framing changes, from definition-first to motivation-first.

## Rule 7 — The after-reading test

After a section is drafted or revised under this directive, check it
against this test before moving on: does the reader finish the section
thinking **"I understand why this tool exists,"** or do they finish
thinking **"I learned another API"**? If the answer is the latter, the
section's facts are probably fine and its causal shape needs rework —
apply Rules 1–3 again before touching the technical content.

---

## Explicit non-goals — what this directive must never change

Applying this directive must never alter:
- Chapter structure or section ordering
- Which examples or domain scenarios are used
- Code listings, listing titles, or code length
- Topic weighting or scope, as set by the chapter's KPI document
- Technical content or technical accuracy
- Learning objectives or the chapter's thesis
- The existence or placement of transition sentences between sections
  (their presence is `style-guide.md`'s rule; only their *wording* is in
  scope here)
- Modern Java positioning as established in `tone-reference.md`
- The invisible decision hierarchy underneath the chapter — the ordered
  reasoning a domain expert would use to choose between tools, which
  determines section order even though it is never stated as a list in
  the manuscript itself

A tone pass governed by this directive touches introductions, transitions,
explanations, and conclusions only. If a proposed edit would change a
listing, a heading, an example, or a technical claim, it is out of scope
for this directive and belongs to a separate editing pass instead.

---

## Known failure mode — read before applying

The most common way this directive goes wrong in practice: reaching for
warmth by adding hedge words or filler ("simply," "just," "easy," "really,"
"actually") that `style-guide.md`'s Prohibited Phrases list already bans,
or by expanding a sentence with a qualifying clause that pushes it over the
35-word cap. Conversational tone and mechanical compliance are not in
tension, but the easy version of "more conversational" often violates both
of the constraints already in place. After any pass using this directive,
re-run the existing style-guide checks (prohibited phrases, sentence
length, listing length, paragraph length) before treating the pass as
finished — do not assume a more natural-sounding sentence is automatically
a compliant one.

---

## How to invoke this directive

When starting or revising a chapter, apply `style-guide.md` and
`tone-reference.md` as before for structure, mechanics, and baseline
voice. Apply this directive specifically when drafting or revising
connective prose, and treat Rules 1–3 as the primary lever: if a section's
transitions state facts adjacently instead of building an argument, that
is the defect this directive exists to catch.
