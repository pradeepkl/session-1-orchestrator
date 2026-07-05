# Session-1 Orchestrator

LangGraph orchestrator that sequences EVALUATE/APPLY judgment-agent calls with human go/no-go gates on GitHub issues and PRs.

## Install

```bash
cd orchestrator
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
# or: pip install -r requirements.txt
python -c "import langgraph; from orchestrator import build_orchestrator"
```

Requires **Python 3.11+**.

## Run tests

```bash
pytest -q
```

## Example walkthrough

The example below runs **one full pass** (evaluate gate → apply gate) and starts pass 2 before stopping. Save as `example.py` in the project root or run interactively:

```python
from langgraph.checkpoint.memory import InMemorySaver

from orchestrator import (
    ApplyOutput,
    ChangeLogEntry,
    ConvergenceAssessment,
    EvaluateOutput,
    GateDecisionResult,
    HardConstraintSelfCheck,
    SuppliedReviewItem,
    build_orchestrator,
    initial_state,
)

# --- Minimal stubs (production uses real clients) ---
class ExampleAgent:
    def evaluate(self, payload):
        return EvaluateOutput(
            items=[
                SuppliedReviewItem(
                    item_id="c1",
                    origin="supplied_review",
                    priority="MEDIUM",
                    signal_to_noise_impact="positive",
                    essence_risk="low",
                    verbosity_impact="neutral",
                    readability_impact="positive",
                    repetition_impact="none",
                    recommendation="APPLY",
                    reason="Wording fix.",
                    minimal_corrected_text="Fixed.",
                )
            ],
            convergence_assessment=ConvergenceAssessment(
                scope_trend="baseline_round_1",
                comparison_note="Needs one edit.",
            ),
        )

    def apply(self, payload):
        return ApplyOutput(
            revised_chapter_text="Fixed chapter.",
            change_log=[
                ChangeLogEntry(
                    item_id="c1",
                    section="Opening paragraph",
                    before_excerpt="Before.",
                    after_excerpt="After.",
                )
            ],
            hard_constraint_self_check=HardConstraintSelfCheck(
                no_cross_reference_invalidated=True,
                no_section_reordered_added_removed=True,
                no_protected_passage_diluted=True,
                no_code_block_changed=True,
            ),
        )


class ExampleGitHub:
    def read_chapter_text(self, chapter_id):
        return "Draft chapter."

    def open_issue(self, title, body):
        print("Opened issue:", title)
        return 42

    def read_issue_decision(self, issue_number):
        return GateDecisionResult(decision="pending")

    def create_branch(self, branch_name, chapter_text):
        print("Branch:", branch_name)

    def open_pr(self, branch_name, title, body, *, draft=False):
        print("Opened PR:", branch_name, "draft=", draft)
        return 99

    def read_pr_decision(self, pr_number):
        return GateDecisionResult(decision="pending")


agent = ExampleAgent()
github = ExampleGitHub()
graph = build_orchestrator(agent, github, checkpointer=InMemorySaver())
config = {"configurable": {"thread_id": "example-ch-1"}}

# Pass 1 — invoke until paused at evaluate gate
graph.invoke(initial_state("ch-1", chapter_text="Draft chapter."), config)
print("Paused at evaluate gate:", graph.get_state(config).values["evaluate_gate_pending"])

# Simulated human approval
graph.update_state(
    config,
    {
        "evaluate_gate_decision": "approved",
        "evaluate_gate_pending": False,
        "approved_item_ids": ["c1"],
    },
)
graph.invoke(None, config)
print("Paused at apply gate:", graph.get_state(config).values["apply_gate_pending"])

# Simulated PR merge approval
graph.update_state(
    config,
    {"apply_gate_decision": "approved", "apply_gate_pending": False},
)
graph.invoke(None, config)
state = graph.get_state(config).values
print("Pass 2 begins — pass_number:", state["pass_number"])
print("Chapter text carried forward:", state["chapter_text"])
```

## Discretionary choices

