# I/O Contract — EVALUATE

The orchestrator assembles every field below itself (fetching from project
knowledge, tracking round state) and calls the agent once per round. The
agent never fetches anything and never tracks state across calls.

## Input schema

```json
{
  "task": "EVALUATE",
  "chapter_id": "chapter06",
  "pass_number": 1,
  "max_passes": 3,
  "chapter_text": "<full current chapter markdown, as the orchestrator's working copy currently has it>",
  "review_comments": [
    { "comment_id": "c1", "text": "<verbatim reviewer text>" }
  ],
  "governing_excerpts": {
    "defect_categories": ["<all ten, verbatim, from editorial-review-process.md>"],
    "seven_question_checklist": ["<verbatim from the addendum>"],
    "style_rules": ["<relevant excerpts from style-guide.md / tone-reference.md / narrative-voice-directive.md>"],
    "protected_passages": [
      { "name": "opening_scenario", "text_anchor": "A method throws an exception..." },
      { "name": "summary_recap", "text_anchor": "A bare `throw` and a bare, nullable return..." }
    ]
  },
  "next_chapter_context": "<opening content of the next chapter, or null if this is the last chapter>",
  "prior_rounds_summary": [
    {
      "pass_number": 1,
      "item_count": 14,
      "severity_mix": { "CRITICAL": 2, "HIGH": 3, "MEDIUM": 5, "LOW": 4 },
      "applied_count": 9,
      "do_not_apply_count": 5
    }
  ],
  "direct_instructions": [
    { "instruction_id": "d1", "text": "chapter title should be X" }
  ]
}
```

Notes on fields:
- `review_comments` may be empty (a defect-category-only scan).
- `direct_instructions` is populated by the orchestrator's own bundling
  detection *or* left for the agent to separate out of raw input text if
  the orchestrator passes the message unsplit — pick one approach and be
  consistent; if the orchestrator does the splitting, this array is
  pre-separated and the agent doesn't need to re-detect it.
- `prior_rounds_summary` is `[]` on pass 1.
- `next_chapter_context` is `null` for the manuscript's final chapter —
  the agent must not attempt a closing bridge in that case, and should
  say so rather than fabricating one.

## Output schema

```json
{
  "items": [
    {
      "item_id": "c1",
      "origin": "supplied_review",
      "priority": "CRITICAL",
      "signal_to_noise_impact": "string",
      "essence_risk": "string",
      "verbosity_impact": "string",
      "readability_impact": "string",
      "repetition_impact": "string",
      "recommendation": "APPLY",
      "reason": "string, convergence-framed if not APPLY",
      "minimal_corrected_text": "string or null — only populated for APPLY / APPLY_SELECTIVELY / APPLY_WITH_CARE"
    }
  ],
  "hard_constraint_rejections": [
    { "item_id": "c7", "constraint_hit": "no_code_listing_changes", "note": "string" }
  ],
  "agent_identified_findings": [
    {
      "item_id": "agent-1",
      "origin": "agent_identified",
      "defect_category": "string, matching one of the ten supplied categories",
      "priority": "MEDIUM",
      "recommendation": "APPLY_SELECTIVELY",
      "reason": "string"
    }
  ],
  "convergence_assessment": {
    "scope_trend": "shrinking | flat | growing | baseline_round_1",
    "comparison_note": "string — factual comparison to prior_rounds_summary, no recommendation to stop/continue"
  }
}
```

## Example — populated (abbreviated)

```json
{
  "items": [
    {
      "item_id": "c2",
      "origin": "supplied_review",
      "priority": "CRITICAL",
      "signal_to_noise_impact": "Removes a false equivalence a careful reader would catch",
      "essence_risk": "Touches the chapter's central thesis but only to correct its precision, not replace it",
      "verbosity_impact": "neutral, same length",
      "readability_impact": "positive",
      "repetition_impact": "none",
      "recommendation": "APPLY",
      "reason": "Genuine technical error (Optional does not enforce the same obligation as a checked exception); applies at every location this claim recurs",
      "minimal_corrected_text": "Checked exceptions and Optional both make uncertainty visible in a method signature, but with different strength..."
    },
    {
      "item_id": "c8",
      "origin": "supplied_review",
      "priority": "LOW",
      "signal_to_noise_impact": "would make the table row match body prose exactly, no accuracy gain",
      "essence_risk": "none",
      "verbosity_impact": "cell roughly triples in length",
      "readability_impact": "negative — breaks table scannability",
      "repetition_impact": "none",
      "recommendation": "DO_NOT_APPLY",
      "reason": "Leaving this table cell as short-form 'deterministic close' doesn't block finalizing the chapter, because it isn't inaccurate — it just isn't as verbose as the corrected body prose, and table cells are supposed to stay short throughout this chapter's tables."
    }
  ],
  "hard_constraint_rejections": [],
  "agent_identified_findings": [],
  "convergence_assessment": {
    "scope_trend": "shrinking",
    "comparison_note": "Round 2 raised 7 items vs round 1's 14; DO_NOT_APPLY share rose from 36% to 57%."
  }
}
```