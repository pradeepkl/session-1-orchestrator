# spec.md — Orchestrator (Session 1) — Addendum 1
### Resolves the three open questions raised in Session 1's README, plus one new gap identified while resolving them. Append this to the canonical spec.md; supersedes anything in §4–5 it contradicts.

## Resolution 1 — `agent_identified_findings` needs `minimal_corrected_text`

Confirmed as a genuine contract gap, not an orchestrator workaround. See
`io-contract-evaluate-amendment-1.md` for the exact field addition to
`io-contract-evaluate.md`. Once that amendment lands, `apply_node`
reconstructs agent-identified APPLY items from `last_evaluate_result`
exactly as it already does for supplied-review items — no special-casing
required.

## Resolution 2 — Apply-gate rejection routing

Confirmed: `apply_gate_node → apply_gate_node` re-wait is correct default
behavior when a human intends to push a fixup commit to the same branch
and re-request review on the same PR.

**New gap surfaced by this resolution:** the current design has no way to
*permanently abandon* a pass. `pending`/`approved`/implicit re-wait covers
"still working on it," but not "this pass is dead, stop waiting." Add:

- A new parseable comment keyword, `abandon`, distinct from `converge`
  (`converge` is a *successful* stop; `abandon` is an unsuccessful one).
- New edge: `apply_gate_node` → `END` on `abandon`, with the final state
  recording `pass_outcome: "abandoned"` (a new state field) rather than
  `"completed"` or `"cap_reached"`.
- `parse_gate_comment()` must recognize `abandon` at the apply gate the
  same way it recognizes `converge` there — both are terminal decisions,
  not routine approve/reject.
- This applies at the apply gate only, matching where `converge` already
  applies. The evaluate gate's rejection path (revise and re-propose)
  doesn't need an abandon path — an evaluate-gate rejection with no
  intention of continuing simply means the operator stops invoking the
  graph; there's no branch/PR alive at that gate to formally close.

## Resolution 3 — `apply_node` payload reconstruction from `last_evaluate_result`

Confirmed as the intended design, now stated here as authoritative rather
than left as a README-only note: `spec.md` §4's `approved_item_ids` is
the state field the evaluate gate populates; `apply_node` is responsible
for reconstructing the full `approved_items` objects required by
`io-contract-apply.md` by looking them up in `last_evaluate_result`
before constructing the APPLY payload. This is not a deviation from the
I/O contract — the contract describes the agent-call boundary, not the
orchestrator's internal state representation.

## State schema addition

```python
class GraphState(TypedDict):
    ...  # all existing fields unchanged
    pass_outcome: Literal["in_progress", "completed", "cap_reached", "abandoned"] | None
```