| Topic | Choice | Notes |
|-------|--------|-------|
| Approval-comment syntax | `approve: all`, `approve: c1,c2`, `reject`, `converge`, `abandon` | Parsed by `parse_gate_comment()`; `approve: all` resolves to concrete APPLY-eligible IDs at parse time (never an empty list downstream). `converge` and `abandon` are terminal at the apply gate only: `converge` is a successful stop (`pass_outcome: "completed"`), `abandon` is an unsuccessful stop (`pass_outcome: "abandoned"`). |
| `pass_outcome` state field | `Literal["in_progress", "completed", "cap_reached", "abandoned"] \| None` | Set by `finalize_end_node` when the apply gate terminates: `"completed"` on `converge`, `"cap_reached"` on approve at `max_passes`, `"abandoned"` on `abandon`. `termination_reason` is populated for the first two (`early_convergence`, `max_passes`) but stays `None` on `abandon`. `None` while the graph is still running. |
| `pr_number` state field | Single field per spec.md §3 | Holds the open issue during evaluate gate, then the open PR during apply gate; gates never overlap. Idempotency uses `pr_number` locally inside each node. |
| `approved_item_ids` on approval | No silent default-to-all in graph | Empty list + `approved` = approve zero items. `approve: all` must be resolved by the comment parser before state is written. |
| Apply payload shape (spec.md §4 vs io-contract-apply.md) | Gate carries IDs; `apply_node` reconstructs objects | Settled in Addendum 1 — gate carries `approved_item_ids`; `apply_node` looks up full objects in `last_evaluate_result` (supplied-review and agent-identified items alike). |
| Apply-gate rejection | `apply_gate_node → apply_gate_node` re-wait | Settled in Addendum 1 — operator can push a fixup commit and re-request review on the same PR. Use `abandon` to permanently stop without advancing `pass_number`. |
| Checkpointer | `InMemorySaver` (tests); Postgres/SQLite (production) | One `thread_id` per chapter. |
| Decision detection | Manual re-invocation + gate-node polling | External process calls `invoke(None, config)` after human comments. |
| Invalid approval IDs | All-or-nothing per pass | A single bad ID in an `approve:` batch blocks the whole batch for that pass — none of the other approved IDs are applied; `input_errors` is synthesized and the operator must resubmit a corrected `approve:` comment. |
| Hard-constraint failure (§8) | Draft PR (`draft=True`) | Failing flag names appear in PR body. |

`ApplyInput` / `ApplyOutput` match `io-contract-apply.md` field-for-field. `EvaluateInput` / `EvaluateOutput` match `io-contract-evaluate.md` including Amendment 1 (`minimal_corrected_text` on `agent_identified_findings`).

## Resolved (Addendum 1)

The three open questions from Session 1 are settled in `docs/session-1-orchestrator-spec.md` (Addendum 1):

1. **`agent_identified_findings` needs `minimal_corrected_text`** — Confirmed as a genuine contract gap, not an orchestrator workaround. Amendment 1 adds the field to `io-contract-evaluate.md`; required (non-null) when recommendation is APPLY / APPLY_SELECTIVELY / APPLY_WITH_CARE, null otherwise. `apply_node` reconstructs agent-identified APPLY items from `last_evaluate_result` the same way as supplied-review items.

2. **Apply-gate rejection routing** — Confirmed: `apply_gate_node → apply_gate_node` re-wait is correct when the operator intends a fixup commit on the same branch/PR. Addendum 1 adds a distinct `abandon` keyword and `apply_gate_node → END` path with `pass_outcome: "abandoned"` for permanently stopping a pass.

3. **`apply_node` payload reconstruction** — Confirmed: `approved_item_ids` is the gate state field; `apply_node` reconstructs full `approved_items` from `last_evaluate_result` before calling the agent. This is orchestrator internal state, not an I/O contract deviation.

## Invalid approval IDs (orchestrator behavior)

If `approved_item_ids` contains an unknown ID, a non-APPLY-eligible ID, or an APPLY-eligible ID missing `minimal_corrected_text`, `apply_node` does **not** call the agent. It synthesizes an `ApplyOutput` with `input_errors` populated (chapter text unchanged) and the graph continues to `apply_gate_node` so the operator can see the failure in the PR body.

Canonical source documents live in `docs/` and must not be reconstructed from the implementation brief.

## Project layout

```
orchestrator/
├── README.md
├── pyproject.toml
├── requirements.txt
├── src/orchestrator.py
├── tests/test_orchestrator.py
└── docs/          # reference copies of spec + I/O contracts
```

All orchestrator logic lives in `src/orchestrator.py` per brief.
