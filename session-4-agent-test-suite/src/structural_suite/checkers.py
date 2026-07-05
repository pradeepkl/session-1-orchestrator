"""Requirement-scoped structural checkers for EVALUATE/APPLY payloads."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable

from structural_suite.constants import (
    APPLY_ELIGIBLE_RECOMMENDATIONS,
    APPLY_OUTPUT_TOP_LEVEL_KEYS,
    EVALUATE_OUTPUT_TOP_LEVEL_KEYS,
    HARD_CONSTRAINT_HITS,
    ITEM_DIMENSION_FIELDS,
    PRIORITY_VALUES,
    RECOMMENDATION_VALUES,
    SCOPE_TREND_VALUES,
    SELF_CHECK_BOOLEAN_KEYS,
)


class StructuralViolation(Exception):
    def __init__(self, requirement_id: str, message: str) -> None:
        self.requirement_id = requirement_id
        super().__init__(f"{requirement_id}: {message}")


@dataclass
class PayloadBundle:
    evaluate_input: dict[str, Any] | None = None
    evaluate_output: dict[str, Any] | None = None
    apply_input: dict[str, Any] | None = None
    apply_output: dict[str, Any] | None = None


Checker = Callable[[PayloadBundle], None]


def _require(payload: dict[str, Any] | None, name: str, requirement_id: str) -> dict[str, Any]:
    if payload is None:
        raise StructuralViolation(requirement_id, f"missing {name} payload")
    return payload


def _non_empty_string(value: Any, field: str, requirement_id: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise StructuralViolation(requirement_id, f"{field} must be a non-empty string")


def _check_playbook_role_exact_matching_io_contract_schema(bundle: PayloadBundle) -> None:
    req = "playbook.role.exact_matching_io_contract_schema"
    if bundle.evaluate_output is not None:
        keys = set(bundle.evaluate_output.keys())
        if keys != EVALUATE_OUTPUT_TOP_LEVEL_KEYS:
            raise StructuralViolation(req, f"evaluate output keys {keys!r} != {EVALUATE_OUTPUT_TOP_LEVEL_KEYS!r}")
    if bundle.apply_output is not None:
        keys = set(bundle.apply_output.keys())
        if keys != APPLY_OUTPUT_TOP_LEVEL_KEYS:
            raise StructuralViolation(req, f"apply output keys {keys!r} != {APPLY_OUTPUT_TOP_LEVEL_KEYS!r}")
    if bundle.evaluate_output is None and bundle.apply_output is None:
        raise StructuralViolation(req, "need evaluate_output and/or apply_output payload")


def _check_playbook_role_single_task_per_invocation(bundle: PayloadBundle) -> None:
    req = "playbook.role.single_task_per_invocation"
    if bundle.evaluate_input is not None:
        if bundle.evaluate_input.get("task") != "EVALUATE":
            raise StructuralViolation(req, "evaluate input task must be EVALUATE")
    if bundle.apply_input is not None:
        if bundle.apply_input.get("task") != "APPLY":
            raise StructuralViolation(req, "apply input task must be APPLY")
    if bundle.evaluate_input is None and bundle.apply_input is None:
        raise StructuralViolation(req, "need evaluate_input and/or apply_input payload")


def _check_playbook_hc_apply_self_check_before_return(bundle: PayloadBundle) -> None:
    req = "playbook.hard_constraint.apply_self_check_before_return"
    output = _require(bundle.apply_output, "apply_output", req)
    block = output.get("hard_constraint_self_check")
    if not isinstance(block, dict):
        raise StructuralViolation(req, "hard_constraint_self_check block missing")
    if not SELF_CHECK_BOOLEAN_KEYS.issubset(block.keys()):
        raise StructuralViolation(req, "hard_constraint_self_check missing boolean sub-fields")


def _check_playbook_hc_evaluate_rejection_out_of_scope(bundle: PayloadBundle) -> None:
    req = "playbook.hard_constraint.evaluate_rejection_out_of_scope"
    output = _require(bundle.evaluate_output, "evaluate_output", req)
    rejections = output.get("hard_constraint_rejections")
    if not isinstance(rejections, list) or not rejections:
        raise StructuralViolation(req, "expected at least one hard_constraint_rejection")
    rejection = rejections[0]
    if rejection.get("constraint_hit") not in HARD_CONSTRAINT_HITS:
        raise StructuralViolation(req, "constraint_hit must name a hard constraint")
    _non_empty_string(rejection.get("note"), "note", req)


def _check_playbook_hc_evaluate_skips_checklist(bundle: PayloadBundle) -> None:
    req = "playbook.hard_constraint.evaluate_skips_checklist"
    output = _require(bundle.evaluate_output, "evaluate_output", req)
    rejections = output.get("hard_constraint_rejections", [])
    items = output.get("items", [])
    rejected_ids = {r.get("item_id") for r in rejections if isinstance(r, dict)}
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get("item_id") in rejected_ids:
            raise StructuralViolation(req, "rejected item must not appear in items with checklist fields")


def _check_playbook_hc_no_code_listing_changes(bundle: PayloadBundle) -> None:
    req = "playbook.hard_constraint.no_code_listing_changes"
    output = _require(bundle.evaluate_output, "evaluate_output", req)
    rejections = output.get("hard_constraint_rejections", [])
    if not any(r.get("constraint_hit") == "no_code_listing_changes" for r in rejections if isinstance(r, dict)):
        raise StructuralViolation(req, "expected a rejection with constraint_hit no_code_listing_changes")


def _each_item(bundle: PayloadBundle, req: str) -> list[dict[str, Any]]:
    output = _require(bundle.evaluate_output, "evaluate_output", req)
    items = output.get("items")
    if not isinstance(items, list) or not items:
        raise StructuralViolation(req, "items must be a non-empty list")
    return [item for item in items if isinstance(item, dict)]


def _check_item_field_present(field: str, requirement_id: str) -> Checker:
    def _checker(bundle: PayloadBundle) -> None:
        for item in _each_item(bundle, requirement_id):
            _non_empty_string(item.get(field), field, requirement_id)

    return _checker


def _check_playbook_evaluate_agent_identified_origin_tag(bundle: PayloadBundle) -> None:
    req = "playbook.evaluate.agent_identified_origin_tag"
    output = _require(bundle.evaluate_output, "evaluate_output", req)
    findings = output.get("agent_identified_findings", [])
    if not findings:
        raise StructuralViolation(req, "need at least one agent_identified finding")
    for finding in findings:
        if finding.get("origin") != "agent_identified":
            raise StructuralViolation(req, "agent finding origin must be agent_identified")


def _check_playbook_evaluate_convergence_computed_from_prior_rounds(bundle: PayloadBundle) -> None:
    req = "playbook.evaluate.convergence_computed_from_prior_rounds"
    inp = _require(bundle.evaluate_input, "evaluate_input", req)
    output = _require(bundle.evaluate_output, "evaluate_output", req)
    if inp.get("prior_rounds_summary"):
        assessment = output.get("convergence_assessment")
        if not isinstance(assessment, dict):
            raise StructuralViolation(req, "convergence_assessment required when prior rounds exist")
        _non_empty_string(assessment.get("comparison_note"), "comparison_note", req)
        if "round" not in assessment["comparison_note"].lower():
            raise StructuralViolation(req, "comparison_note must reference prior round facts")


def _check_playbook_evaluate_hard_constraints_checked_first(bundle: PayloadBundle) -> None:
    req = "playbook.evaluate.hard_constraints_checked_first"
    output = _require(bundle.evaluate_output, "evaluate_output", req)
    rejections = output.get("hard_constraint_rejections", [])
    if not rejections:
        raise StructuralViolation(req, "fixture needs hard_constraint_rejections to exercise ordering")
    rejected_ids = {r.get("item_id") for r in rejections if isinstance(r, dict)}
    for item in output.get("items", []):
        if isinstance(item, dict) and item.get("item_id") in rejected_ids:
            raise StructuralViolation(req, "hard-constraint-hit comment must not be fully evaluated in items")


def _check_enum_on_items(field: str, allowed: frozenset[str], req: str) -> Checker:
    def _checker(bundle: PayloadBundle) -> None:
        for item in _each_item(bundle, req):
            value = item.get(field)
            if value not in allowed:
                raise StructuralViolation(req, f"{field} value {value!r} not in {sorted(allowed)}")

    return _checker


def _check_playbook_evaluate_seven_dimensions_always_written(bundle: PayloadBundle) -> None:
    req = "playbook.evaluate.seven_dimensions_always_written"
    for item in _each_item(bundle, req):
        for field in ITEM_DIMENSION_FIELDS:
            if field not in item:
                raise StructuralViolation(req, f"item missing dimension field {field}")
            if field in {"priority", "recommendation"}:
                continue
            _non_empty_string(item.get(field), field, req)


def _check_playbook_evaluate_return_evaluate_contract_only(bundle: PayloadBundle) -> None:
    req = "playbook.evaluate.return_evaluate_contract_only"
    output = _require(bundle.evaluate_output, "evaluate_output", req)
    if set(output.keys()) != EVALUATE_OUTPUT_TOP_LEVEL_KEYS:
        raise StructuralViolation(req, "extra or missing top-level evaluate output fields")


def _check_playbook_apply_change_log_per_approved_item(bundle: PayloadBundle) -> None:
    req = "playbook.apply.change_log_per_approved_item"
    inp = _require(bundle.apply_input, "apply_input", req)
    output = _require(bundle.apply_output, "apply_output", req)
    approved_ids = {item["item_id"] for item in inp.get("approved_items", []) if isinstance(item, dict)}
    logged_ids = {entry.get("item_id") for entry in output.get("change_log", []) if isinstance(entry, dict)}
    if not approved_ids.issubset(logged_ids):
        raise StructuralViolation(req, "change_log must include every approved item")


def _check_playbook_apply_closing_bridge_no_chapter_number(bundle: PayloadBundle) -> None:
    req = "playbook.apply.closing_bridge_no_chapter_number"
    output = _require(bundle.apply_output, "apply_output", req)
    text = output.get("revised_chapter_text", "")
    if re.search(r"\bchapter\s+\d+\b", text, re.IGNORECASE):
        raise StructuralViolation(req, "revised chapter text must not reference chapter numbers")


def _check_playbook_apply_closing_bridge_no_next_chapter_phrasing(bundle: PayloadBundle) -> None:
    req = "playbook.apply.closing_bridge_no_next_chapter_phrasing"
    output = _require(bundle.apply_output, "apply_output", req)
    text = output.get("revised_chapter_text", "")
    if re.search(r"next chapter", text, re.IGNORECASE):
        raise StructuralViolation(req, "revised chapter text must not use next-chapter phrasing")


def _check_playbook_apply_hard_constraint_boolean_self_check_block(bundle: PayloadBundle) -> None:
    req = "playbook.apply.hard_constraint_boolean_self_check_block"
    output = _require(bundle.apply_output, "apply_output", req)
    block = output.get("hard_constraint_self_check")
    if not isinstance(block, dict):
        raise StructuralViolation(req, "missing hard_constraint_self_check block")
    for key in SELF_CHECK_BOOLEAN_KEYS:
        if not isinstance(block.get(key), bool):
            raise StructuralViolation(req, f"{key} must be a boolean")


def _check_playbook_apply_rejects_do_not_apply_as_input_error(bundle: PayloadBundle) -> None:
    req = "playbook.apply.rejects_do_not_apply_as_input_error"
    inp = _require(bundle.apply_input, "apply_input", req)
    output = _require(bundle.apply_output, "apply_output", req)
    bad_ids = {
        item.get("item_id")
        for item in inp.get("approved_items", [])
        if isinstance(item, dict) and item.get("recommendation") == "DO_NOT_APPLY"
    }
    if not bad_ids:
        raise StructuralViolation(req, "fixture must include DO_NOT_APPLY in approved_items")
    reported = {err.get("item_id") for err in output.get("input_errors", []) if isinstance(err, dict)}
    if not bad_ids.issubset(reported):
        raise StructuralViolation(req, "DO_NOT_APPLY items must be reported in input_errors")


def _check_playbook_apply_restructure_flags_input_error(bundle: PayloadBundle) -> None:
    req = "playbook.apply.restructure_flags_input_error"
    output = _require(bundle.apply_output, "apply_output", req)
    errors = output.get("input_errors", [])
    if not any("restruct" in (err.get("problem") or "").lower() for err in errors if isinstance(err, dict)):
        raise StructuralViolation(req, "expected restructure problem in input_errors")


def _check_playbook_apply_return_apply_contract_only(bundle: PayloadBundle) -> None:
    req = "playbook.apply.return_apply_contract_only"
    output = _require(bundle.apply_output, "apply_output", req)
    if set(output.keys()) != APPLY_OUTPUT_TOP_LEVEL_KEYS:
        raise StructuralViolation(req, "extra or missing top-level apply output fields")


def _check_evaluate_input_task(bundle: PayloadBundle) -> None:
    req = "io_evaluate.input.task_is_evaluate"
    inp = _require(bundle.evaluate_input, "evaluate_input", req)
    if inp.get("task") != "EVALUATE":
        raise StructuralViolation(req, "task must be EVALUATE")


def _check_present(path: str, req: str, root: str) -> Checker:
    def _checker(bundle: PayloadBundle) -> None:
        payload = _require(getattr(bundle, root), root, req)
        parts = path.split(".")
        cur: Any = payload
        for part in parts:
            if not isinstance(cur, dict) or part not in cur:
                raise StructuralViolation(req, f"missing field {path}")
            cur = cur[part]
        if isinstance(cur, str) and not cur.strip():
            raise StructuralViolation(req, f"{path} must be non-empty")

    return _checker


def _check_evaluate_input_review_comments_array(bundle: PayloadBundle) -> None:
    req = "io_evaluate.input.review_comments_array"
    inp = _require(bundle.evaluate_input, "evaluate_input", req)
    if not isinstance(inp.get("review_comments"), list):
        raise StructuralViolation(req, "review_comments must be an array")


def _check_evaluate_input_review_comments_may_be_empty(bundle: PayloadBundle) -> None:
    req = "io_evaluate.input.review_comments_may_be_empty"
    inp = _require(bundle.evaluate_input, "evaluate_input", req)
    if "review_comments" not in inp or not isinstance(inp["review_comments"], list):
        raise StructuralViolation(req, "review_comments must be a list (possibly empty)")


def _check_evaluate_input_review_comment_id_and_text(bundle: PayloadBundle) -> None:
    req = "io_evaluate.input.review_comment_id_and_text"
    inp = _require(bundle.evaluate_input, "evaluate_input", req)
    comments = inp.get("review_comments", [])
    if not comments:
        raise StructuralViolation(req, "fixture needs at least one review comment")
    comment = comments[0]
    _non_empty_string(comment.get("comment_id"), "comment_id", req)
    _non_empty_string(comment.get("text"), "text", req)


def _check_evaluate_input_direct_instructions_id_and_text(bundle: PayloadBundle) -> None:
    req = "io_evaluate.input.direct_instructions_id_and_text"
    inp = _require(bundle.evaluate_input, "evaluate_input", req)
    instructions = inp.get("direct_instructions", [])
    if not instructions:
        raise StructuralViolation(req, "fixture needs direct_instructions")
    entry = instructions[0]
    _non_empty_string(entry.get("instruction_id"), "instruction_id", req)
    _non_empty_string(entry.get("text"), "text", req)


def _check_evaluate_input_governing_excerpts_defect_categories(bundle: PayloadBundle) -> None:
    req = "io_evaluate.input.governing_excerpts_defect_categories"
    inp = _require(bundle.evaluate_input, "evaluate_input", req)
    categories = inp.get("governing_excerpts", {}).get("defect_categories")
    if not isinstance(categories, list) or len(categories) < 10:
        raise StructuralViolation(req, "defect_categories must list all ten categories")


def _check_evaluate_input_governing_excerpts_protected_passages(bundle: PayloadBundle) -> None:
    req = "io_evaluate.input.governing_excerpts_protected_passages"
    inp = _require(bundle.evaluate_input, "evaluate_input", req)
    passages = inp.get("governing_excerpts", {}).get("protected_passages")
    if not isinstance(passages, list) or not passages:
        raise StructuralViolation(req, "protected_passages must be a non-empty list")
    passage = passages[0]
    _non_empty_string(passage.get("name"), "name", req)
    _non_empty_string(passage.get("text_anchor"), "text_anchor", req)


def _check_evaluate_input_prior_rounds_summary_empty_on_pass_one(bundle: PayloadBundle) -> None:
    req = "io_evaluate.input.prior_rounds_summary_empty_on_pass_one"
    inp = _require(bundle.evaluate_input, "evaluate_input", req)
    if inp.get("pass_number") == 1 and inp.get("prior_rounds_summary") != []:
        raise StructuralViolation(req, "prior_rounds_summary must be [] on pass 1")


def _check_evaluate_input_prior_rounds_summary_entry_shape(bundle: PayloadBundle) -> None:
    req = "io_evaluate.input.prior_rounds_summary_entry_shape"
    inp = _require(bundle.evaluate_input, "evaluate_input", req)
    summary = inp.get("prior_rounds_summary", [])
    if not summary:
        raise StructuralViolation(req, "fixture needs prior_rounds_summary entry")
    entry = summary[0]
    required = {"pass_number", "item_count", "severity_mix", "applied_count", "do_not_apply_count"}
    if not required.issubset(entry.keys()):
        raise StructuralViolation(req, f"prior round entry missing keys from {required}")


def _check_evaluate_input_next_chapter_context_nullable(bundle: PayloadBundle) -> None:
    req = "io_evaluate.input.next_chapter_context_nullable"
    inp = _require(bundle.evaluate_input, "evaluate_input", req)
    if "next_chapter_context" not in inp:
        raise StructuralViolation(req, "next_chapter_context key must be present (string or null)")


def _check_evaluate_output_items_array(bundle: PayloadBundle) -> None:
    req = "io_evaluate.output.items_array"
    output = _require(bundle.evaluate_output, "evaluate_output", req)
    if not isinstance(output.get("items"), list):
        raise StructuralViolation(req, "items must be an array")


def _check_evaluate_output_item_origin_supplied_review(bundle: PayloadBundle) -> None:
    req = "io_evaluate.output.item_origin_supplied_review"
    for item in _each_item(bundle, req):
        if item.get("origin") != "supplied_review":
            raise StructuralViolation(req, "supplied review item origin must be supplied_review")


def _check_evaluate_output_item_priority_enum(bundle: PayloadBundle) -> None:
    req = "io_evaluate.output.item_priority_enum"
    for item in _each_item(bundle, req):
        if item.get("priority") not in PRIORITY_VALUES:
            raise StructuralViolation(req, "invalid priority enum")


def _check_evaluate_output_recommendation_enum_values(bundle: PayloadBundle) -> None:
    req = "io_evaluate.output.recommendation_enum_values"
    for item in _each_item(bundle, req):
        if item.get("recommendation") not in RECOMMENDATION_VALUES:
            raise StructuralViolation(req, "invalid recommendation enum")


def _check_evaluate_output_minimal_corrected_text_nullability(bundle: PayloadBundle) -> None:
    req = "io_evaluate.output.minimal_corrected_text_nullability_matches_recommendation"
    for item in _each_item(bundle, req):
        rec = item.get("recommendation")
        text = item.get("minimal_corrected_text")
        if rec in APPLY_ELIGIBLE_RECOMMENDATIONS and not text:
            raise StructuralViolation(req, "minimal_corrected_text required for APPLY recommendations")
        if rec not in APPLY_ELIGIBLE_RECOMMENDATIONS and text is not None:
            raise StructuralViolation(req, "minimal_corrected_text must be null when not APPLY-eligible")


def _check_evaluate_output_hard_constraint_rejections_array(bundle: PayloadBundle) -> None:
    req = "io_evaluate.output.hard_constraint_rejections_array"
    output = _require(bundle.evaluate_output, "evaluate_output", req)
    if not isinstance(output.get("hard_constraint_rejections"), list):
        raise StructuralViolation(req, "hard_constraint_rejections must be an array")


def _check_evaluate_output_rejection_fields(bundle: PayloadBundle, field: str) -> None:
    req = f"io_evaluate.output.rejection_{field}_present"
    output = _require(bundle.evaluate_output, "evaluate_output", req)
    rejections = output.get("hard_constraint_rejections", [])
    if not rejections:
        raise StructuralViolation(req, "need at least one rejection")
    rejection = rejections[0]
    _non_empty_string(rejection.get(field), field, req)


def _check_evaluate_output_hard_constraint_rejection_skips_checklist(bundle: PayloadBundle) -> None:
    req = "io_evaluate.output.hard_constraint_rejection_skips_checklist"
    output = _require(bundle.evaluate_output, "evaluate_output", req)
    rejections = output.get("hard_constraint_rejections", [])
    items = output.get("items", [])
    rejected_ids = {r.get("item_id") for r in rejections if isinstance(r, dict)}
    for item in items:
        if isinstance(item, dict) and item.get("item_id") in rejected_ids:
            raise StructuralViolation(req, "rejected item must not appear in items with checklist fields")


def _check_evaluate_output_agent_identified_findings_array(bundle: PayloadBundle) -> None:
    req = "io_evaluate.output.agent_identified_findings_array"
    output = _require(bundle.evaluate_output, "evaluate_output", req)
    if not isinstance(output.get("agent_identified_findings"), list):
        raise StructuralViolation(req, "agent_identified_findings must be an array")


def _check_agent_finding_field(field: str, req: str) -> Checker:
    def _checker(bundle: PayloadBundle) -> None:
        output = _require(bundle.evaluate_output, "evaluate_output", req)
        findings = output.get("agent_identified_findings", [])
        if not findings:
            raise StructuralViolation(req, "need at least one agent_identified finding")
        finding = findings[0]
        value = finding.get(field)
        if field in {"reason", "defect_category"}:
            _non_empty_string(value, field, req)
        elif field == "origin":
            if value != "agent_identified":
                raise StructuralViolation(req, "origin must be agent_identified")
        elif field == "priority":
            if value not in PRIORITY_VALUES:
                raise StructuralViolation(req, "invalid priority")
        elif field == "recommendation":
            if value not in RECOMMENDATION_VALUES:
                raise StructuralViolation(req, "invalid recommendation")
        elif field == "item_id":
            _non_empty_string(value, "item_id", req)

    return _checker


def _check_evaluate_output_agent_identified_defect_category_matches_supplied(bundle: PayloadBundle) -> None:
    req = "io_evaluate.output.agent_identified_defect_category_matches_supplied"
    inp = _require(bundle.evaluate_input, "evaluate_input", req)
    output = _require(bundle.evaluate_output, "evaluate_output", req)
    allowed = set(inp.get("governing_excerpts", {}).get("defect_categories", []))
    for finding in output.get("agent_identified_findings", []):
        if isinstance(finding, dict) and finding.get("defect_category") not in allowed:
            raise StructuralViolation(req, "defect_category must match a supplied category")


def _check_evaluate_output_agent_identified_finding_has_corrected_text_field(bundle: PayloadBundle) -> None:
    req = "io_evaluate.output.agent_identified_finding_has_corrected_text_field"
    output = _require(bundle.evaluate_output, "evaluate_output", req)
    for finding in output.get("agent_identified_findings", []):
        if isinstance(finding, dict) and "minimal_corrected_text" not in finding:
            raise StructuralViolation(req, "agent finding missing minimal_corrected_text field")


def _check_evaluate_output_agent_identified_corrected_text_nullability(bundle: PayloadBundle) -> None:
    req = "io_evaluate.output.agent_identified_finding_corrected_text_nullability_matches_recommendation"
    output = _require(bundle.evaluate_output, "evaluate_output", req)
    for finding in output.get("agent_identified_findings", []):
        if not isinstance(finding, dict):
            continue
        rec = finding.get("recommendation")
        text = finding.get("minimal_corrected_text")
        if rec in APPLY_ELIGIBLE_RECOMMENDATIONS and not text:
            raise StructuralViolation(req, "agent finding minimal_corrected_text required for APPLY recs")
        if rec not in APPLY_ELIGIBLE_RECOMMENDATIONS and text is not None:
            raise StructuralViolation(req, "agent finding minimal_corrected_text must be null otherwise")


def _check_evaluate_output_supplied_and_agent_identified_same_nullability(bundle: PayloadBundle) -> None:
    req = "io_evaluate.output.supplied_and_agent_identified_corrected_text_same_nullability"
    output = _require(bundle.evaluate_output, "evaluate_output", req)

    def _rule(rec: str | None, text: Any) -> bool:
        if rec in APPLY_ELIGIBLE_RECOMMENDATIONS:
            return bool(text)
        return text is None

    for item in output.get("items", []):
        if isinstance(item, dict) and not _rule(item.get("recommendation"), item.get("minimal_corrected_text")):
            raise StructuralViolation(req, "supplied item violates corrected-text nullability rule")
    for finding in output.get("agent_identified_findings", []):
        if isinstance(finding, dict) and not _rule(
            finding.get("recommendation"), finding.get("minimal_corrected_text")
        ):
            raise StructuralViolation(req, "agent finding violates corrected-text nullability rule")


def _check_evaluate_output_convergence_assessment_present(bundle: PayloadBundle) -> None:
    req = "io_evaluate.output.convergence_assessment_present"
    output = _require(bundle.evaluate_output, "evaluate_output", req)
    if not isinstance(output.get("convergence_assessment"), dict):
        raise StructuralViolation(req, "convergence_assessment object required")


def _check_evaluate_output_scope_trend_enum(bundle: PayloadBundle) -> None:
    req = "io_evaluate.output.scope_trend_enum_values"
    output = _require(bundle.evaluate_output, "evaluate_output", req)
    trend = output.get("convergence_assessment", {}).get("scope_trend")
    if trend not in SCOPE_TREND_VALUES:
        raise StructuralViolation(req, "invalid scope_trend enum")


def _check_evaluate_output_scope_trend_present(bundle: PayloadBundle) -> None:
    req = "io_evaluate.output.scope_trend_present"
    output = _require(bundle.evaluate_output, "evaluate_output", req)
    _non_empty_string(
        output.get("convergence_assessment", {}).get("scope_trend"),
        "scope_trend",
        req,
    )


def _check_evaluate_output_comparison_note_present(bundle: PayloadBundle) -> None:
    req = "io_evaluate.output.comparison_note_present"
    output = _require(bundle.evaluate_output, "evaluate_output", req)
    _non_empty_string(
        output.get("convergence_assessment", {}).get("comparison_note"),
        "comparison_note",
        req,
    )


def _check_evaluate_output_item_string_field(field: str, req: str) -> Checker:
    def _checker(bundle: PayloadBundle) -> None:
        for item in _each_item(bundle, req):
            _non_empty_string(item.get(field), field, req)

    return _checker


def _check_evaluate_output_item_has_field(
    bundle: PayloadBundle, field: str, req: str
) -> None:
    for item in _each_item(bundle, req):
        if field not in item:
            raise StructuralViolation(req, f"item missing field {field}")


def _check_apply_input_task(bundle: PayloadBundle) -> None:
    req = "io_apply.input.task_is_apply"
    inp = _require(bundle.apply_input, "apply_input", req)
    if inp.get("task") != "APPLY":
        raise StructuralViolation(req, "task must be APPLY")


def _check_apply_input_approved_items_array(bundle: PayloadBundle) -> None:
    req = "io_apply.input.approved_items_array"
    inp = _require(bundle.apply_input, "apply_input", req)
    if not isinstance(inp.get("approved_items"), list):
        raise StructuralViolation(req, "approved_items must be an array")


def _check_apply_input_approved_item_field(field: str, req: str) -> Checker:
    def _checker(bundle: PayloadBundle) -> None:
        inp = _require(bundle.apply_input, "apply_input", req)
        items = inp.get("approved_items", [])
        if not items:
            raise StructuralViolation(req, "need approved_items entry")
        item = items[0]
        value = item.get(field)
        if field == "recommendation":
            if value not in APPLY_ELIGIBLE_RECOMMENDATIONS:
                raise StructuralViolation(req, "approved item recommendation must be APPLY-eligible")
        else:
            _non_empty_string(value, field, req)

    return _checker


def _check_apply_input_direct_instruction_action_field(bundle: PayloadBundle) -> None:
    req = "io_apply.input.direct_instruction_action_field"
    inp = _require(bundle.apply_input, "apply_input", req)
    instructions = inp.get("direct_instructions", [])
    if not instructions:
        raise StructuralViolation(req, "need direct_instructions entry")
    _non_empty_string(instructions[0].get("action"), "action", req)


def _check_apply_input_invalid_recommendation_reported(bundle: PayloadBundle) -> None:
    req = "io_apply.input.invalid_recommendation_reported_in_input_errors"
    inp = _require(bundle.apply_input, "apply_input", req)
    output = _require(bundle.apply_output, "apply_output", req)
    bad_ids = {
        item.get("item_id")
        for item in inp.get("approved_items", [])
        if isinstance(item, dict) and item.get("recommendation") == "DO_NOT_APPLY"
    }
    if not bad_ids:
        raise StructuralViolation(req, "fixture must include DO_NOT_APPLY in approved_items")
    reported = {err.get("item_id") for err in output.get("input_errors", []) if isinstance(err, dict)}
    if not bad_ids.issubset(reported):
        raise StructuralViolation(req, "DO_NOT_APPLY items must be reported in input_errors")


def _check_apply_output_array(field: str, req: str) -> Checker:
    def _checker(bundle: PayloadBundle) -> None:
        output = _require(bundle.apply_output, "apply_output", req)
        if not isinstance(output.get(field), list):
            raise StructuralViolation(req, f"{field} must be an array")

    return _checker


def _check_apply_output_change_log_field(field: str, req: str) -> Checker:
    def _checker(bundle: PayloadBundle) -> None:
        output = _require(bundle.apply_output, "apply_output", req)
        entries = output.get("change_log", [])
        if not entries:
            raise StructuralViolation(req, "need change_log entry")
        _non_empty_string(entries[0].get(field), field, req)

    return _checker


def _check_apply_output_deviation_fields(bundle: PayloadBundle, field: str) -> None:
    req = f"io_apply.output.deviation_{field}_present"
    output = _require(bundle.apply_output, "apply_output", req)
    deviations = output.get("deviations_from_review_wording", [])
    if not deviations:
        raise StructuralViolation(req, "need deviations_from_review_wording entry")
    if field == "item_id":
        _non_empty_string(deviations[0].get("item_id"), "item_id", req)
    else:
        _non_empty_string(deviations[0].get("reason"), "reason", req)


def _check_apply_output_input_error_field(field: str, req: str) -> Checker:
    def _checker(bundle: PayloadBundle) -> None:
        output = _require(bundle.apply_output, "apply_output", req)
        errors = output.get("input_errors", [])
        if not errors:
            raise StructuralViolation(req, "need input_errors entry for field check")
        _non_empty_string(errors[0].get(field), field, req)

    return _checker


def _check_self_check_boolean(field: str, req: str) -> Checker:
    def _checker(bundle: PayloadBundle) -> None:
        output = _require(bundle.apply_output, "apply_output", req)
        block = output.get("hard_constraint_self_check", {})
        if not isinstance(block.get(field), bool):
            raise StructuralViolation(req, f"{field} must be a boolean")

    return _checker


def _check_self_check_notes_populated_on_failure(bundle: PayloadBundle) -> None:
    req = "io_apply.output.hard_constraint_self_check_notes_populated_on_failure"
    output = _require(bundle.apply_output, "apply_output", req)
    block = output.get("hard_constraint_self_check", {})
    any_false = any(block.get(key) is False for key in SELF_CHECK_BOOLEAN_KEYS)
    notes = block.get("notes", "")
    if any_false and not str(notes).strip():
        raise StructuralViolation(req, "notes must be populated when any self-check boolean is false")
    if not any_false and str(notes).strip():
        raise StructuralViolation(req, "notes should be empty when all self-check booleans are true")


def _check_meta_amendment_supersedes(bundle: PayloadBundle) -> None:
    req = "meta.amendment_1_supersedes_base_contract_for_agent_identified_findings"
    output = _require(bundle.evaluate_output, "evaluate_output", req)
    findings = output.get("agent_identified_findings", [])
    apply_recommended = [
        f for f in findings if isinstance(f, dict) and f.get("recommendation") in APPLY_ELIGIBLE_RECOMMENDATIONS
    ]
    if not apply_recommended:
        raise StructuralViolation(req, "fixture needs APPLY-recommended agent finding")
    for finding in apply_recommended:
        if "minimal_corrected_text" not in finding:
            raise StructuralViolation(req, "amended shape requires minimal_corrected_text on agent findings")
        if not finding.get("minimal_corrected_text"):
            raise StructuralViolation(req, "minimal_corrected_text must be non-null for APPLY recommendations")


REGISTRY: dict[str, Checker] = {
    "playbook.role.exact_matching_io_contract_schema": _check_playbook_role_exact_matching_io_contract_schema,
    "playbook.role.single_task_per_invocation": _check_playbook_role_single_task_per_invocation,
    "playbook.hard_constraint.apply_self_check_before_return": _check_playbook_hc_apply_self_check_before_return,
    "playbook.hard_constraint.evaluate_rejection_out_of_scope": _check_playbook_hc_evaluate_rejection_out_of_scope,
    "playbook.hard_constraint.evaluate_skips_checklist": _check_playbook_hc_evaluate_skips_checklist,
    "playbook.hard_constraint.no_code_listing_changes": _check_playbook_hc_no_code_listing_changes,
    "playbook.evaluate.agent_identified_origin_tag": _check_playbook_evaluate_agent_identified_origin_tag,
    "playbook.evaluate.convergence_computed_from_prior_rounds": _check_playbook_evaluate_convergence_computed_from_prior_rounds,
    "playbook.evaluate.essence_risk_present": _check_item_field_present(
        "essence_risk", "playbook.evaluate.essence_risk_present"
    ),
    "playbook.evaluate.hard_constraints_checked_first": _check_playbook_evaluate_hard_constraints_checked_first,
    "playbook.evaluate.priority_enum_values": _check_enum_on_items(
        "priority", PRIORITY_VALUES, "playbook.evaluate.priority_enum_values"
    ),
    "playbook.evaluate.priority_field_present": _check_item_field_present(
        "priority", "playbook.evaluate.priority_field_present"
    ),
    "playbook.evaluate.readability_impact_present": _check_item_field_present(
        "readability_impact", "playbook.evaluate.readability_impact_present"
    ),
    "playbook.evaluate.reason_field_present": _check_item_field_present(
        "reason", "playbook.evaluate.reason_field_present"
    ),
    "playbook.evaluate.recommendation_enum_values": _check_enum_on_items(
        "recommendation", RECOMMENDATION_VALUES, "playbook.evaluate.recommendation_enum_values"
    ),
    "playbook.evaluate.recommendation_field_present": _check_item_field_present(
        "recommendation", "playbook.evaluate.recommendation_field_present"
    ),
    "playbook.evaluate.repetition_impact_present": _check_item_field_present(
        "repetition_impact", "playbook.evaluate.repetition_impact_present"
    ),
    "playbook.evaluate.return_evaluate_contract_only": _check_playbook_evaluate_return_evaluate_contract_only,
    "playbook.evaluate.seven_dimensions_always_written": _check_playbook_evaluate_seven_dimensions_always_written,
    "playbook.evaluate.signal_to_noise_impact_present": _check_item_field_present(
        "signal_to_noise_impact", "playbook.evaluate.signal_to_noise_impact_present"
    ),
    "playbook.evaluate.verbosity_impact_present": _check_item_field_present(
        "verbosity_impact", "playbook.evaluate.verbosity_impact_present"
    ),
    "playbook.apply.change_log_per_approved_item": _check_playbook_apply_change_log_per_approved_item,
    "playbook.apply.closing_bridge_no_chapter_number": _check_playbook_apply_closing_bridge_no_chapter_number,
    "playbook.apply.closing_bridge_no_next_chapter_phrasing": _check_playbook_apply_closing_bridge_no_next_chapter_phrasing,
    "playbook.apply.hard_constraint_boolean_self_check_block": _check_playbook_apply_hard_constraint_boolean_self_check_block,
    "playbook.apply.rejects_do_not_apply_as_input_error": _check_playbook_apply_rejects_do_not_apply_as_input_error,
    "playbook.apply.restructure_flags_input_error": _check_playbook_apply_restructure_flags_input_error,
    "playbook.apply.return_apply_contract_only": _check_playbook_apply_return_apply_contract_only,
    "io_evaluate.input.task_is_evaluate": _check_evaluate_input_task,
    "io_evaluate.input.chapter_id_present": _check_present("chapter_id", "io_evaluate.input.chapter_id_present", "evaluate_input"),
    "io_evaluate.input.chapter_text_present": _check_present("chapter_text", "io_evaluate.input.chapter_text_present", "evaluate_input"),
    "io_evaluate.input.pass_number_present": _check_present("pass_number", "io_evaluate.input.pass_number_present", "evaluate_input"),
    "io_evaluate.input.max_passes_present": _check_present("max_passes", "io_evaluate.input.max_passes_present", "evaluate_input"),
    "io_evaluate.input.review_comments_array": _check_evaluate_input_review_comments_array,
    "io_evaluate.input.review_comments_may_be_empty": _check_evaluate_input_review_comments_may_be_empty,
    "io_evaluate.input.review_comment_id_and_text": _check_evaluate_input_review_comment_id_and_text,
    "io_evaluate.input.governing_excerpts_present": _check_present(
        "governing_excerpts", "io_evaluate.input.governing_excerpts_present", "evaluate_input"
    ),
    "io_evaluate.input.governing_excerpts_defect_categories": _check_evaluate_input_governing_excerpts_defect_categories,
    "io_evaluate.input.governing_excerpts_seven_question_checklist": _check_present(
        "governing_excerpts.seven_question_checklist",
        "io_evaluate.input.governing_excerpts_seven_question_checklist",
        "evaluate_input",
    ),
    "io_evaluate.input.governing_excerpts_style_rules": _check_present(
        "governing_excerpts.style_rules", "io_evaluate.input.governing_excerpts_style_rules", "evaluate_input"
    ),
    "io_evaluate.input.governing_excerpts_protected_passages": _check_evaluate_input_governing_excerpts_protected_passages,
    "io_evaluate.input.next_chapter_context_nullable": _check_evaluate_input_next_chapter_context_nullable,
    "io_evaluate.input.prior_rounds_summary_empty_on_pass_one": _check_evaluate_input_prior_rounds_summary_empty_on_pass_one,
    "io_evaluate.input.prior_rounds_summary_entry_shape": _check_evaluate_input_prior_rounds_summary_entry_shape,
    "io_evaluate.input.direct_instructions_array": _check_present(
        "direct_instructions", "io_evaluate.input.direct_instructions_array", "evaluate_input"
    ),
    "io_evaluate.input.direct_instructions_id_and_text": _check_evaluate_input_direct_instructions_id_and_text,
    "io_evaluate.output.items_array": _check_evaluate_output_items_array,
    "io_evaluate.output.item_id_present": _check_evaluate_output_item_string_field(
        "item_id", "io_evaluate.output.item_id_present"
    ),
    "io_evaluate.output.item_origin_supplied_review": _check_evaluate_output_item_origin_supplied_review,
    "io_evaluate.output.item_priority_present": _check_evaluate_output_item_string_field(
        "priority", "io_evaluate.output.item_priority_present"
    ),
    "io_evaluate.output.item_priority_enum": _check_evaluate_output_item_priority_enum,
    "io_evaluate.output.signal_to_noise_impact_present": _check_evaluate_output_item_string_field(
        "signal_to_noise_impact", "io_evaluate.output.signal_to_noise_impact_present"
    ),
    "io_evaluate.output.essence_risk_present": _check_evaluate_output_item_string_field(
        "essence_risk", "io_evaluate.output.essence_risk_present"
    ),
    "io_evaluate.output.verbosity_impact_present": _check_evaluate_output_item_string_field(
        "verbosity_impact", "io_evaluate.output.verbosity_impact_present"
    ),
    "io_evaluate.output.readability_impact_present": _check_evaluate_output_item_string_field(
        "readability_impact", "io_evaluate.output.readability_impact_present"
    ),
    "io_evaluate.output.repetition_impact_present": _check_evaluate_output_item_string_field(
        "repetition_impact", "io_evaluate.output.repetition_impact_present"
    ),
    "io_evaluate.output.recommendation_present": _check_evaluate_output_item_string_field(
        "recommendation", "io_evaluate.output.recommendation_present"
    ),
    "io_evaluate.output.recommendation_enum_values": _check_evaluate_output_recommendation_enum_values,
    "io_evaluate.output.reason_present": _check_evaluate_output_item_string_field(
        "reason", "io_evaluate.output.reason_present"
    ),
    "io_evaluate.output.minimal_corrected_text_field_present": lambda b: _check_evaluate_output_item_has_field(
        b, "minimal_corrected_text", "io_evaluate.output.minimal_corrected_text_field_present"
    ),
    "io_evaluate.output.minimal_corrected_text_nullability_matches_recommendation": _check_evaluate_output_minimal_corrected_text_nullability,
    "io_evaluate.output.hard_constraint_rejections_array": _check_evaluate_output_hard_constraint_rejections_array,
    "io_evaluate.output.rejection_item_id_present": lambda b: _check_evaluate_output_rejection_fields(b, "item_id"),
    "io_evaluate.output.rejection_constraint_hit_present": lambda b: _check_evaluate_output_rejection_fields(
        b, "constraint_hit"
    ),
    "io_evaluate.output.rejection_note_present": lambda b: _check_evaluate_output_rejection_fields(b, "note"),
    "io_evaluate.output.hard_constraint_rejection_skips_checklist": _check_evaluate_output_hard_constraint_rejection_skips_checklist,
    "io_evaluate.output.agent_identified_findings_array": _check_evaluate_output_agent_identified_findings_array,
    "io_evaluate.output.agent_identified_item_id_present": _check_agent_finding_field(
        "item_id", "io_evaluate.output.agent_identified_item_id_present"
    ),
    "io_evaluate.output.agent_identified_origin_value": _check_agent_finding_field(
        "origin", "io_evaluate.output.agent_identified_origin_value"
    ),
    "io_evaluate.output.agent_identified_defect_category_present": _check_agent_finding_field(
        "defect_category", "io_evaluate.output.agent_identified_defect_category_present"
    ),
    "io_evaluate.output.agent_identified_defect_category_matches_supplied": _check_evaluate_output_agent_identified_defect_category_matches_supplied,
    "io_evaluate.output.agent_identified_priority_present": _check_agent_finding_field(
        "priority", "io_evaluate.output.agent_identified_priority_present"
    ),
    "io_evaluate.output.agent_identified_recommendation_present": _check_agent_finding_field(
        "recommendation", "io_evaluate.output.agent_identified_recommendation_present"
    ),
    "io_evaluate.output.agent_identified_reason_present": _check_agent_finding_field(
        "reason", "io_evaluate.output.agent_identified_reason_present"
    ),
    "io_evaluate.output.agent_identified_finding_has_corrected_text_field": _check_evaluate_output_agent_identified_finding_has_corrected_text_field,
    "io_evaluate.output.agent_identified_finding_corrected_text_nullability_matches_recommendation": _check_evaluate_output_agent_identified_corrected_text_nullability,
    "io_evaluate.output.supplied_and_agent_identified_corrected_text_same_nullability": _check_evaluate_output_supplied_and_agent_identified_same_nullability,
    "io_evaluate.output.convergence_assessment_present": _check_evaluate_output_convergence_assessment_present,
    "io_evaluate.output.scope_trend_present": _check_evaluate_output_scope_trend_present,
    "io_evaluate.output.scope_trend_enum_values": _check_evaluate_output_scope_trend_enum,
    "io_evaluate.output.comparison_note_present": _check_evaluate_output_comparison_note_present,
    "io_apply.input.task_is_apply": _check_apply_input_task,
    "io_apply.input.chapter_id_present": _check_present("chapter_id", "io_apply.input.chapter_id_present", "apply_input"),
    "io_apply.input.chapter_text_present": _check_present("chapter_text", "io_apply.input.chapter_text_present", "apply_input"),
    "io_apply.input.pass_number_present": _check_present("pass_number", "io_apply.input.pass_number_present", "apply_input"),
    "io_apply.input.approved_items_array": _check_apply_input_approved_items_array,
    "io_apply.input.approved_item_id_present": _check_apply_input_approved_item_field(
        "item_id", "io_apply.input.approved_item_id_present"
    ),
    "io_apply.input.approved_item_recommendation_present": _check_apply_input_approved_item_field(
        "recommendation", "io_apply.input.approved_item_recommendation_present"
    ),
    "io_apply.input.approved_item_minimal_corrected_text_present": _check_apply_input_approved_item_field(
        "minimal_corrected_text", "io_apply.input.approved_item_minimal_corrected_text_present"
    ),
    "io_apply.input.direct_instructions_array": _check_present(
        "direct_instructions", "io_apply.input.direct_instructions_array", "apply_input"
    ),
    "io_apply.input.direct_instruction_action_field": _check_apply_input_direct_instruction_action_field,
    "io_apply.input.next_chapter_context": _check_present(
        "next_chapter_context", "io_apply.input.next_chapter_context", "apply_input"
    ),
    "io_apply.input.invalid_recommendation_reported_in_input_errors": _check_apply_input_invalid_recommendation_reported,
    "io_apply.output.revised_chapter_text_present": _check_present(
        "revised_chapter_text", "io_apply.output.revised_chapter_text_present", "apply_output"
    ),
    "io_apply.output.change_log_array": _check_apply_output_array("change_log", "io_apply.output.change_log_array"),
    "io_apply.output.change_log_item_id_present": _check_apply_output_change_log_field(
        "item_id", "io_apply.output.change_log_item_id_present"
    ),
    "io_apply.output.change_log_section_present": _check_apply_output_change_log_field(
        "section", "io_apply.output.change_log_section_present"
    ),
    "io_apply.output.change_log_before_excerpt_present": _check_apply_output_change_log_field(
        "before_excerpt", "io_apply.output.change_log_before_excerpt_present"
    ),
    "io_apply.output.change_log_after_excerpt_present": _check_apply_output_change_log_field(
        "after_excerpt", "io_apply.output.change_log_after_excerpt_present"
    ),
    "io_apply.output.deviations_from_review_wording_array": _check_apply_output_array(
        "deviations_from_review_wording", "io_apply.output.deviations_from_review_wording_array"
    ),
    "io_apply.output.deviation_item_id_present": lambda b: _check_apply_output_deviation_fields(b, "item_id"),
    "io_apply.output.deviation_reason_present": lambda b: _check_apply_output_deviation_fields(b, "reason"),
    "io_apply.output.input_errors_array": _check_apply_output_array("input_errors", "io_apply.output.input_errors_array"),
    "io_apply.output.input_error_item_id_present": _check_apply_output_input_error_field(
        "item_id", "io_apply.output.input_error_item_id_present"
    ),
    "io_apply.output.input_error_problem_present": _check_apply_output_input_error_field(
        "problem", "io_apply.output.input_error_problem_present"
    ),
    "io_apply.output.hard_constraint_self_check.no_cross_reference_invalidated": _check_self_check_boolean(
        "no_cross_reference_invalidated",
        "io_apply.output.hard_constraint_self_check.no_cross_reference_invalidated",
    ),
    "io_apply.output.hard_constraint_self_check.no_section_reordered_added_removed": _check_self_check_boolean(
        "no_section_reordered_added_removed",
        "io_apply.output.hard_constraint_self_check.no_section_reordered_added_removed",
    ),
    "io_apply.output.hard_constraint_self_check.no_protected_passage_diluted": _check_self_check_boolean(
        "no_protected_passage_diluted",
        "io_apply.output.hard_constraint_self_check.no_protected_passage_diluted",
    ),
    "io_apply.output.hard_constraint_self_check.no_code_block_changed": _check_self_check_boolean(
        "no_code_block_changed",
        "io_apply.output.hard_constraint_self_check.no_code_block_changed",
    ),
    "io_apply.output.hard_constraint_self_check_notes_populated_on_failure": _check_self_check_notes_populated_on_failure,
    "meta.amendment_1_supersedes_base_contract_for_agent_identified_findings": _check_meta_amendment_supersedes,
}


def check_requirement(requirement_id: str, bundle: PayloadBundle) -> None:
    try:
        checker = REGISTRY[requirement_id]
    except KeyError as exc:
        raise KeyError(f"no checker registered for {requirement_id}") from exc
    checker(bundle)
