# spec.md — Dependency Contract Checker

## 0. Scope note (read first)

This checker verifies assumptions **`agent-judgment-playbook.md` makes about
the other five governing documents**. Two important scoping findings from
close reading, before the check list:

1. **The playbook never states a numeric pass cap.** It explicitly refuses
   to own pass-count logic ("If you find yourself wanting to track a pass
   count... stop: that is out of scope for this role"). None of the five
   governing documents in this fixture set state a pass-cap number either.
   The "3" only appears in `session-1-orchestrator-spec.md` and
   `editorial-review-automation-playbook.md` — both **outside** the six
   files this session was given. So "the 3-pass cap" from the brief's
   starting list is **not checkable within this document set** — see
   Open Question Q1 below. It is not implemented as a mechanical check.

2. **The playbook doesn't cite *which* document each Hard Constraint comes
   from.** The brief's starting list asks us to check the five named Hard
   Constraints "actually appear, verbatim or near-verbatim, in the governing
   documents the playbook cites them from" — but the playbook doesn't cite
   a source document per constraint; they're presented as the playbook's
   own rules. Mapping each constraint to an implied source doc is a
   judgment call, not a lookup. See Q2 and the "not automatable" list.

## 1. Input shape

`check_all(docs: dict[str, str]) -> list[CheckResult]`, where `docs` maps
canonical filenames (e.g. `"agent-judgment-playbook.md"`) to raw file text.

**Justification:** raw strings make every checker a pure function, trivial
to unit test with inline mutated strings, and decoupled from the filesystem.
A thin wrapper, `check_all_from_dir(path) -> list[CheckResult]`, reads the
six conventional filenames from a directory and calls `check_all` — this is
what a pre-commit hook or CLI entry point uses. Both are provided.

## 2. Output shape

```python
@dataclass(frozen=True)
class CheckResult:
    assumption_id: str
    passed: bool
    expected: object   # what the assumption claims
    found: object      # what was actually present
    detail: str        # human-readable, for a non-programmer editorial lead
```

One result per assumption. `check_all` never short-circuits — it runs every
checker and returns the full list even if earlier ones failed.

## 3. Mechanically checkable assumptions

| ID | Checked against | Mechanical check | Pass | Fail |
|---|---|---|---|---|
| `defect_category_count` | `editorial-review-process.md` | Count `### N.` headings under `## Recurring Defect Categories`. Separately extract the number-word in that file's own claim ("all **ten** recurring defect categories") and convert to an int — that becomes `expected`, so the check is self-referential rather than a hardcoded magic number. | actual heading count == expected | e.g. `expected=10, found=9` |
| `checklist_question_count` | `editorial-review-process-addendum-go-no-go.md`, cross-checked against `agent-judgment-playbook.md` | Count numbered items under `## The seven questions`. `expected` is parsed from the playbook's own phrase `"seven-question checklist"` (number-word → int), so a future playbook edit that says "eight-question checklist" changes the expectation automatically. | counts match | e.g. `expected=7, found=6` |
| `evaluate_dimension_count` | `editorial-review-process.md` Phase 1 numbered list, cross-checked against playbook's `"seven dimensions"` phrase | Same number-word-derived-expectation pattern as above, counting the `1. **Priority** ... 7. **Recommendation**` list in `editorial-review-process.md`. | counts match | mismatch reported |
| `hard_constraint_count` | `agent-judgment-playbook.md` | Count bold-labeled bullets (`- **Label**`) under `## Hard Constraints`. `expected` is a fixed constant (`5`) since no document states this count in words — see Q3, this is a documented snapshot assumption, not self-referential. | count == 5 | e.g. `expected=5, found=4` |
| `protected_callout_names_present` | Playbook's `protected_passages` example list, checked against `editorial-review-process.md`'s "What NOT to Touch by Default" and `style-guide.md` | Three keyword-presence checks: "opening" + "scenario" in the process doc's protected list; "When NOT to use" (case-insensitive) in `style-guide.md`; "Summary" + "recap" in the process doc's protected list. | all three keyword pairs found | any missing keyword reported by name |
| `recommendation_scale_consistency` | `agent-judgment-playbook.md` vs. `editorial-review-process.md` vs. the addendum | Extract the 5-way vocabulary from each doc, normalize (uppercase, collapse all whitespace *including embedded newlines* to a single space, `_`→space) BEFORE splitting on `/`, so a value that line-wraps mid-phrase (e.g. "APPLY\nWITH CARE" across a line break) is still read as one token, not two. Then compare as a prefix match (process.md's `RESOLVED AS SIDE EFFECT OF ANOTHER ITEM` is allowed to extend playbook's `RESOLVED AS SIDE EFFECT` — see Q4). | all 5 values present, as 5 distinct tokens, in both compared docs after normalization | named mismatch(es) reported, including if a doc yields fewer than 5 parsed tokens |
| `closing_bridge_convention_defined` | `editorial-review-process.md` | Heading `## The Closing-Bridge Convention` exists, and the phrase "never a chapter number" (or equivalent) appears in that section, matching the playbook's own "never a chapter number" instruction. | both found | whichever is missing, named |

## 4. Not automatable (honest list, not padded)

| Assumption | Why it can't be mechanically checked |
|---|---|
| Hard Constraints' "near-verbatim" match to a *specific* source document | The playbook doesn't say which document each constraint derives from (see Q2). Deciding that "No section dilution" is "the same rule as" editorial-review-process.md's "What NOT to Touch by Default" is a semantic judgment about equivalent intent, not a string match. |
| Whether each of the 10 defect-category *descriptions* is still accurate prose | This is exactly the brief's own example — checking a category still *exists* is countable; checking its prose description still correctly describes real recurring chapter defects requires re-reading actual chapter text and judgment. |
| Whether the 7 checklist *questions'* substance still make sense together (no contradiction, no redundant pair) | Requires reading comprehension of the questions' meaning, not their count or headings. |
| "Book spine alignment" (addendum Q4) — whether cited precedent is real | Requires checking actual chapter files for the claimed convention, a judgment call about consistency, not a static cross-reference between these six documents. |
| Deeper semantic equivalence behind `protected_callout_names_present`'s keyword hits | The mechanical check only proves the *keywords* co-occur; it can't confirm "When NOT to use" in style-guide.md and "When X is not the right choice" in editorial-review-process.md are describing the *same* callout convention rather than two different ones that happen to share vocabulary. |

## 5. Open questions — flagged back, not silently resolved

- **Q1 (pass cap):** The brief's starting list includes "the 3-pass cap" as
  a checkable assumption, but no number appears anywhere in the six
  documents this session was scoped to. Was this meant to be checked
  against `session-1-orchestrator-spec.md` / the automation playbook
  instead (outside this session's file list), or was it listed in error?
- **Q2 (Hard Constraint provenance):** Should the playbook be edited to
  name which document each Hard Constraint derives from, so this becomes
  mechanically checkable rather than judgment-based?
- **Q3 (Hard Constraint count as a magic number):** `hard_constraint_count`
  expects a fixed `5` because nothing states the count in words. Is 5 the
  intended permanent number, or should the playbook state it explicitly
  ("five Hard Constraints") the way it does for the checklist and
  dimensions, so this check could become self-referential like the others?
- **Q4 (recommendation-scale phrasing):** Is `editorial-review-process.md`'s
  "RESOLVED AS SIDE EFFECT **OF ANOTHER ITEM**" an intentional fuller name
  that the playbook's "RESOLVED_AS_SIDE_EFFECT" abbreviates, or drift that
  should be reconciled to one canonical phrasing?
- **Q5 (dimension count ambiguity):** The playbook's EVALUATE step 3 lists
  8 bullet fields (`priority` through `reason`) under a header claiming
  "seven dimensions." This only reconciles to 7 if `reason` is read as a
  sub-field of `recommendation` rather than its own dimension — is that
  the intended reading, or is the header out of date?