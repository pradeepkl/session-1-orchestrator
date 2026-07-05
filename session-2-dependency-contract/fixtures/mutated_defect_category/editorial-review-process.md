# Editorial Review Process — Modern Java eBook

This file defines the repeatable review-and-fix workflow used on this
manuscript, starting with Chapter 2 and Chapter 3. Any chapter still in
final-editing should be run through this same process, so the manuscript's
quality bar stays consistent from chapter to chapter regardless of which
session or model performed the review.

This file is the **process**. `style-guide.md`, `tone-reference.md`, and
`narrative-voice-directive.md` remain the **rules**. This file does not
restate those rules — it describes how to apply them, plus the categories
of defect that recurred across the chapters already reviewed and are worth
checking for by default.

---

## The Two-Phase Workflow

Editorial review on this manuscript always runs in two distinct phases,
never blended into one pass. Keep them separate even within a single
conversation — the person may want to see the evaluation before authorizing
edits, and combining the phases makes it harder to review the reasoning
before the manuscript changes.

### Phase 1 — Evaluate Only (no file edits)

Given a chapter draft and a set of review comments (either freeform
editorial feedback or `<claudeai_review_comments>` blocks), produce a
standalone evaluation document. Do not touch the chapter file in this
phase.

For each review item, assess:

1. **Priority** — CRITICAL / HIGH / MEDIUM / LOW
2. **Signal-to-noise impact** — does fixing this make the chapter clearer,
   or just different?
3. **Essence risk** — does the fix touch the chapter's core teaching point,
   or only its surface expression? Flag anything that risks diluting the
   central thesis.
4. **Verbosity impact** — estimate words added/removed
5. **Readability impact** — does it read more naturally afterward?
6. **Repetition impact** — does it reduce a construct or example being
   over-proven after the reader already understands it?
7. **Recommendation** — APPLY / APPLY SELECTIVELY / APPLY WITH CARE /
   RESOLVED AS SIDE EFFECT OF ANOTHER ITEM / DO NOT APPLY (with reason)

Close the evaluation with:
- A summary table (issue → priority → recommendation)
- A "net expected outcome" comparison (word count before/after, defect
  count before/after)
- An explicit note on which sections should be left alone, so the next
  phase does not over-trim material the review didn't flag

Save this as `chapterNN-editorial-review-evaluation.md`.

### Phase 2 — Apply Only (targeted edits)

Once the person confirms (or in the same turn, if they've pre-authorized
it — check their message), apply the fixes from Phase 1 as **targeted,
minimal edits**:

- Preserve section structure, heading order, and listing numbering unless
  a specific finding requires reordering (e.g., a section landing before
  the vocabulary it depends on is complete).
- Prefer editing a sentence or paragraph over rewriting a section.
- If a listing must be removed because it's redundant, remove its
  surrounding prose too, but do not touch adjacent listings' numbering
  logic beyond what naturally follows.
- After every removal, re-check cross-references (listing numbers, table
  numbers, "as shown above/below" pointers) for consistency.
- Do not apply LOW-priority stylistic suggestions if they'd require
  touching load-bearing teaching material the review explicitly said to
  keep.

Save the result as `chapterNN-<descriptive-slug>.md` and present both
files (evaluation + revised chapter) together if this is the first time
sharing them, or just the revised chapter if only edits were requested.

---

## Recurring Defect Categories (check every chapter for these)

These are not chapter-specific bugs — they are patterns that showed up
independently in both Chapter 2 and Chapter 3, and are worth checking for
by default on every remaining chapter, even without an explicit review
comment flagging them.

### 1. Enumerated counts in prose
"Three capabilities," "the four contracts," "five things happen in
sequence," "Use case 1/2/3/4." The style guide already prohibits this, but
it recurs. Fix: let headings, listings, and tables carry the count
implicitly. Rewrite the sentence so it doesn't need the number at all,
rather than swapping one number for another.

