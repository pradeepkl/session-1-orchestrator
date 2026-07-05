# I/O Contract — APPLY

Called only after the orchestrator (and, per its gating rule, possibly the
person) has approved specific items from a prior EVALUATE response. The
agent receives only approved items — never the full evaluation, never a
DO_NOT_APPLY item.

## Input schema

```json
{
  "task": "APPLY",
  "chapter_id": "chapter06",
  "pass_number": 1,
  "chapter_text": "<current working copy, exact string>",
  "approved_items": [
    {
      "item_id": "c1",
      "recommendation": "APPLY",
      "minimal_corrected_text": "<from the EVALUATE response — the exact text to introduce>"
    }
  ],
  "direct_instructions": [
    { "instruction_id": "d1", "text": "chapter title should be X", "action": "apply_verbatim" }
  ],
  "next_chapter_context": "<same as EVALUATE input, or null>"
}
```

Notes:
- `chapter_text` is supplied fresh by the orchestrator on every call — the
  agent never assumes it still matches an earlier view of the chapter and
  never re-fetches or re-copies anything itself.
- `approved_items` only ever contains items the orchestrator has already
  cleared for application. If an included item's `recommendation` is
  anything other than APPLY / APPLY_SELECTIVELY / APPLY_WITH_CARE, that's
  an orchestrator-side bug — the agent should report it in
  `input_errors` rather than acting on it.

## Output schema

```json
{
  "revised_chapter_text": "<full string, orchestrator persists this — agent does not write files>",
  "change_log": [
    {
      "item_id": "c1",
      "section": "string — human-locatable section/paragraph name, not a line number",
      "before_excerpt": "string, short",
      "after_excerpt": "string, short"
    }
  ],
  "deviations_from_review_wording": [
    {
      "item_id": "c7",
      "reason": "string — why the applied text differs from the review's literal suggestion, e.g. a style-rule conflict"
    }
  ],
  "hard_constraint_self_check": {
    "no_cross_reference_invalidated": true,
    "no_section_reordered_added_removed": true,
    "no_protected_passage_diluted": true,
    "no_code_block_changed": true,
    "notes": "string, populated only if any of the above is false"
  },
  "input_errors": [
    { "item_id": "c9", "problem": "string — e.g. 'received item with recommendation DO_NOT_APPLY'" }
  ]
}
```

## Example — populated (abbreviated)

```json
{
  "revised_chapter_text": "<full chapter markdown>",
  "change_log": [
    {
      "item_id": "c1",
      "section": "Opening paragraph",
      "before_excerpt": "Both failures share the same root cause: the compiler never knew...",
      "after_excerpt": "One failure was acknowledged and handled dishonestly; the other was never acknowledged in the first place."
    }
  ],
  "deviations_from_review_wording": [
    {
      "item_id": "c14",
      "reason": "Review's suggested bridge used 'The next chapter examines...', which violates the supplied style rule against chapter-number/chapter-reference phrasing in body prose. Rewrote to name the concept without naming the chapter."
    }
  ],
  "hard_constraint_self_check": {
    "no_cross_reference_invalidated": true,
    "no_section_reordered_added_removed": true,
    "no_protected_passage_diluted": true,
    "no_code_block_changed": true,
    "notes": ""
  },
  "input_errors": []
}
```