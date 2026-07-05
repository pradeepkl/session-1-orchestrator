# Addendum to editorial-review-process.md — Pre-Edit Go/No-Go Checklist

This addendum sits inside **Phase 1 (Evaluate Only)**. It runs on every
individual review comment, on every chapter, before any recommendation is
marked APPLY — including comments that arrive in a later round, after a
chapter has already been through one edit pass. A second- or third-round
review comment is not exempt from this checklist just because it's fixing
an earlier fix.

Run each comment through all seven questions below. The checklist does not
replace the existing recommendation scale (APPLY / APPLY SELECTIVELY / APPLY
WITH CARE / RESOLVED AS SIDE EFFECT / DO NOT APPLY) — it's the filter a
comment passes through *before* that scale is assigned.

## The seven questions

1. **Structural break** — Does the fix change section structure, heading
   order, listing numbering, or the chapter's established architecture? A
   comment that requires restructuring to accommodate it needs a stronger
   justification than one that's a local sentence-level fix.

2. **Technical error** — Is this correcting an outright factual error about
   language semantics (category 6 in the defect list), or is it a rhetorical
   or stylistic preference dressed up as a correction? Technical errors
   override every other consideration, including "don't touch load-bearing
   material" defaults. Stylistic preferences do not.

3. **Chapter spine alignment** — Does the fix serve the chapter's own
   controlling idea (its named architecture — e.g. the "compiler learns X"
   progression), or does it pull a sentence toward a different, unrelated
   virtue (extra precision, extra hedging) that the chapter doesn't need at
   that point?

4. **Book spine alignment** — Does the fix match conventions already
   established elsewhere in the manuscript (title formats, listing formats,
   bridge-sentence conventions, recurring defect categories), or does
   reverting/changing it make this chapter *less* consistent with the rest
   of the book? Check actual precedent in other chapter files before
   accepting a claim about "the book's style" — don't take the comment's
   characterization of convention on faith.

5. **Readability / flow** — Does the surrounding paragraph read better
   after the change, independent of correctness? A technically-defensible
   fix that makes prose clunkier is still a cost to weigh against its
   benefit.

6. **Conciseness** — Does the fix add words without adding meaning? Prefer
   the shorter of two equally-correct phrasings. A fix that trades a short,
   confident sentence for a longer, hedged one needs a real technical
   justification, not just a precision preference.



## Decision rule

- **GO** requires: no unjustified structural break, AND (a genuine technical
  error OR a clear, precedent-backed alignment gain) AND no net loss on
  readability/conciseness/tone.
- **NO-GO** applies when a comment's only justification is a stylistic
  preference that conflicts with established precedent elsewhere in the
  book, touches protected/load-bearing material (see "What NOT to Touch by
  Default" above) without a technical-error justification, or nets out
  longer and more hedged without a correctness gain.
- When a comment identifies a real problem but its *proposed* fix fails the
  checklist (e.g., correct concern, overwrought solution), say so
  explicitly: agree with the diagnosis, reject or lighten the prescribed
  edit, and note what a minimal version of the fix would look like instead
  of applying the comment's exact wording by default.

## Worked precedent (Chapter 4, round 2 of review)

Applying this checklist to a second-round review is what caught: a genuine
regression (the Summary's recap paragraph still contained the null/shape
conflation that had already been corrected elsewhere in the same chapter —
GO, technical error overrides the "don't touch the recap" default); a
title-revert request that was actually *less* consistent with the book's
established title convention once other chapters' real titles were checked
(NO-GO); and an opening-sentence edit that touched protected material to
fix something that was never a technical error in the first place, trading
a strong hook for a hedged one (NO-GO).