### 2. Proving the same idea more times than needed
A thesis lands at a specific listing (usually the fully-integrated
pipeline/example near the chapter's midpoint or two-thirds mark). Material
after that point should extend the idea to a new context, not re-prove it
in a different domain example. Watch for: repeated predicate/rule
definitions across multiple listings, multiple near-identical scenario
walkthroughs, "Vocabulary/Decisions in Action" sections that restate rather
than extend.

**Test:** if a listing after the thesis-landing point could be deleted
without the reader losing a concept (only losing a rehearsal of a concept
they already have), it's a candidate for removal or consolidation.

### 3. Absolute or overstated claims
Phrases like "only X travels freely," "the compiler ensures," "always,"
"never," "X is always Y" often overstate what's technically true. These
read as confident but are editorially risky — they can be factually wrong
(see #6 below) or simply broader than the underlying mechanism supports.
Fix: ground the claim historically or add the specific qualifying
condition, without losing the rhetorical force of the sentence.

### 4. Unnecessary invented terminology
A chapter introduces a named concept ("functional descriptor," etc.) that
isn't used consistently elsewhere and isn't required — plain language
already available in the chapter does the same job. Fix: remove the term,
rely on the example and existing vocabulary.

### 5. Self-contradiction against the chapter's own framework
A chapter teaches a decision rule (e.g., value vs. entity, strategy vs.
capability) and then an example elsewhere in the same chapter violates that
rule without acknowledgment. This is more serious than simple imprecision
— it undermines the chapter's own teaching tool. Fix: add a short
qualifying note at the point of tension rather than renaming or
restructuring every downstream reference (renaming has a much larger blast
radius across listings; a caveat is lower-risk and just as honest).

### 6. Technically incorrect claims about language semantics
Distinct from #3 — this is not overstatement, it's an outright factual
error (e.g., claiming a plain `catch` chain gets exhaustiveness checking,
when only a sealed-type pattern-matching `switch` does). These must be
fixed regardless of length/style considerations — correctness overrides
brevity every time.

### 7. Introduced-but-unused constructs in integrated/final examples
A chapter's closing "everything together" example sometimes introduces a
construct (an interface, a helper type) that never actually gets exercised
by the code that follows, and the surrounding prose then asserts it was
used. This is a structural bug, not a style issue. Fix: either wire the
construct into the example properly (composition-based rewrite) or remove
it if wiring it in would require restructuring beyond a targeted edit —
prefer removal when the instruction is to make minimal, targeted fixes.

### 8. Version-specific syntax distracting from a timeless lesson
An example meant to teach a general concept (e.g., method references)
uses a very recent, narrowly-available API and calls out its version in a
comment, pulling reader attention toward "what is this new API" instead of
the concept being taught. Fix: swap in a longstanding equivalent unless the
version-specific API is the actual point of the section.

### 9. Analogies stretched past where they hold
A teaching analogy (SQL, a physical metaphor, etc.) is used to explain
several constructs, and it fits some cleanly but is forced for others. Fix:
keep the analogy for the constructs where it's genuinely illuminating, and
add one honest sentence marking where it stops working, rather than
silently forcing a weak parallel.

---

## The Closing-Bridge Convention

Every chapter's Summary should end with a short (one-to-two sentence)
forward-pointing bridge to the next chapter's actual theme — not a
plot-summary of what's coming, and never a chapter number.

Pattern: name the concept the current chapter established, then pose the
gap or question the next chapter resolves, in the same voice as the rest
of the Summary.

**Example (Chapter 2 → Chapter 3):**
> Behavior no longer needs a subclass to live in — a lambda stored, passed,
> and composed proves that. What replaces inheritance as the way the rest
> of a domain gets modeled is the question that follows next.

**Example (Chapter 3 → Chapter 4, pattern matching):**
> A sealed hierarchy declares its shape once, but nothing so far has
> verified that every branch handling it actually accounts for that shape.
> Teaching the compiler to check that completeness — and to refuse to
> compile when it cannot — is where this leaves off.

When writing this bridge, it helps to have at least skimmed the opening of
the next chapter (or its KPI file) so the bridge's language actually matches
the next chapter's real throughline, rather than a guess.

---

## What NOT to Touch by Default

Every review so far has explicitly identified certain sections as strong
and load-bearing. Unless a specific comment targets them, leave these
categories alone even while trimming elsewhere:

- The chapter's opening problem/motivation scenario (the "fragile base
  class," the "why modern Java" framing, etc.)
- Any section teaching a core decision rule the chapter is named for
- "When X is not the right choice" boundary callouts — these are
  consistently flagged as some of the strongest material in the manuscript
- The Summary's core recap paragraph (only the closing bridge gets
  rewritten, not the recap itself)

---

## Session Continuity Note

This file lives in project knowledge, not conversation memory. A fresh
session reviewing any later chapter should:

1. Rely on `project_knowledge_search` to pull this file, plus
   `style-guide.md`, `tone-reference.md`, `narrative-voice-directive.md`,
   and the relevant `chapterNN-kpi.md`, automatically — no need to paste
   this file's contents into the conversation.
2. Follow the two-phase workflow above without deviation.
3. Check the chapter against all ten recurring defect categories, even if
   the person's review comments don't explicitly name all of them.
4. Apply the closing-bridge convention, referencing the actual next
   chapter's content if it's available in project files.
5. Produce both output files (evaluation + revised chapter) unless the
   person has already approved and only wants the revised chapter.
