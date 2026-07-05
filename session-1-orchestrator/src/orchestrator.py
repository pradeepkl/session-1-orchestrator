"""Session-1 LangGraph orchestrator for EVALUATE/APPLY judgment workflow."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, Protocol, TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field, model_validator

# ---------------------------------------------------------------------------
# I/O contract models (io-contract-evaluate.md, io-contract-apply.md)
# ---------------------------------------------------------------------------

APPLY_ELIGIBLE_RECOMMENDATIONS = frozenset(
    {"APPLY", "APPLY_SELECTIVELY", "APPLY_WITH_CARE"}
)


class ReviewComment(BaseModel):
    comment_id: str
    text: str


class ProtectedPassage(BaseModel):
    name: str
    text_anchor: str


class GoverningExcerpts(BaseModel):
    defect_categories: list[str]
    seven_question_checklist: list[str]
    style_rules: list[str]
    protected_passages: list[ProtectedPassage] = Field(default_factory=list)


class EvaluateDirectInstruction(BaseModel):
    instruction_id: str
    text: str


class EvaluateInput(BaseModel):
    task: Literal["EVALUATE"] = "EVALUATE"
    chapter_id: str
    pass_number: int
    max_passes: int
    chapter_text: str
    review_comments: list[ReviewComment]
    governing_excerpts: GoverningExcerpts
    next_chapter_context: str | None = None
    prior_rounds_summary: list[dict] = Field(default_factory=list)
    direct_instructions: list[EvaluateDirectInstruction] = Field(default_factory=list)


class SuppliedReviewItem(BaseModel):
    item_id: str
    origin: str
    priority: str
    signal_to_noise_impact: str
    essence_risk: str
    verbosity_impact: str
    readability_impact: str
    repetition_impact: str
    recommendation: str
    reason: str
    minimal_corrected_text: str | None = None


class HardConstraintRejection(BaseModel):
    item_id: str
    constraint_hit: str
    note: str


class AgentIdentifiedFinding(BaseModel):
    item_id: str
    origin: str
    defect_category: str
    priority: str
    recommendation: str
    reason: str
    minimal_corrected_text: str | None = None

    @model_validator(mode="after")
    def _minimal_corrected_text_required_for_apply(self) -> AgentIdentifiedFinding:
        if self.recommendation in APPLY_ELIGIBLE_RECOMMENDATIONS:
            if not self.minimal_corrected_text:
                raise ValueError(
                    "minimal_corrected_text is required when recommendation is "
                    "APPLY / APPLY_SELECTIVELY / APPLY_WITH_CARE"
                )
        return self


class ConvergenceAssessment(BaseModel):
    scope_trend: Literal["shrinking", "flat", "growing", "baseline_round_1"]
    comparison_note: str


class EvaluateOutput(BaseModel):
    items: list[SuppliedReviewItem]
    hard_constraint_rejections: list[HardConstraintRejection] = Field(default_factory=list)
    agent_identified_findings: list[AgentIdentifiedFinding] = Field(default_factory=list)
    convergence_assessment: ConvergenceAssessment


class ApprovedItem(BaseModel):
    item_id: str
    recommendation: str
    minimal_corrected_text: str


class ApplyDirectInstruction(BaseModel):
    instruction_id: str
    text: str
    action: str


class ApplyInput(BaseModel):
    task: Literal["APPLY"] = "APPLY"
    chapter_id: str
    pass_number: int
    chapter_text: str
    approved_items: list[ApprovedItem]
    direct_instructions: list[ApplyDirectInstruction] = Field(default_factory=list)
    next_chapter_context: str | None = None


class ChangeLogEntry(BaseModel):
    item_id: str
    section: str
    before_excerpt: str
    after_excerpt: str


class DeviationFromReviewWording(BaseModel):
    item_id: str
    reason: str


class HardConstraintSelfCheck(BaseModel):
    no_cross_reference_invalidated: bool
    no_section_reordered_added_removed: bool
    no_protected_passage_diluted: bool
    no_code_block_changed: bool
    notes: str = ""


class ApplyInputError(BaseModel):
    item_id: str
    problem: str


class ApplyOutput(BaseModel):
    revised_chapter_text: str
    change_log: list[ChangeLogEntry]
    deviations_from_review_wording: list[DeviationFromReviewWording] = Field(
        default_factory=list
    )
    hard_constraint_self_check: HardConstraintSelfCheck
    input_errors: list[ApplyInputError] = Field(default_factory=list)


GateDecisionLiteral = Literal["approved", "rejected", "pending", "converged", "abandoned"]


class GateDecisionResult(BaseModel):
    """Parsed human decision from a GitHub issue comment or PR review."""

    decision: GateDecisionLiteral
    approved_item_ids: list[str] = Field(default_factory=list)
    revision_notes: str | None = None


# ---------------------------------------------------------------------------
# Graph state (spec.md Section 3 + justified additions)
# ---------------------------------------------------------------------------


class GraphState(TypedDict, total=False):
    chapter_id: str
    pass_number: int
    max_passes: int
    chapter_text: str
    prior_rounds_summary: list[dict]
    last_evaluate_result: EvaluateOutput | None
    last_apply_result: ApplyOutput | None
    evaluate_gate_pending: bool
    evaluate_gate_decision: Literal["approved", "rejected", "pending", "converged"]
    approved_item_ids: list[str]
    apply_gate_pending: bool
    apply_gate_decision: Literal["approved", "rejected", "pending", "converged", "abandoned"]
    pr_number: int | None
    evaluate_refused: bool
    termination_reason: Literal["max_passes", "early_convergence", "evaluate_refused"] | None
    pass_outcome: Literal["in_progress", "completed", "cap_reached", "abandoned"] | None
    review_comments: list[dict]
    governing_excerpts: dict
    next_chapter_context: str | None
    direct_instructions: list[dict]
    hard_constraint_blocked: bool
    hard_constraint_failures: list[str]
    chapter_hydrated: bool


# ---------------------------------------------------------------------------
# Injectable client protocols (spec.md Section 7)
# ---------------------------------------------------------------------------


class AgentClient(Protocol):
    def evaluate(self, payload: EvaluateInput) -> EvaluateOutput: ...

    def apply(self, payload: ApplyInput) -> ApplyOutput: ...


class GitHubClient(Protocol):
    """Read-only against default branch for writes; no default-branch write method exposed."""

    def read_chapter_text(self, chapter_id: str) -> str: ...

    def open_issue(self, title: str, body: str) -> int: ...

    def read_issue_decision(self, issue_number: int) -> GateDecisionResult: ...

    def create_branch(self, branch_name: str, chapter_text: str) -> None: ...

    def open_pr(
        self,
        branch_name: str,
        title: str,
        body: str,
        *,
        draft: bool = False,
    ) -> int: ...

    def read_pr_decision(self, pr_number: int) -> GateDecisionResult: ...


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DEFAULT_BRANCH_NAME = "main"
_APPROVE_ALL_RE = re.compile(r"^\s*approve:\s*all\s*$", re.IGNORECASE)
_APPROVE_IDS_RE = re.compile(r"^\s*approve:\s*(.+)\s*$", re.IGNORECASE)
_REJECT_RE = re.compile(r"^\s*reject\s*$", re.IGNORECASE)
_CONVERGE_RE = re.compile(r"^\s*converge\s*$", re.IGNORECASE)
_ABANDON_RE = re.compile(r"^\s*abandon\s*$", re.IGNORECASE)


def branch_name_for_pass(chapter_id: str, pass_number: int) -> str:
    return f"chapter-{chapter_id}-pass-{pass_number}"


def is_apply_eligible(recommendation: str) -> bool:
    return recommendation in APPLY_ELIGIBLE_RECOMMENDATIONS


def apply_eligible_item_ids(result: EvaluateOutput) -> list[str]:
    ids: list[str] = []
    for item in result.items:
        if is_apply_eligible(item.recommendation):
            ids.append(item.item_id)
    for finding in result.agent_identified_findings:
        if is_apply_eligible(finding.recommendation):
            ids.append(finding.item_id)
    return ids


def parse_gate_comment(
    comment: str,
    apply_eligible_ids: list[str],
) -> GateDecisionResult:
    """Machine-parseable gate comments (spec.md Section 4).

    `approve: all` resolves to the concrete APPLY-eligible ID list at parse time so
    downstream `approved_item_ids` is never ambiguous. `converge` and `abandon` are
    terminal apply-gate decisions (successful vs unsuccessful stop).
    """
    text = comment.strip()
    if _REJECT_RE.match(text):
        return GateDecisionResult(decision="rejected")
    if _CONVERGE_RE.match(text):
        return GateDecisionResult(decision="converged")
    if _ABANDON_RE.match(text):
        return GateDecisionResult(decision="abandoned")
    if _APPROVE_ALL_RE.match(text):
        return GateDecisionResult(decision="approved", approved_item_ids=list(apply_eligible_ids))
    match = _APPROVE_IDS_RE.match(text)
    if match:
        raw_ids = [part.strip() for part in match.group(1).split(",") if part.strip()]
        return GateDecisionResult(decision="approved", approved_item_ids=raw_ids)
    return GateDecisionResult(decision="pending")


def _lookup_item(
    evaluate_result: EvaluateOutput,
    item_id: str,
) -> tuple[str, str | None] | None:
    for item in evaluate_result.items:
        if item.item_id == item_id:
            return item.recommendation, item.minimal_corrected_text
    for finding in evaluate_result.agent_identified_findings:
        if finding.item_id == item_id:
            return finding.recommendation, finding.minimal_corrected_text
    return None


def reconstruct_approved_items(
    evaluate_result: EvaluateOutput,
    approved_item_ids: list[str],
) -> tuple[list[ApprovedItem], list[ApplyInputError]]:
    """Gate carries approved_item_ids; apply_node rebuilds io-contract-apply.md objects."""
    approved: list[ApprovedItem] = []
    input_errors: list[ApplyInputError] = []
    for item_id in approved_item_ids:
        found = _lookup_item(evaluate_result, item_id)
        if found is None:
            input_errors.append(
                ApplyInputError(
                    item_id=item_id,
                    problem="unknown item_id not present in last EVALUATE result",
                )
            )
            continue
        recommendation, corrected = found
        if not is_apply_eligible(recommendation):
            input_errors.append(
                ApplyInputError(
                    item_id=item_id,
                    problem=(
                        f"item recommendation {recommendation!r} is not "
                        "APPLY-eligible (orchestrator approved a non-apply item)"
                    ),
                )
            )
            continue
        if not corrected:
            input_errors.append(
                ApplyInputError(
                    item_id=item_id,
                    problem="APPLY-eligible item missing minimal_corrected_text",
                )
            )
            continue
        approved.append(
            ApprovedItem(
                item_id=item_id,
                recommendation=recommendation,
                minimal_corrected_text=corrected,
            )
        )
    return approved, input_errors


def synthesize_orchestrator_apply_output(
    chapter_text: str,
    input_errors: list[ApplyInputError],
) -> ApplyOutput:
    """APPLY output when orchestrator rejects the payload before calling the agent."""
    return ApplyOutput(
        revised_chapter_text=chapter_text,
        change_log=[],
        hard_constraint_self_check=HardConstraintSelfCheck(
            no_cross_reference_invalidated=True,
            no_section_reordered_added_removed=True,
            no_protected_passage_diluted=True,
            no_code_block_changed=True,
            notes="Apply skipped: orchestrator input validation failed.",
        ),
        input_errors=input_errors,
    )


def format_evaluate_issue_body(result: EvaluateOutput) -> str:
    lines = [
        "| item_id | recommendation | reason |",
        "| --- | --- | --- |",
    ]
    for item in result.items:
        lines.append(f"| {item.item_id} | {item.recommendation} | {item.reason} |")
    for finding in result.agent_identified_findings:
        lines.append(f"| {finding.item_id} | {finding.recommendation} | {finding.reason} |")
    lines.extend(
        [
            "",
            "## Convergence assessment",
            f"scope_trend: {result.convergence_assessment.scope_trend}",
            result.convergence_assessment.comparison_note,
        ]
    )
    return "\n".join(lines)


def format_apply_pr_body(
    apply_result: ApplyOutput,
    evaluate_result: EvaluateOutput | None,
) -> str:
    lines = ["## Post-edit summary"]
    for entry in apply_result.change_log:
        lines.append(
            f"- {entry.before_excerpt} → {entry.item_id} → {entry.section}"
        )
    lines.append("")
    lines.append("## Scope-integrity confirmation")
    check = apply_result.hard_constraint_self_check
    lines.append(
        f"no_cross_reference_invalidated={check.no_cross_reference_invalidated}, "
        f"no_section_reordered_added_removed={check.no_section_reordered_added_removed}, "
        f"no_protected_passage_diluted={check.no_protected_passage_diluted}, "
        f"no_code_block_changed={check.no_code_block_changed}"
    )
    if check.notes:
        lines.append(check.notes)
    if evaluate_result is not None:
        lines.append("")
        lines.append("## Convergence assessment")
        lines.append(f"scope_trend: {evaluate_result.convergence_assessment.scope_trend}")
        lines.append(evaluate_result.convergence_assessment.comparison_note)
    if apply_result.input_errors:
        lines.append("")
        lines.append("## Input errors")
        for err in apply_result.input_errors:
            lines.append(f"- {err.item_id}: {err.problem}")
    return "\n".join(lines)


def failing_hard_constraints(check: HardConstraintSelfCheck) -> list[str]:
    failures: list[str] = []
    for name in (
        "no_cross_reference_invalidated",
        "no_section_reordered_added_removed",
        "no_protected_passage_diluted",
        "no_code_block_changed",
    ):
        if not getattr(check, name):
            failures.append(name)
    return failures


def _default_governing_excerpts(raw: dict | GoverningExcerpts | None) -> GoverningExcerpts:
    if isinstance(raw, GoverningExcerpts):
        return raw
    if raw:
        return GoverningExcerpts.model_validate(raw)
    return GoverningExcerpts(
        defect_categories=[],
        seven_question_checklist=[],
        style_rules=[],
        protected_passages=[],
    )


def _build_prior_round_entry(
    pass_number: int,
    evaluate_result: EvaluateOutput | None,
    apply_result: ApplyOutput,
) -> dict:
    item_count = len(evaluate_result.items) if evaluate_result else 0
    do_not_apply = (
        sum(1 for i in evaluate_result.items if i.recommendation == "DO_NOT_APPLY")
        if evaluate_result
        else 0
    )
    applied_count = len(apply_result.change_log)
    return {
        "pass_number": pass_number,
        "item_count": item_count,
        "applied_count": applied_count,
        "do_not_apply_count": do_not_apply,
    }


@dataclass(frozen=True)
class OrchestratorDeps:
    agent: AgentClient
    github: GitHubClient


def _hydrate_chapter_if_needed(state: GraphState, deps: OrchestratorDeps) -> dict:
    """Pass-1 hydration from GitHub; never re-read after pass 1 begins (spec.md Section 3)."""
    updates: dict = {}
    if state.get("pass_number", 1) == 1 and not state.get("chapter_hydrated"):
        if not state.get("chapter_text"):
            updates["chapter_text"] = deps.github.read_chapter_text(state["chapter_id"])
        updates["chapter_hydrated"] = True
    return updates


# ---------------------------------------------------------------------------
# Nodes (spec.md Section 4)
# ---------------------------------------------------------------------------


def make_evaluate_node(deps: OrchestratorDeps):
    """spec.md Section 4 — evaluate_node; Section 5 — 4th-EVALUATE refusal."""

    def evaluate_node(state: GraphState) -> dict:
        if state["pass_number"] > state["max_passes"]:
            return {
                "evaluate_refused": True,
                "termination_reason": "evaluate_refused",
                "evaluate_gate_pending": False,
            }

        hydration = _hydrate_chapter_if_needed(state, deps)
        chapter_text = hydration.get("chapter_text", state["chapter_text"])
        governing = _default_governing_excerpts(state.get("governing_excerpts"))

        payload = EvaluateInput(
            chapter_id=state["chapter_id"],
            pass_number=state["pass_number"],
            max_passes=state["max_passes"],
            chapter_text=chapter_text,
            prior_rounds_summary=state.get("prior_rounds_summary", []),
            review_comments=[
                ReviewComment.model_validate(c) for c in state.get("review_comments", [])
            ],
            governing_excerpts=governing,
            next_chapter_context=state.get("next_chapter_context"),
            direct_instructions=[
                EvaluateDirectInstruction.model_validate(d)
                for d in state.get("direct_instructions", [])
            ],
        )
        result = deps.agent.evaluate(payload)
        return {
            **hydration,
            "evaluate_refused": False,
            "last_evaluate_result": result,
            "evaluate_gate_pending": True,
            "evaluate_gate_decision": "pending",
            "approved_item_ids": [],
            "pr_number": None,
        }

    return evaluate_node


def make_evaluate_gate_node(deps: OrchestratorDeps):
    """spec.md Section 4 — evaluate_gate_node (GitHub issue, idempotent pause)."""

    def evaluate_gate_node(state: GraphState) -> dict:
        evaluate_result = state["last_evaluate_result"]
        assert evaluate_result is not None

        # pr_number holds the open issue while the evaluate gate is active (spec.md Section 3).
        issue_number = state.get("pr_number")
        if issue_number is None:
            title = (
                f"EVALUATE gate — chapter {state['chapter_id']} "
                f"pass {state['pass_number']}"
            )
            body = format_evaluate_issue_body(evaluate_result)
            issue_number = deps.github.open_issue(title, body)

        decision = deps.github.read_issue_decision(issue_number)

        return {
            "pr_number": issue_number,
            "evaluate_gate_decision": decision.decision,
            "evaluate_gate_pending": decision.decision == "pending",
            "approved_item_ids": decision.approved_item_ids,
        }

    return evaluate_gate_node


def make_apply_node(deps: OrchestratorDeps):
    """spec.md Section 4 — apply_node; reconstructs approved_items from last_evaluate_result."""

    def apply_node(state: GraphState) -> dict:
        evaluate_result = state["last_evaluate_result"]
        assert evaluate_result is not None

        approved_items, input_errors = reconstruct_approved_items(
            evaluate_result,
            state.get("approved_item_ids", []),
        )

        if input_errors:
            result = synthesize_orchestrator_apply_output(
                state["chapter_text"],
                input_errors,
            )
        else:
            apply_instructions = [
                ApplyDirectInstruction(
                    instruction_id=d["instruction_id"],
                    text=d["text"],
                    action=d.get("action", "apply_verbatim"),
                )
                for d in state.get("direct_instructions", [])
            ]

            payload = ApplyInput(
                chapter_id=state["chapter_id"],
                pass_number=state["pass_number"],
                chapter_text=state["chapter_text"],
                approved_items=approved_items,
                direct_instructions=apply_instructions,
                next_chapter_context=state.get("next_chapter_context"),
            )
            result = deps.agent.apply(payload)
        failures = failing_hard_constraints(result.hard_constraint_self_check)
        return {
            "last_apply_result": result,
            "apply_gate_pending": True,
            "apply_gate_decision": "pending",
            "hard_constraint_blocked": bool(failures),
            "hard_constraint_failures": failures,
            "pr_number": None,
        }

    return apply_node


def make_apply_gate_node(deps: OrchestratorDeps):
    """spec.md Section 4 — apply_gate_node; Section 8 — hard-constraint persistence gate."""

    def apply_gate_node(state: GraphState) -> dict:
        apply_result = state["last_apply_result"]
        evaluate_result = state.get("last_evaluate_result")
        assert apply_result is not None

        pr_number = state.get("pr_number")
        branch = branch_name_for_pass(state["chapter_id"], state["pass_number"])

        if pr_number is None:
            deps.github.create_branch(branch, apply_result.revised_chapter_text)
            body = format_apply_pr_body(apply_result, evaluate_result)
            draft = state.get("hard_constraint_blocked", False)
            if draft:
                body += (
                    "\n\n## HARD CONSTRAINT FAILURE — merge blocked\n"
                    "Failing flags: "
                    + ", ".join(state.get("hard_constraint_failures", []))
                )
            title = (
                f"APPLY gate — chapter {state['chapter_id']} "
                f"pass {state['pass_number']}"
            )
            pr_number = deps.github.open_pr(branch, title, body, draft=draft)

        decision = deps.github.read_pr_decision(pr_number)
        return {
            "pr_number": pr_number,
            "apply_gate_decision": decision.decision,
            "apply_gate_pending": decision.decision == "pending",
        }

    return apply_gate_node


def make_increment_pass_node():
    """Helper node: advance pass counter and reset per-pass gate state (spec.md Section 4/5)."""

    def increment_pass_node(state: GraphState) -> dict:
        apply_result = state["last_apply_result"]
        evaluate_result = state.get("last_evaluate_result")
        assert apply_result is not None
        prior = list(state.get("prior_rounds_summary", []))
        prior.append(
            _build_prior_round_entry(state["pass_number"], evaluate_result, apply_result)
        )
        return {
            "pass_number": state["pass_number"] + 1,
            "chapter_text": apply_result.revised_chapter_text,
            "prior_rounds_summary": prior,
            "last_evaluate_result": None,
            "last_apply_result": None,
            "evaluate_gate_pending": False,
            "evaluate_gate_decision": "pending",
            "approved_item_ids": [],
            "apply_gate_pending": False,
            "apply_gate_decision": "pending",
            "pr_number": None,
            "hard_constraint_blocked": False,
            "hard_constraint_failures": [],
            "evaluate_refused": False,
        }

    return increment_pass_node


# ---------------------------------------------------------------------------
# Routing (spec.md Section 5)
# ---------------------------------------------------------------------------


def route_after_evaluate(state: GraphState) -> str:
    """spec.md Section 5 — evaluate_node routing (refusal bypasses evaluate gate)."""
    if state.get("evaluate_refused"):
        return END
    return "evaluate_gate_node"


def route_evaluate_gate(state: GraphState) -> str:
    """spec.md Section 5 — evaluate_gate_node routing."""
    decision = state.get("evaluate_gate_decision", "pending")
    if decision == "approved":
        return "apply_node"
    if decision == "rejected":
        return "evaluate_gate_node"
    return "evaluate_gate_node"


def route_apply_gate(state: GraphState) -> str:
    """spec.md Section 5 — apply_gate_node routing.

    spec.md gap: apply-gate rejection loops apply_gate_node → apply_gate_node
    (re-wait) without advancing pass_number or terminating.
    """
    decision = state.get("apply_gate_decision", "pending")
    if decision == "converged":
        return END
    if decision == "abandoned":
        return END
    if decision == "approved":
        if state["pass_number"] >= state["max_passes"]:
            return END
        return "increment_pass_node"
    if decision == "rejected":
        return "apply_gate_node"
    return "apply_gate_node"


def make_finalize_end_node():
    """Helper node: set termination_reason when apply gate ends at max_passes (Section 5)."""

    def finalize_end_node(state: GraphState) -> dict:
        if state.get("apply_gate_decision") == "abandoned":
            return {"pass_outcome": "abandoned"}
        if state.get("apply_gate_decision") == "converged":
            return {
                "termination_reason": "early_convergence",
                "pass_outcome": "completed",
            }
        if state.get("apply_gate_decision") == "approved" and state["pass_number"] >= state[
            "max_passes"
        ]:
            return {"termination_reason": "max_passes", "pass_outcome": "cap_reached"}
        return {}

    return finalize_end_node


# ---------------------------------------------------------------------------
# Factory (spec.md Section 7)
# ---------------------------------------------------------------------------


def build_orchestrator(
    agent_client: AgentClient,
    github_client: GitHubClient,
    checkpointer: InMemorySaver | None = None,
):
    """Build and compile the Session-1 orchestrator graph (spec.md Section 7)."""
    deps = OrchestratorDeps(agent=agent_client, github=github_client)
    if checkpointer is None:
        checkpointer = InMemorySaver()

    graph = StateGraph(GraphState)
    graph.add_node("evaluate_node", make_evaluate_node(deps))
    graph.add_node("evaluate_gate_node", make_evaluate_gate_node(deps))
    graph.add_node("apply_node", make_apply_node(deps))
    graph.add_node("apply_gate_node", make_apply_gate_node(deps))
    graph.add_node("increment_pass_node", make_increment_pass_node())
    graph.add_node("finalize_end_node", make_finalize_end_node())

    graph.add_edge(START, "evaluate_node")
    graph.add_conditional_edges("evaluate_node", route_after_evaluate)
    graph.add_conditional_edges(
        "evaluate_gate_node",
        route_evaluate_gate,
        {
            "apply_node": "apply_node",
            "evaluate_gate_node": "evaluate_gate_node",
        },
    )
    graph.add_edge("apply_node", "apply_gate_node")
    graph.add_conditional_edges(
        "apply_gate_node",
        route_apply_gate,
        {
            END: "finalize_end_node",
            "increment_pass_node": "increment_pass_node",
            "apply_gate_node": "apply_gate_node",
        },
    )
    graph.add_edge("increment_pass_node", "evaluate_node")
    graph.add_edge("finalize_end_node", END)

    return graph.compile(
        checkpointer=checkpointer,
        interrupt_after=["evaluate_gate_node", "apply_gate_node"],
    )


def initial_state(
    chapter_id: str,
    *,
    chapter_text: str = "",
    pass_number: int = 1,
    max_passes: int = 3,
    review_comments: list[dict] | None = None,
    governing_excerpts: dict | None = None,
    next_chapter_context: str | None = None,
    direct_instructions: list[dict] | None = None,
) -> GraphState:
    """Convenience builder for graph invocation inputs."""
    return GraphState(
        chapter_id=chapter_id,
        pass_number=pass_number,
        max_passes=max_passes,
        chapter_text=chapter_text,
        prior_rounds_summary=[],
        last_evaluate_result=None,
        last_apply_result=None,
        evaluate_gate_pending=False,
        evaluate_gate_decision="pending",
        approved_item_ids=[],
        apply_gate_pending=False,
        apply_gate_decision="pending",
        pr_number=None,
        evaluate_refused=False,
        termination_reason=None,
        review_comments=review_comments or [],
        governing_excerpts=governing_excerpts
        or {
            "defect_categories": [],
            "seven_question_checklist": [],
            "style_rules": [],
            "protected_passages": [],
        },
        next_chapter_context=next_chapter_context,
        direct_instructions=direct_instructions or [],
        hard_constraint_blocked=False,
        hard_constraint_failures=[],
        chapter_hydrated=bool(chapter_text),
        pass_outcome=None,
    )
