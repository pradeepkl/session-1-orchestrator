# io-contract-evaluate.md — Amendment 1
### Append to the canonical file's Output Schema section, under `agent_identified_findings`.

## Change

Add a new field to each entry in `agent_identified_findings`:

```json
{
  "item_id": "agent-1",
  "origin": "agent_identified",
  "defect_category": "string, matching one of the ten supplied categories",
  "priority": "MEDIUM",
  "recommendation": "APPLY_SELECTIVELY",
  "reason": "string",
  "minimal_corrected_text": "string or null — required (non-null) when recommendation is APPLY / APPLY_SELECTIVELY / APPLY_WITH_CARE; null otherwise"
}
```

## Rationale

`SuppliedReviewItem` already carries `minimal_corrected_text` for exactly
this reason: an item recommended for APPLY needs corrected text
available for the orchestrator to build the APPLY payload, since the
agent is never re-consulted between EVALUATE and APPLY for the same
item's wording. `AgentIdentifiedFinding` had no equivalent field,
meaning an agent-identified finding could be marked
APPLY/APPLY_SELECTIVELY/APPLY_WITH_CARE with no way to actually apply
it. This was a genuine contract gap, surfaced by the Session 1
orchestrator build — not a workaround to design around.

## Compatibility note

This is an additive, optional-shaped field (null-permitted for
non-APPLY recommendations) — it does not change the shape of any
existing DO_NOT_APPLY finding, and any code already handling
`agent_identified_findings` without this field only needs updating if it
constructs or consumes APPLY-recommended agent findings.