# spec.md — Orchestrator (Session 1)
### Authored upstream (orchestrating session), not by the implementing session. The implementing session builds and tests against this document as fixed ground truth. Any perceived defect here is flagged back as a question, not silently corrected.

## 1. Purpose

A LangGraph state graph, in Python, that sequences calls to the judgment
agent (EVALUATE / APPLY, per `agent-judgment-playbook.md` and the two I/O
contracts), enforces the 3-pass cap, and inserts two mandatory human
go/no-go gates per pass. The orchestrator holds all sequencing/state
logic; the agent holds none. GitHub is the persistence and approval
layer — the orchestrator never writes to the default branch directly.

## 2. Repository assumptions

- Canonical markdown files (governing docs, playbook, I/O contracts) and
  chapter files live in a GitHub repo.
- The orchestrator's GitHub credential is **read-only** against the
  default branch. This is enforced by token scope (a fine-grained PAT
  with contents:read only against the default branch) *and* by a branch
  protection rule requiring PR review before merge — belt and suspenders,
  not either alone.
- Every APPLY result is pushed to a **new branch** (naming convention:
  `chapter-<chapter_id>-pass-<pass_number>`) and opened as a PR against
  the default branch. The orchestrator never pushes to the default
  branch under any condition, including a pass-3-cap outcome.
- The PR body contains, verbatim from the APPLY/EVALUATE outputs: the
  post-edit summary (change → resolved item → location), the
  scope-integrity confirmation, and the convergence assessment.

## 3. State schema

```python
class GraphState(TypedDict):
    chapter_id: str
    pass_number: int
    max_passes: int  # fixed at 3
    chapter_text: str  # in-memory working copy, hydrated read-only from
                        # GitHub at pass start; never re-initialized from
                        # source after pass 1
    prior_rounds_summary: list[dict]  # [] on pass 1
    last_evaluate_result: EvaluateOutput | None
    last_apply_result: ApplyOutput | None
    evaluate_gate_pending: bool
    evaluate_gate_decision: Literal["approved", "rejected", "pending"]
    approved_item_ids: list[str]  # populated by a partial approval
    apply_gate_pending: bool
    apply_gate_decision: Literal["approved", "rejected", "pending"]
    pr_number: int | None  # whichever gate currently has an open
                           # PR/issue awaiting a decision
```

## 4. Node list

- `evaluate_node` — calls the agent with an EVALUATE payload built per
  `io-contract-evaluate.md`.
- `evaluate_gate_node` — posts the EVALUATE result as a GitHub issue (one
  per pass, not a PR — no code diff exists yet at this point) containing
  the per-item table and convergence assessment. Pauses the graph.
  Reads back the author's decision as: a comment matching a fixed
  parseable format (e.g. `approve: c1,c2,c4` or `approve: all` or
  `reject`) — the implementing session may propose a different concrete
  syntax but must document it in README.md and keep it machine-parseable
  with no natural-language interpretation required.
- `apply_node` — calls the agent with an APPLY payload containing only
  `approved_item_ids` from the prior gate, per `io-contract-apply.md`.
- `apply_gate_node` — pushes a branch, opens a PR with the diff and the
  post-edit summary. Pauses the graph. Reads back merge (approved) or
  close-without-merge (rejected) as the decision.
- Routing/helper nodes as needed to connect the above; name and justify
  any addition in the implementing session's own code comments.

## 5. Conditional edges

- `evaluate_node` → `evaluate_gate_node`: always. No path bypasses this
  gate for any EVALUATE outcome, regardless of severity.
- `evaluate_gate_node` → `apply_node`: on approval (full or partial —
  `approved_item_ids` may be a subset of all APPLY-eligible items).
- `evaluate_gate_node` → itself (re-wait) on rejection with revision
  notes; a rejection does not auto-advance the pass counter.
- `apply_node` → `apply_gate_node`: always.
- `apply_gate_node` → next pass's `evaluate_node`: on merge/approval,
  incrementing `pass_number`.
- `apply_gate_node` → `END`: on hitting `max_passes`, or on the author
  explicitly declaring convergence early via the same comment mechanism
  used at the evaluate gate.
- A 4th `evaluate_node` call is refused (graph raises/returns an explicit
  refusal state) once `pass_number > max_passes`.

## 6. Checkpointing

A paused graph (either gate) persists state via LangGraph's checkpointer
and resumes without re-running the EVALUATE or APPLY call already
awaiting approval. The implementing session chooses the concrete
checkpointer backend (in-memory is acceptable for tests; note in
README.md what a production backend would require) and the mechanism for
detecting an author's decision has arrived (webhook, poll, or manual
re-invocation) — state and justify the choice; do not leave it implicit.

## 7. Injectable dependencies

Both the agent call and all GitHub operations (branch create, PR open,
PR/issue read, comment read, merge status read) go through injectable
client interfaces so stubs can stand in during testing. Neither is
hardcoded inside node logic.

## 8. Persistence gate on Hard Constraint failure

If any `hard_constraint_self_check` flag from an APPLY result is false,
`apply_gate_node` does not open a mergeable PR. It opens the PR as a
draft (or opens no PR, returning a failure state — implementing session's
choice, documented in spec) with the failing flag(s) called out explicitly
in the PR/issue body.

## 9. Out of scope for this spec

- The agent's own judgment logic (owned by `agent-judgment-playbook.md`).
- The exact field-level content of EVALUATE/APPLY payloads (owned by the
  two I/O contract files — model as Pydantic directly from those).
- Any UI beyond raw GitHub PR/issue interactions.