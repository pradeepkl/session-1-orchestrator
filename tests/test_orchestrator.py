"""Tests for the Session-1 orchestrator (stub clients only)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pytest
from langgraph.checkpoint.memory import InMemorySaver

from orchestrator import (
    AgentIdentifiedFinding,
    ApplyInput,
    ApplyOutput,
    ChangeLogEntry,
    ConvergenceAssessment,
    EvaluateInput,
    EvaluateOutput,
    GateDecisionResult,
    HardConstraintSelfCheck,
    SuppliedReviewItem,
    apply_eligible_item_ids,
    branch_name_for_pass,
    build_orchestrator,
    initial_state,
    make_evaluate_node,
    OrchestratorDeps,
    parse_gate_comment,
    DEFAULT_BRANCH_NAME,
)


# ---------------------------------------------------------------------------
# Stub clients
# ---------------------------------------------------------------------------


@dataclass
class StubAgentClient:
    evaluate_response: EvaluateOutput | None = None
    apply_response: ApplyOutput | None = None
    calls: list[dict[str, Any]] = field(default_factory=list)

    def evaluate(self, payload: EvaluateInput) -> EvaluateOutput:
        self.calls.append({"method": "evaluate", "payload": payload})
        assert self.evaluate_response is not None
        return self.evaluate_response

    def apply(self, payload: ApplyInput) -> ApplyOutput:
        self.calls.append({"method": "apply", "payload": payload})
        assert self.apply_response is not None
        return self.apply_response

    def count(self, method: str) -> int:
        return sum(1 for c in self.calls if c["method"] == method)


ALLOWED_GITHUB_METHODS = {
    "read_chapter_text",
    "open_issue",
    "read_issue_decision",
    "create_branch",
    "open_pr",
    "read_pr_decision",
}


@dataclass
class StubGitHubClient:
    chapter_text: str = "Original chapter text."
    issue_decision: GateDecisionResult | None = None
    issue_comment: str | None = None
    apply_eligible_ids: list[str] = field(default_factory=list)
    pr_decision: GateDecisionResult = field(
        default_factory=lambda: GateDecisionResult(decision="pending")
    )
    calls: list[dict[str, Any]] = field(default_factory=list)
    _issue_counter: int = 100
    _pr_counter: int = 200

    def read_chapter_text(self, chapter_id: str) -> str:
        self._record("read_chapter_text", chapter_id=chapter_id)
        return self.chapter_text

    def open_issue(self, title: str, body: str) -> int:
        self._record("open_issue", title=title, body=body)
        self._issue_counter += 1
        return self._issue_counter

    def read_issue_decision(self, issue_number: int) -> GateDecisionResult:
        self._record("read_issue_decision", issue_number=issue_number)
        if self.issue_decision is not None:
            return self.issue_decision
        if self.issue_comment is not None:
            return parse_gate_comment(self.issue_comment, self.apply_eligible_ids)
        return GateDecisionResult(decision="pending")

    def create_branch(self, branch_name: str, chapter_text: str) -> None:
        self._record("create_branch", branch_name=branch_name, chapter_text=chapter_text)
        if branch_name == DEFAULT_BRANCH_NAME:
            raise AssertionError("create_branch must not target default branch")

    def open_pr(
        self,
        branch_name: str,
        title: str,
        body: str,
        *,
        draft: bool = False,
    ) -> int:
        self._record(
            "open_pr",
            branch_name=branch_name,
            title=title,
            body=body,
            draft=draft,
        )
        if branch_name == DEFAULT_BRANCH_NAME:
            raise AssertionError("open_pr must not target default branch")
        self._pr_counter += 1
        return self._pr_counter

    def read_pr_decision(self, pr_number: int) -> GateDecisionResult:
        self._record("read_pr_decision", pr_number=pr_number)
        return self.pr_decision

    def write_to_default_branch(self, *_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("write_to_default_branch must never be called")

    def _record(self, method: str, **kwargs: Any) -> None:
        self.calls.append({"method": method, **kwargs})


# ---------------------------------------------------------------------------
# Fixtures / canned responses
# ---------------------------------------------------------------------------


def _review_item(
    item_id: str,
    *,
    recommendation: str = "APPLY",
    corrected: str = "Corrected text.",
    reason: str = "Needs fix.",
) -> SuppliedReviewItem:
    return SuppliedReviewItem(
        item_id=item_id,
        origin="supplied_review",
        priority="MEDIUM",
        signal_to_noise_impact="positive",
        essence_risk="low",
        verbosity_impact="neutral",
        readability_impact="positive",
        repetition_impact="none",
        recommendation=recommendation,
        reason=reason,
        minimal_corrected_text=corrected if recommendation in {"APPLY", "APPLY_SELECTIVELY", "APPLY_WITH_CARE"} else None,
    )


def sample_evaluate_output() -> EvaluateOutput:
    return EvaluateOutput(
        items=[
            _review_item("c1", corrected="Corrected one."),
            _review_item("c2", corrected="Corrected two."),
            _review_item("c3", recommendation="DO_NOT_APPLY", reason="Out of scope."),
        ],
        agent_identified_findings=[
            AgentIdentifiedFinding(
                item_id="f1",
                origin="agent_identified",
                defect_category="precision",
                priority="LOW",
                recommendation="APPLY",
                reason="Agent finding",
                minimal_corrected_text="Finding fix.",
            ),
        ],
        convergence_assessment=ConvergenceAssessment(
            scope_trend="shrinking",
            comparison_note="Still improving.",
        ),
    )


def five_apply_eligible_evaluate_output() -> EvaluateOutput:
    return EvaluateOutput(
        items=[_review_item(f"c{i}", corrected=f"Fix {i}.") for i in range(1, 6)],
        convergence_assessment=ConvergenceAssessment(
            scope_trend="baseline_round_1",
            comparison_note="Pass 1 baseline.",
        ),
    )


def sample_apply_output(
    *,
    revised_text: str = "Revised chapter text.",
    hard_check: HardConstraintSelfCheck | None = None,
) -> ApplyOutput:
    check = hard_check or HardConstraintSelfCheck(
        no_cross_reference_invalidated=True,
        no_section_reordered_added_removed=True,
        no_protected_passage_diluted=True,
        no_code_block_changed=True,
        notes="",
    )
    return ApplyOutput(
        revised_chapter_text=revised_text,
        change_log=[
            ChangeLogEntry(
                item_id="c1",
                section="Opening paragraph",
                before_excerpt="Before text.",
                after_excerpt="After text.",
            )
        ],
        hard_constraint_self_check=check,
    )


def make_graph(
    agent: StubAgentClient,
    github: StubGitHubClient,
    checkpointer: InMemorySaver | None = None,
):
    return build_orchestrator(agent, github, checkpointer=checkpointer or InMemorySaver())


def thread_config(thread_id: str = "test-thread") -> dict:
    return {"configurable": {"thread_id": thread_id}}


def approve_evaluate(
    graph,
    config: dict,
    *,
    approved_item_ids: list[str] | None = None,
) -> None:
    graph.update_state(
        config,
        {
            "evaluate_gate_decision": "approved",
            "evaluate_gate_pending": False,
            "approved_item_ids": approved_item_ids if approved_item_ids is not None else [],
        },
    )


def approve_apply(graph, config: dict) -> None:
    graph.update_state(
        config,
        {
            "apply_gate_decision": "approved",
            "apply_gate_pending": False,
        },
    )


# ---------------------------------------------------------------------------
# Required tests (Section 5)
# ---------------------------------------------------------------------------


def test_every_evaluate_reaches_evaluate_gate_and_pauses():
    agent = StubAgentClient(evaluate_response=sample_evaluate_output())
    github = StubGitHubClient()
    graph = make_graph(agent, github)
    config = thread_config("t-eval-gate")

    graph.invoke(initial_state("ch-1", chapter_text="Chapter."), config)
    state = graph.get_state(config)

    assert agent.count("evaluate") == 1
    assert agent.count("apply") == 0
    assert sum(1 for c in github.calls if c["method"] == "open_issue") == 1
    assert sum(1 for c in github.calls if c["method"] == "open_pr") == 0
    assert state.values["evaluate_gate_pending"] is True
    assert state.next == ("evaluate_gate_node",)


def test_partial_approval_carries_only_approved_ids_into_apply():
    evaluate = sample_evaluate_output()
    agent = StubAgentClient(
        evaluate_response=evaluate,
        apply_response=sample_apply_output(),
    )
    github = StubGitHubClient()
    graph = make_graph(agent, github)
    config = thread_config("t-partial")

    graph.invoke(initial_state("ch-1", chapter_text="Chapter."), config)
    eligible = apply_eligible_item_ids(evaluate)
    assert set(eligible) == {"c1", "c2", "f1"}

    approve_evaluate(graph, config, approved_item_ids=["c1", "f1"])
    graph.invoke(None, config)

    apply_calls = [c for c in agent.calls if c["method"] == "apply"]
    assert len(apply_calls) == 1
    approved_ids = {item.item_id for item in apply_calls[0]["payload"].approved_items}
    assert approved_ids == {"c1", "f1"}
    assert "c2" not in approved_ids


def test_every_apply_reaches_apply_gate_and_opens_pr():
    agent = StubAgentClient(
        evaluate_response=sample_evaluate_output(),
        apply_response=sample_apply_output(),
    )
    github = StubGitHubClient()
    graph = make_graph(agent, github)
    config = thread_config("t-apply-pr")

    graph.invoke(initial_state("ch-1", chapter_text="Chapter."), config)
    approve_evaluate(graph, config, approved_item_ids=["c1"])
    graph.invoke(None, config)

    branch_calls = [c for c in github.calls if c["method"] == "create_branch"]
    pr_calls = [c for c in github.calls if c["method"] == "open_pr"]
    assert len(branch_calls) == 1
    assert len(pr_calls) == 1
    expected_branch = branch_name_for_pass("ch-1", 1)
    assert branch_calls[0]["branch_name"] == expected_branch
    assert pr_calls[0]["branch_name"] == expected_branch


def test_paused_graph_resumes_without_rerunning_completed_calls():
    agent = StubAgentClient(
        evaluate_response=sample_evaluate_output(),
        apply_response=sample_apply_output(),
    )
    github = StubGitHubClient()
    graph = make_graph(agent, github)
    config = thread_config("t-resume")

    graph.invoke(initial_state("ch-1", chapter_text="Chapter."), config)
    assert agent.count("evaluate") == 1

    approve_evaluate(graph, config, approved_item_ids=["c1"])
    graph.invoke(None, config)
    assert agent.count("evaluate") == 1
    assert agent.count("apply") == 1

    approve_apply(graph, config)
    apply_before = agent.count("apply")
    graph.invoke(None, config)
    assert agent.count("apply") == apply_before


def test_chapter_text_persists_across_passes_without_rehydration():
    agent = StubAgentClient(
        evaluate_response=sample_evaluate_output(),
        apply_response=sample_apply_output(revised_text="Pass-1 revised text."),
    )
    github = StubGitHubClient(chapter_text="Hydrated once.")
    graph = make_graph(agent, github)
    config = thread_config("t-persist")

    graph.invoke(initial_state("ch-1"), config)
    reads_after_start = [
        c for c in github.calls if c["method"] == "read_chapter_text"
    ]
    assert len(reads_after_start) == 1

    approve_evaluate(graph, config, approved_item_ids=["c1"])
    graph.invoke(None, config)
    approve_apply(graph, config)
    graph.invoke(None, config)

    state = graph.get_state(config)
    assert state.values["pass_number"] == 2
    assert state.values["chapter_text"] == "Pass-1 revised text."

    agent.evaluate_response = sample_evaluate_output()
    agent.apply_response = sample_apply_output(revised_text="unused")

    graph.invoke(None, config)
    evaluate_calls = [c for c in agent.calls if c["method"] == "evaluate"]
    pass2_payload = evaluate_calls[-1]["payload"]
    assert pass2_payload.chapter_text == "Pass-1 revised text."
    assert sum(1 for c in github.calls if c["method"] == "read_chapter_text") == 1


def test_fourth_evaluate_refused_via_routing():
    agent = StubAgentClient(evaluate_response=sample_evaluate_output())
    github = StubGitHubClient()
    graph = make_graph(agent, github)
    config = thread_config("t-refuse-route")

    state_in = initial_state("ch-1", chapter_text="Chapter.", pass_number=4, max_passes=3)
    graph.invoke(state_in, config)
    final = graph.get_state(config).values

    assert final["evaluate_refused"] is True
    assert final["termination_reason"] == "evaluate_refused"
    assert agent.count("evaluate") == 0
    assert sum(1 for c in github.calls if c["method"] == "open_issue") == 0


def test_fourth_evaluate_refused_direct_node_call():
    agent = StubAgentClient(evaluate_response=sample_evaluate_output())
    github = StubGitHubClient()
    deps = OrchestratorDeps(agent=agent, github=github)
    node = make_evaluate_node(deps)

    result = node(
        initial_state("ch-1", chapter_text="Chapter.", pass_number=4, max_passes=3)
    )
    assert result["evaluate_refused"] is True
    assert agent.count("evaluate") == 0


def test_github_client_never_writes_default_branch():
    agent = StubAgentClient(
        evaluate_response=sample_evaluate_output(),
        apply_response=sample_apply_output(),
    )
    github = StubGitHubClient()
    graph = make_graph(agent, github)
    config = thread_config("t-no-default")

    graph.invoke(initial_state("ch-1", chapter_text="Chapter."), config)

    github.issue_decision = GateDecisionResult(decision="rejected")
    graph.invoke(None, config)
    github.issue_decision = GateDecisionResult(decision="approved", approved_item_ids=["c1"])
    approve_evaluate(graph, config, approved_item_ids=["c1"])
    graph.invoke(None, config)

    github.pr_decision = GateDecisionResult(decision="rejected")
    graph.invoke(None, config)
    github.pr_decision = GateDecisionResult(decision="approved")
    approve_apply(graph, config)
    graph.invoke(None, config)

    for call in github.calls:
        assert call["method"] in ALLOWED_GITHUB_METHODS
        if call["method"] in ("create_branch", "open_pr"):
            assert call["branch_name"] != DEFAULT_BRANCH_NAME


def test_stub_raises_if_default_branch_write_method_invoked():
    github = StubGitHubClient()
    with pytest.raises(AssertionError, match="write_to_default_branch"):
        github.write_to_default_branch("main", "text")


def test_hard_constraint_failure_blocks_mergeable_pr():
    agent = StubAgentClient(
        evaluate_response=sample_evaluate_output(),
        apply_response=sample_apply_output(
            hard_check=HardConstraintSelfCheck(
                no_cross_reference_invalidated=True,
                no_section_reordered_added_removed=True,
                no_protected_passage_diluted=True,
                no_code_block_changed=False,
                notes="Code block touched.",
            )
        ),
    )
    github = StubGitHubClient()
    graph = make_graph(agent, github)
    config = thread_config("t-hard")

    graph.invoke(initial_state("ch-1", chapter_text="Chapter."), config)
    approve_evaluate(graph, config, approved_item_ids=["c1"])
    graph.invoke(None, config)

    state = graph.get_state(config).values
    assert state["hard_constraint_blocked"] is True
    assert "no_code_block_changed" in state["hard_constraint_failures"]

    pr_calls = [c for c in github.calls if c["method"] == "open_pr"]
    assert len(pr_calls) == 1
    assert pr_calls[0]["draft"] is True
    assert "no_code_block_changed" in pr_calls[0]["body"]


# ---------------------------------------------------------------------------
# Additional tests
# ---------------------------------------------------------------------------


def test_evaluate_gate_rejection_loop_no_repost():
    agent = StubAgentClient(evaluate_response=sample_evaluate_output())
    github = StubGitHubClient(
        issue_decision=GateDecisionResult(decision="rejected")
    )
    graph = make_graph(agent, github)
    config = thread_config("t-eval-reject")

    graph.invoke(initial_state("ch-1", chapter_text="Chapter."), config)
    assert sum(1 for c in github.calls if c["method"] == "open_issue") == 1
    pass_before = graph.get_state(config).values["pass_number"]

    graph.invoke(None, config)
    assert sum(1 for c in github.calls if c["method"] == "open_issue") == 1
    assert graph.get_state(config).values["pass_number"] == pass_before
    assert agent.count("apply") == 0


def test_apply_gate_rejection_loop():
    agent = StubAgentClient(
        evaluate_response=sample_evaluate_output(),
        apply_response=sample_apply_output(),
    )
    github = StubGitHubClient(
        pr_decision=GateDecisionResult(decision="rejected")
    )
    graph = make_graph(agent, github)
    config = thread_config("t-apply-reject")

    graph.invoke(initial_state("ch-1", chapter_text="Chapter."), config)
    approve_evaluate(graph, config, approved_item_ids=["c1"])
    graph.invoke(None, config)

    pr_opens = sum(1 for c in github.calls if c["method"] == "open_pr")
    pass_before = graph.get_state(config).values["pass_number"]

    graph.invoke(None, config)
    assert sum(1 for c in github.calls if c["method"] == "open_pr") == pr_opens
    assert graph.get_state(config).values["pass_number"] == pass_before
    assert agent.count("apply") == 1


def test_early_convergence_at_apply_gate_routes_to_end():
    agent = StubAgentClient(
        evaluate_response=sample_evaluate_output(),
        apply_response=sample_apply_output(),
    )
    github = StubGitHubClient()
    graph = make_graph(agent, github)
    config = thread_config("t-converge")

    graph.invoke(initial_state("ch-1", chapter_text="Chapter.", max_passes=3), config)
    approve_evaluate(graph, config, approved_item_ids=["c1"])
    graph.invoke(None, config)

    graph.update_state(
        config,
        {
            "apply_gate_decision": "converged",
            "apply_gate_pending": False,
        },
    )
    graph.invoke(None, config)

    state = graph.get_state(config)
    assert state.values["termination_reason"] == "early_convergence"
    assert state.values["pass_outcome"] == "completed"
    assert state.values["pass_number"] == 1
    assert agent.count("evaluate") == 1


def test_parse_approve_all_resolves_to_concrete_ids():
    evaluate = five_apply_eligible_evaluate_output()
    eligible = apply_eligible_item_ids(evaluate)
    assert len(eligible) == 5

    parsed = parse_gate_comment("approve: all", eligible)
    assert parsed.decision == "approved"
    assert len(parsed.approved_item_ids) == 5
    assert set(parsed.approved_item_ids) == {"c1", "c2", "c3", "c4", "c5"}


def test_approve_all_via_issue_comment_in_gate_node():
    evaluate = five_apply_eligible_evaluate_output()
    agent = StubAgentClient(
        evaluate_response=evaluate,
        apply_response=sample_apply_output(),
    )
    eligible = apply_eligible_item_ids(evaluate)
    github = StubGitHubClient(
        issue_comment="approve: all",
        apply_eligible_ids=eligible,
    )
    graph = make_graph(agent, github)
    config = thread_config("t-approve-all")

    graph.invoke(initial_state("ch-1", chapter_text="Chapter."), config)
    state = graph.get_state(config)
    assert len(state.values["approved_item_ids"]) == 5


def test_empty_approved_list_with_approved_decision_applies_nothing():
    agent = StubAgentClient(
        evaluate_response=sample_evaluate_output(),
        apply_response=sample_apply_output(),
    )
    github = StubGitHubClient()
    graph = make_graph(agent, github)
    config = thread_config("t-empty-approve")

    graph.invoke(initial_state("ch-1", chapter_text="Chapter."), config)
    approve_evaluate(graph, config, approved_item_ids=[])
    graph.invoke(None, config)

    apply_calls = [c for c in agent.calls if c["method"] == "apply"]
    assert len(apply_calls) == 1
    assert apply_calls[0]["payload"].approved_items == []


def test_unknown_approved_item_id_does_not_crash_graph():
    agent = StubAgentClient(
        evaluate_response=sample_evaluate_output(),
        apply_response=sample_apply_output(),
    )
    github = StubGitHubClient()
    graph = make_graph(agent, github)
    config = thread_config("t-bad-id")

    graph.invoke(initial_state("ch-1", chapter_text="Chapter."), config)
    approve_evaluate(graph, config, approved_item_ids=["nonexistent"])
    graph.invoke(None, config)

    assert agent.count("apply") == 0
    state = graph.get_state(config).values
    apply_result = state["last_apply_result"]
    assert apply_result is not None
    assert any(
        e.item_id == "nonexistent" and "unknown item_id" in e.problem
        for e in apply_result.input_errors
    )
    assert state["apply_gate_pending"] is True
    assert state["chapter_text"] == "Chapter."


def test_mixed_valid_and_invalid_approval_batch_is_all_or_nothing():
    agent = StubAgentClient(
        evaluate_response=sample_evaluate_output(),
        apply_response=sample_apply_output(),
    )
    github = StubGitHubClient()
    graph = make_graph(agent, github)
    config = thread_config("t-batch-all-or-nothing")

    graph.invoke(initial_state("ch-1", chapter_text="Chapter."), config)
    approve_evaluate(graph, config, approved_item_ids=["c1", "nonexistent"])
    graph.invoke(None, config)

    assert agent.count("apply") == 0
    apply_result = graph.get_state(config).values["last_apply_result"]
    assert apply_result is not None
    assert any(e.item_id == "nonexistent" for e in apply_result.input_errors)
    assert apply_result.revised_chapter_text == "Chapter."
    assert graph.get_state(config).values["chapter_text"] == "Chapter."


def test_non_apply_eligible_approved_id_reported_as_input_error():
    agent = StubAgentClient(
        evaluate_response=sample_evaluate_output(),
        apply_response=sample_apply_output(),
    )
    github = StubGitHubClient()
    graph = make_graph(agent, github)
    config = thread_config("t-not-eligible")

    graph.invoke(initial_state("ch-1", chapter_text="Chapter."), config)
    approve_evaluate(graph, config, approved_item_ids=["c3"])
    graph.invoke(None, config)

    assert agent.count("apply") == 0
    errors = graph.get_state(config).values["last_apply_result"].input_errors
    assert any(e.item_id == "c3" and "not APPLY-eligible" in e.problem for e in errors)


def test_parse_abandon_recognized_at_apply_gate():
    parsed = parse_gate_comment("abandon", [])
    assert parsed.decision == "abandoned"


def test_abandon_at_evaluate_gate_is_no_op():
    evaluate = sample_evaluate_output()
    agent = StubAgentClient(evaluate_response=evaluate)
    eligible = apply_eligible_item_ids(evaluate)
    github = StubGitHubClient(
        issue_comment="abandon",
        apply_eligible_ids=eligible,
    )
    graph = make_graph(agent, github)
    config = thread_config("t-eval-abandon-noop")

    graph.invoke(initial_state("ch-1", chapter_text="Chapter."), config)
    pass_before = graph.get_state(config).values["pass_number"]
    evaluate_calls_before = agent.count("evaluate")

    graph.invoke(None, config)

    state = graph.get_state(config)
    assert state.values["pass_number"] == pass_before
    assert agent.count("evaluate") == evaluate_calls_before
    assert agent.count("apply") == 0
    assert state.values["evaluate_gate_pending"] is True
    assert state.values["evaluate_gate_decision"] == "pending"
    assert state.values.get("pass_outcome") is None
    assert state.values.get("termination_reason") is None
    assert state.next == ("evaluate_gate_node",)


def test_apply_gate_rejection_then_abandon_routes_to_end():
    agent = StubAgentClient(
        evaluate_response=sample_evaluate_output(),
        apply_response=sample_apply_output(),
    )
    github = StubGitHubClient(
        pr_decision=GateDecisionResult(decision="rejected"),
    )
    graph = make_graph(agent, github)
    config = thread_config("t-abandon")

    graph.invoke(initial_state("ch-1", chapter_text="Chapter."), config)
    approve_evaluate(graph, config, approved_item_ids=["c1"])
    graph.invoke(None, config)

    pass_before = graph.get_state(config).values["pass_number"]
    evaluate_calls_before = agent.count("evaluate")
    apply_calls_before = agent.count("apply")

    graph.invoke(None, config)
    assert graph.get_state(config).values["pass_number"] == pass_before
    assert agent.count("evaluate") == evaluate_calls_before
    assert agent.count("apply") == apply_calls_before

    github.pr_decision = GateDecisionResult(decision="abandoned")
    graph.invoke(None, config)
    graph.invoke(None, config)

    state = graph.get_state(config)
    assert state.values["pass_outcome"] == "abandoned"
    assert state.values["pass_number"] == pass_before
    assert agent.count("evaluate") == evaluate_calls_before
    assert agent.count("apply") == apply_calls_before
    assert state.next == ()
