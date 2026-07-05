"""Per-requirement compliant/violating PayloadBundle definitions."""

from __future__ import annotations

from copy import deepcopy

from structural_suite.checkers import PayloadBundle
from tests.structural.conftest import Case
from tests.structural.fixtures.evaluate_apply import (
    APPLY_INPUT,
    APPLY_OUTPUT,
    EVALUATE_INPUT,
    EVALUATE_OUTPUT,
    clone,
)
from tests.structural.fixtures.violations import (
    APPLY_INPUT_DO_NOT_APPLY,
    APPLY_INPUT_WRONG_TASK,
    APPLY_OUTPUT_BAD_TOP_LEVEL_KEYS,
    APPLY_OUTPUT_CHAPTER_NUMBER_BRIDGE,
    APPLY_OUTPUT_EXTRA_TOP_LEVEL,
    APPLY_OUTPUT_MISSING_CHANGE_LOG_FOR_APPROVED,
    APPLY_OUTPUT_MISSING_SELF_CHECK,
    APPLY_OUTPUT_NEXT_CHAPTER_PHRASING,
    APPLY_OUTPUT_NO_INPUT_ERROR_FOR_DNA,
    APPLY_OUTPUT_RESTRUCTURE_ERROR,
    APPLY_OUTPUT_SELF_CHECK_FALSE_NO_NOTES,
    APPLY_OUTPUT_SELF_CHECK_NOT_BOOL,
    APPLY_OUTPUT_SELF_CHECK_NOTES_WHEN_ALL_TRUE,
    EVALUATE_INPUT_MISSING_CHAPTER_ID,
    EVALUATE_INPUT_PASS_ONE_WITH_PRIOR,
    EVALUATE_INPUT_WRONG_TASK,
    EVALUATE_OUTPUT_AGENT_TEXT_WHEN_DNA,
    EVALUATE_OUTPUT_BAD_DEFECT_CATEGORY,
    EVALUATE_OUTPUT_BAD_PRIORITY,
    EVALUATE_OUTPUT_BAD_SCOPE_TREND,
    EVALUATE_OUTPUT_BAD_TOP_LEVEL_KEYS,
    EVALUATE_OUTPUT_CODE_LISTING_REJECTION,
    EVALUATE_OUTPUT_EXTRA_TOP_LEVEL,
    EVALUATE_OUTPUT_MISSING_AGENT_TEXT_FIELD,
    EVALUATE_OUTPUT_NO_REJECTIONS,
    EVALUATE_OUTPUT_REJECTED_IN_ITEMS,
    EVALUATE_OUTPUT_WRONG_CODE_CONSTRAINT,
)


def _bundle(
    evaluate_input=EVALUATE_INPUT,
    evaluate_output=EVALUATE_OUTPUT,
    apply_input=APPLY_INPUT,
    apply_output=APPLY_OUTPUT,
) -> PayloadBundle:
    return PayloadBundle(
        evaluate_input=clone(evaluate_input) if evaluate_input is not None else None,
        evaluate_output=clone(evaluate_output) if evaluate_output is not None else None,
        apply_input=clone(apply_input) if apply_input is not None else None,
        apply_output=clone(apply_output) if apply_output is not None else None,
    )


def _drop(payload: dict, key: str) -> dict:
    copy = clone(payload)
    copy.pop(key, None)
    return copy


def _set(payload: dict, **fields) -> dict:
    copy = clone(payload)
    copy.update(fields)
    return copy


def _nested_set(payload: dict, path: list[str], value) -> dict:
    copy = deepcopy(payload)
    cur = copy
    for part in path[:-1]:
        cur = cur[part]
    cur[path[-1]] = value
    return copy


APPLY_OUTPUT_WITH_INPUT_ERRORS = clone(APPLY_OUTPUT)
APPLY_OUTPUT_WITH_INPUT_ERRORS["input_errors"] = [
    {
        "item_id": "c9",
        "problem": "received item with recommendation DO_NOT_APPLY",
    }
]

EVALUATE_INPUT_PASS_ONE = clone(EVALUATE_INPUT)
EVALUATE_INPUT_PASS_ONE["pass_number"] = 1
EVALUATE_INPUT_PASS_ONE["prior_rounds_summary"] = []

EVALUATE_OUTPUT_MISSING_ITEM_FIELD = clone(EVALUATE_OUTPUT)
del EVALUATE_OUTPUT_MISSING_ITEM_FIELD["items"][0]["essence_risk"]

EVALUATE_OUTPUT_MISSING_MINIMAL_FIELD = clone(EVALUATE_OUTPUT)
del EVALUATE_OUTPUT_MISSING_MINIMAL_FIELD["items"][0]["minimal_corrected_text"]

EVALUATE_OUTPUT_APPLY_WITHOUT_TEXT = clone(EVALUATE_OUTPUT)
EVALUATE_OUTPUT_APPLY_WITHOUT_TEXT["items"][0]["minimal_corrected_text"] = None

EVALUATE_OUTPUT_BAD_RECOMMENDATION = clone(EVALUATE_OUTPUT)
EVALUATE_OUTPUT_BAD_RECOMMENDATION["items"][0]["recommendation"] = "MAYBE"

EVALUATE_OUTPUT_MISSING_REJECTION_NOTE = clone(EVALUATE_OUTPUT)
EVALUATE_OUTPUT_MISSING_REJECTION_NOTE["hard_constraint_rejections"][0]["note"] = ""

EVALUATE_OUTPUT_NOT_ITEMS_ARRAY = clone(EVALUATE_OUTPUT)
EVALUATE_OUTPUT_NOT_ITEMS_ARRAY["items"] = "not-a-list"

EVALUATE_INPUT_BAD_PRIOR_SHAPE = clone(EVALUATE_INPUT)
EVALUATE_INPUT_BAD_PRIOR_SHAPE["prior_rounds_summary"] = [{"pass_number": 1}]

EVALUATE_INPUT_MISSING_NEXT_KEY = clone(EVALUATE_INPUT)
del EVALUATE_INPUT_MISSING_NEXT_KEY["next_chapter_context"]

EVALUATE_INPUT_EMPTY_COMMENTS = clone(EVALUATE_INPUT)
EVALUATE_INPUT_EMPTY_COMMENTS["review_comments"] = []

APPLY_OUTPUT_EMPTY_DEVIATIONS = clone(APPLY_OUTPUT)
APPLY_OUTPUT_EMPTY_DEVIATIONS["deviations_from_review_wording"] = []

CASE_BUILDERS: dict[str, tuple[PayloadBundle, PayloadBundle]] = {
    "playbook.role.exact_matching_io_contract_schema": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_EXTRA_TOP_LEVEL),
    ),
    "playbook.role.single_task_per_invocation": (
        _bundle(),
        _bundle(evaluate_input=EVALUATE_INPUT_WRONG_TASK, apply_input=APPLY_INPUT_WRONG_TASK),
    ),
    "playbook.hard_constraint.apply_self_check_before_return": (
        _bundle(),
        _bundle(apply_output=APPLY_OUTPUT_MISSING_SELF_CHECK),
    ),
    "playbook.hard_constraint.evaluate_rejection_out_of_scope": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_NO_REJECTIONS),
    ),
    "playbook.hard_constraint.evaluate_skips_checklist": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_REJECTED_IN_ITEMS),
    ),
    "playbook.hard_constraint.no_code_listing_changes": (
        _bundle(evaluate_output=EVALUATE_OUTPUT_CODE_LISTING_REJECTION),
        _bundle(evaluate_output=EVALUATE_OUTPUT_WRONG_CODE_CONSTRAINT),
    ),
    "playbook.evaluate.agent_identified_origin_tag": (
        _bundle(),
        _bundle(
            evaluate_output=_nested_set(
                EVALUATE_OUTPUT, ["agent_identified_findings", 0, "origin"], "supplied_review"
            )
        ),
    ),
    "playbook.evaluate.convergence_computed_from_prior_rounds": (
        _bundle(),
        _bundle(
            evaluate_output=_nested_set(
                EVALUATE_OUTPUT, ["convergence_assessment", "comparison_note"], "Looks fine."
            )
        ),
    ),
    "playbook.evaluate.essence_risk_present": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_MISSING_ITEM_FIELD),
    ),
    "playbook.evaluate.hard_constraints_checked_first": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_REJECTED_IN_ITEMS),
    ),
    "playbook.evaluate.priority_enum_values": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_BAD_PRIORITY),
    ),
    "playbook.evaluate.priority_field_present": (
        _bundle(),
        _bundle(
            evaluate_output=_nested_set(
                EVALUATE_OUTPUT,
                ["items", 0],
                _drop(EVALUATE_OUTPUT["items"][0], "priority"),
            )
        ),
    ),
    "playbook.evaluate.readability_impact_present": (
        _bundle(),
        _bundle(
            evaluate_output=_nested_set(
                EVALUATE_OUTPUT, ["items", 0, "readability_impact"], ""
            )
        ),
    ),
    "playbook.evaluate.reason_field_present": (
        _bundle(),
        _bundle(evaluate_output=_nested_set(EVALUATE_OUTPUT, ["items", 0, "reason"], "")),
    ),
    "playbook.evaluate.recommendation_enum_values": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_BAD_RECOMMENDATION),
    ),
    "playbook.evaluate.recommendation_field_present": (
        _bundle(),
        _bundle(evaluate_output=_nested_set(EVALUATE_OUTPUT, ["items", 0, "recommendation"], "")),
    ),
    "playbook.evaluate.repetition_impact_present": (
        _bundle(),
        _bundle(evaluate_output=_nested_set(EVALUATE_OUTPUT, ["items", 0, "repetition_impact"], "")),
    ),
    "playbook.evaluate.return_evaluate_contract_only": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_EXTRA_TOP_LEVEL),
    ),
    "playbook.evaluate.seven_dimensions_always_written": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_MISSING_ITEM_FIELD),
    ),
    "playbook.evaluate.signal_to_noise_impact_present": (
        _bundle(),
        _bundle(
            evaluate_output=_nested_set(
                EVALUATE_OUTPUT, ["items", 0, "signal_to_noise_impact"], ""
            )
        ),
    ),
    "playbook.evaluate.verbosity_impact_present": (
        _bundle(),
        _bundle(evaluate_output=_nested_set(EVALUATE_OUTPUT, ["items", 0, "verbosity_impact"], "")),
    ),
    "playbook.apply.change_log_per_approved_item": (
        _bundle(),
        _bundle(apply_output=APPLY_OUTPUT_MISSING_CHANGE_LOG_FOR_APPROVED),
    ),
    "playbook.apply.closing_bridge_no_chapter_number": (
        _bundle(),
        _bundle(apply_output=APPLY_OUTPUT_CHAPTER_NUMBER_BRIDGE),
    ),
    "playbook.apply.closing_bridge_no_next_chapter_phrasing": (
        _bundle(),
        _bundle(apply_output=APPLY_OUTPUT_NEXT_CHAPTER_PHRASING),
    ),
    "playbook.apply.hard_constraint_boolean_self_check_block": (
        _bundle(),
        _bundle(apply_output=APPLY_OUTPUT_SELF_CHECK_NOT_BOOL),
    ),
    "playbook.apply.rejects_do_not_apply_as_input_error": (
        _bundle(apply_input=APPLY_INPUT_DO_NOT_APPLY, apply_output=APPLY_OUTPUT_WITH_INPUT_ERRORS),
        _bundle(apply_input=APPLY_INPUT_DO_NOT_APPLY, apply_output=APPLY_OUTPUT_NO_INPUT_ERROR_FOR_DNA),
    ),
    "playbook.apply.restructure_flags_input_error": (
        _bundle(apply_output=APPLY_OUTPUT_RESTRUCTURE_ERROR),
        _bundle(apply_output=APPLY_OUTPUT_NO_INPUT_ERROR_FOR_DNA),
    ),
    "playbook.apply.return_apply_contract_only": (
        _bundle(),
        _bundle(apply_output=APPLY_OUTPUT_EXTRA_TOP_LEVEL),
    ),
    "io_evaluate.input.task_is_evaluate": (
        _bundle(),
        _bundle(evaluate_input=EVALUATE_INPUT_WRONG_TASK),
    ),
    "io_evaluate.input.chapter_id_present": (
        _bundle(),
        _bundle(evaluate_input=EVALUATE_INPUT_MISSING_CHAPTER_ID),
    ),
    "io_evaluate.input.chapter_text_present": (
        _bundle(),
        _bundle(evaluate_input=_set(EVALUATE_INPUT, chapter_text="")),
    ),
    "io_evaluate.input.pass_number_present": (
        _bundle(),
        _bundle(evaluate_input=_drop(EVALUATE_INPUT, "pass_number")),
    ),
    "io_evaluate.input.max_passes_present": (
        _bundle(),
        _bundle(evaluate_input=_drop(EVALUATE_INPUT, "max_passes")),
    ),
    "io_evaluate.input.review_comments_array": (
        _bundle(),
        _bundle(evaluate_input=_set(EVALUATE_INPUT, review_comments="not-a-list")),
    ),
    "io_evaluate.input.review_comments_may_be_empty": (
        _bundle(evaluate_input=EVALUATE_INPUT_EMPTY_COMMENTS),
        _bundle(evaluate_input=_drop(EVALUATE_INPUT, "review_comments")),
    ),
    "io_evaluate.input.review_comment_id_and_text": (
        _bundle(),
        _bundle(
            evaluate_input=_set(
                EVALUATE_INPUT,
                review_comments=[{"comment_id": "", "text": "missing id"}],
            )
        ),
    ),
    "io_evaluate.input.governing_excerpts_present": (
        _bundle(),
        _bundle(evaluate_input=_drop(EVALUATE_INPUT, "governing_excerpts")),
    ),
    "io_evaluate.input.governing_excerpts_defect_categories": (
        _bundle(),
        _bundle(
            evaluate_input=_nested_set(
                EVALUATE_INPUT, ["governing_excerpts", "defect_categories"], ["only_one"]
            )
        ),
    ),
    "io_evaluate.input.governing_excerpts_seven_question_checklist": (
        _bundle(),
        _bundle(
            evaluate_input=_nested_set(
                EVALUATE_INPUT,
                ["governing_excerpts"],
                _drop(EVALUATE_INPUT["governing_excerpts"], "seven_question_checklist"),
            )
        ),
    ),
    "io_evaluate.input.governing_excerpts_style_rules": (
        _bundle(),
        _bundle(
            evaluate_input=_nested_set(
                EVALUATE_INPUT,
                ["governing_excerpts"],
                _drop(EVALUATE_INPUT["governing_excerpts"], "style_rules"),
            )
        ),
    ),
    "io_evaluate.input.governing_excerpts_protected_passages": (
        _bundle(),
        _bundle(
            evaluate_input=_nested_set(
                EVALUATE_INPUT, ["governing_excerpts", "protected_passages"], []
            )
        ),
    ),
    "io_evaluate.input.next_chapter_context_nullable": (
        _bundle(),
        _bundle(evaluate_input=EVALUATE_INPUT_MISSING_NEXT_KEY),
    ),
    "io_evaluate.input.prior_rounds_summary_empty_on_pass_one": (
        _bundle(evaluate_input=EVALUATE_INPUT_PASS_ONE),
        _bundle(evaluate_input=EVALUATE_INPUT_PASS_ONE_WITH_PRIOR),
    ),
    "io_evaluate.input.prior_rounds_summary_entry_shape": (
        _bundle(),
        _bundle(evaluate_input=EVALUATE_INPUT_BAD_PRIOR_SHAPE),
    ),
    "io_evaluate.input.direct_instructions_array": (
        _bundle(),
        _bundle(evaluate_input=_drop(EVALUATE_INPUT, "direct_instructions")),
    ),
    "io_evaluate.input.direct_instructions_id_and_text": (
        _bundle(),
        _bundle(
            evaluate_input=_set(
                EVALUATE_INPUT, direct_instructions=[{"instruction_id": "d1", "text": ""}]
            )
        ),
    ),
    "io_evaluate.output.items_array": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_NOT_ITEMS_ARRAY),
    ),
    "io_evaluate.output.item_id_present": (
        _bundle(),
        _bundle(evaluate_output=_nested_set(EVALUATE_OUTPUT, ["items", 0, "item_id"], "")),
    ),
    "io_evaluate.output.item_origin_supplied_review": (
        _bundle(),
        _bundle(evaluate_output=_nested_set(EVALUATE_OUTPUT, ["items", 0, "origin"], "agent_identified")),
    ),
    "io_evaluate.output.item_priority_present": (
        _bundle(),
        _bundle(evaluate_output=_nested_set(EVALUATE_OUTPUT, ["items", 0, "priority"], "")),
    ),
    "io_evaluate.output.item_priority_enum": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_BAD_PRIORITY),
    ),
    "io_evaluate.output.signal_to_noise_impact_present": (
        _bundle(),
        _bundle(
            evaluate_output=_nested_set(
                EVALUATE_OUTPUT, ["items", 0, "signal_to_noise_impact"], ""
            )
        ),
    ),
    "io_evaluate.output.essence_risk_present": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_MISSING_ITEM_FIELD),
    ),
    "io_evaluate.output.verbosity_impact_present": (
        _bundle(),
        _bundle(evaluate_output=_nested_set(EVALUATE_OUTPUT, ["items", 0, "verbosity_impact"], "")),
    ),
    "io_evaluate.output.readability_impact_present": (
        _bundle(),
        _bundle(evaluate_output=_nested_set(EVALUATE_OUTPUT, ["items", 0, "readability_impact"], "")),
    ),
    "io_evaluate.output.repetition_impact_present": (
        _bundle(),
        _bundle(evaluate_output=_nested_set(EVALUATE_OUTPUT, ["items", 0, "repetition_impact"], "")),
    ),
    "io_evaluate.output.recommendation_present": (
        _bundle(),
        _bundle(evaluate_output=_nested_set(EVALUATE_OUTPUT, ["items", 0, "recommendation"], "")),
    ),
    "io_evaluate.output.recommendation_enum_values": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_BAD_RECOMMENDATION),
    ),
    "io_evaluate.output.reason_present": (
        _bundle(),
        _bundle(evaluate_output=_nested_set(EVALUATE_OUTPUT, ["items", 0, "reason"], "")),
    ),
    "io_evaluate.output.minimal_corrected_text_field_present": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_MISSING_MINIMAL_FIELD),
    ),
    "io_evaluate.output.minimal_corrected_text_nullability_matches_recommendation": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_APPLY_WITHOUT_TEXT),
    ),
    "io_evaluate.output.hard_constraint_rejections_array": (
        _bundle(),
        _bundle(evaluate_output=_set(EVALUATE_OUTPUT, hard_constraint_rejections="nope")),
    ),
    "io_evaluate.output.rejection_item_id_present": (
        _bundle(),
        _bundle(
            evaluate_output=_nested_set(
                EVALUATE_OUTPUT, ["hard_constraint_rejections", 0, "item_id"], ""
            )
        ),
    ),
    "io_evaluate.output.rejection_constraint_hit_present": (
        _bundle(),
        _bundle(
            evaluate_output=_nested_set(
                EVALUATE_OUTPUT, ["hard_constraint_rejections", 0, "constraint_hit"], ""
            )
        ),
    ),
    "io_evaluate.output.rejection_note_present": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_MISSING_REJECTION_NOTE),
    ),
    "io_evaluate.output.hard_constraint_rejection_skips_checklist": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_REJECTED_IN_ITEMS),
    ),
    "io_evaluate.output.agent_identified_findings_array": (
        _bundle(),
        _bundle(evaluate_output=_set(EVALUATE_OUTPUT, agent_identified_findings="nope")),
    ),
    "io_evaluate.output.agent_identified_item_id_present": (
        _bundle(),
        _bundle(
            evaluate_output=_nested_set(
                EVALUATE_OUTPUT, ["agent_identified_findings", 0, "item_id"], ""
            )
        ),
    ),
    "io_evaluate.output.agent_identified_origin_value": (
        _bundle(),
        _bundle(
            evaluate_output=_nested_set(
                EVALUATE_OUTPUT, ["agent_identified_findings", 0, "origin"], "supplied_review"
            )
        ),
    ),
    "io_evaluate.output.agent_identified_defect_category_present": (
        _bundle(),
        _bundle(
            evaluate_output=_nested_set(
                EVALUATE_OUTPUT, ["agent_identified_findings", 0, "defect_category"], ""
            )
        ),
    ),
    "io_evaluate.output.agent_identified_defect_category_matches_supplied": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_BAD_DEFECT_CATEGORY),
    ),
    "io_evaluate.output.agent_identified_priority_present": (
        _bundle(),
        _bundle(
            evaluate_output=_nested_set(
                EVALUATE_OUTPUT, ["agent_identified_findings", 0, "priority"], "URGENT"
            )
        ),
    ),
    "io_evaluate.output.agent_identified_recommendation_present": (
        _bundle(),
        _bundle(
            evaluate_output=_nested_set(
                EVALUATE_OUTPUT, ["agent_identified_findings", 0, "recommendation"], ""
            )
        ),
    ),
    "io_evaluate.output.agent_identified_reason_present": (
        _bundle(),
        _bundle(
            evaluate_output=_nested_set(
                EVALUATE_OUTPUT, ["agent_identified_findings", 0, "reason"], ""
            )
        ),
    ),
    "io_evaluate.output.agent_identified_finding_has_corrected_text_field": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_MISSING_AGENT_TEXT_FIELD),
    ),
    "io_evaluate.output.agent_identified_finding_corrected_text_nullability_matches_recommendation": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_AGENT_TEXT_WHEN_DNA),
    ),
    "io_evaluate.output.supplied_and_agent_identified_corrected_text_same_nullability": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_AGENT_TEXT_WHEN_DNA),
    ),
    "io_evaluate.output.convergence_assessment_present": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_BAD_TOP_LEVEL_KEYS),
    ),
    "io_evaluate.output.scope_trend_present": (
        _bundle(),
        _bundle(
            evaluate_output=_nested_set(
                EVALUATE_OUTPUT, ["convergence_assessment", "scope_trend"], ""
            )
        ),
    ),
    "io_evaluate.output.scope_trend_enum_values": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_BAD_SCOPE_TREND),
    ),
    "io_evaluate.output.comparison_note_present": (
        _bundle(),
        _bundle(
            evaluate_output=_nested_set(
                EVALUATE_OUTPUT, ["convergence_assessment", "comparison_note"], ""
            )
        ),
    ),
    "io_apply.input.task_is_apply": (
        _bundle(),
        _bundle(apply_input=APPLY_INPUT_WRONG_TASK),
    ),
    "io_apply.input.chapter_id_present": (
        _bundle(),
        _bundle(apply_input=_drop(APPLY_INPUT, "chapter_id")),
    ),
    "io_apply.input.chapter_text_present": (
        _bundle(),
        _bundle(apply_input=_set(APPLY_INPUT, chapter_text="")),
    ),
    "io_apply.input.pass_number_present": (
        _bundle(),
        _bundle(apply_input=_drop(APPLY_INPUT, "pass_number")),
    ),
    "io_apply.input.approved_items_array": (
        _bundle(),
        _bundle(apply_input=_set(APPLY_INPUT, approved_items="nope")),
    ),
    "io_apply.input.approved_item_id_present": (
        _bundle(),
        _bundle(
            apply_input=_set(
                APPLY_INPUT,
                approved_items=[{"item_id": "", "recommendation": "APPLY", "minimal_corrected_text": "x"}],
            )
        ),
    ),
    "io_apply.input.approved_item_recommendation_present": (
        _bundle(),
        _bundle(
            apply_input=_set(
                APPLY_INPUT,
                approved_items=[
                    {"item_id": "c1", "recommendation": "DO_NOT_APPLY", "minimal_corrected_text": "x"}
                ],
            )
        ),
    ),
    "io_apply.input.approved_item_minimal_corrected_text_present": (
        _bundle(),
        _bundle(
            apply_input=_set(
                APPLY_INPUT,
                approved_items=[{"item_id": "c1", "recommendation": "APPLY", "minimal_corrected_text": ""}],
            )
        ),
    ),
    "io_apply.input.direct_instructions_array": (
        _bundle(),
        _bundle(apply_input=_drop(APPLY_INPUT, "direct_instructions")),
    ),
    "io_apply.input.direct_instruction_action_field": (
        _bundle(),
        _bundle(
            apply_input=_set(
                APPLY_INPUT,
                direct_instructions=[{"instruction_id": "d1", "text": "t", "action": ""}],
            )
        ),
    ),
    "io_apply.input.next_chapter_context": (
        _bundle(),
        _bundle(apply_input=_drop(APPLY_INPUT, "next_chapter_context")),
    ),
    "io_apply.input.invalid_recommendation_reported_in_input_errors": (
        _bundle(apply_input=APPLY_INPUT_DO_NOT_APPLY, apply_output=APPLY_OUTPUT_WITH_INPUT_ERRORS),
        _bundle(apply_input=APPLY_INPUT_DO_NOT_APPLY, apply_output=APPLY_OUTPUT_NO_INPUT_ERROR_FOR_DNA),
    ),
    "io_apply.output.revised_chapter_text_present": (
        _bundle(),
        _bundle(apply_output=_set(APPLY_OUTPUT, revised_chapter_text="")),
    ),
    "io_apply.output.change_log_array": (
        _bundle(),
        _bundle(apply_output=_set(APPLY_OUTPUT, change_log="nope")),
    ),
    "io_apply.output.change_log_item_id_present": (
        _bundle(),
        _bundle(apply_output=_nested_set(APPLY_OUTPUT, ["change_log", 0, "item_id"], "")),
    ),
    "io_apply.output.change_log_section_present": (
        _bundle(),
        _bundle(apply_output=_nested_set(APPLY_OUTPUT, ["change_log", 0, "section"], "")),
    ),
    "io_apply.output.change_log_before_excerpt_present": (
        _bundle(),
        _bundle(apply_output=_nested_set(APPLY_OUTPUT, ["change_log", 0, "before_excerpt"], "")),
    ),
    "io_apply.output.change_log_after_excerpt_present": (
        _bundle(),
        _bundle(apply_output=_nested_set(APPLY_OUTPUT, ["change_log", 0, "after_excerpt"], "")),
    ),
    "io_apply.output.deviations_from_review_wording_array": (
        _bundle(),
        _bundle(apply_output=_set(APPLY_OUTPUT, deviations_from_review_wording="nope")),
    ),
    "io_apply.output.deviation_item_id_present": (
        _bundle(),
        _bundle(
            apply_output=_nested_set(
                APPLY_OUTPUT, ["deviations_from_review_wording", 0, "item_id"], ""
            )
        ),
    ),
    "io_apply.output.deviation_reason_present": (
        _bundle(),
        _bundle(
            apply_output=_nested_set(
                APPLY_OUTPUT, ["deviations_from_review_wording", 0, "reason"], ""
            )
        ),
    ),
    "io_apply.output.input_errors_array": (
        _bundle(apply_output=APPLY_OUTPUT_WITH_INPUT_ERRORS),
        _bundle(apply_output=_set(APPLY_OUTPUT, input_errors="nope")),
    ),
    "io_apply.output.input_error_item_id_present": (
        _bundle(apply_output=APPLY_OUTPUT_WITH_INPUT_ERRORS),
        _bundle(
            apply_output=_nested_set(APPLY_OUTPUT_WITH_INPUT_ERRORS, ["input_errors", 0, "item_id"], "")
        ),
    ),
    "io_apply.output.input_error_problem_present": (
        _bundle(apply_output=APPLY_OUTPUT_WITH_INPUT_ERRORS),
        _bundle(
            apply_output=_nested_set(APPLY_OUTPUT_WITH_INPUT_ERRORS, ["input_errors", 0, "problem"], "")
        ),
    ),
    "io_apply.output.hard_constraint_self_check.no_cross_reference_invalidated": (
        _bundle(),
        _bundle(
            apply_output=_nested_set(
                APPLY_OUTPUT,
                ["hard_constraint_self_check", "no_cross_reference_invalidated"],
                "yes",
            )
        ),
    ),
    "io_apply.output.hard_constraint_self_check.no_section_reordered_added_removed": (
        _bundle(),
        _bundle(
            apply_output=_nested_set(
                APPLY_OUTPUT,
                ["hard_constraint_self_check", "no_section_reordered_added_removed"],
                "yes",
            )
        ),
    ),
    "io_apply.output.hard_constraint_self_check.no_protected_passage_diluted": (
        _bundle(),
        _bundle(
            apply_output=_nested_set(
                APPLY_OUTPUT, ["hard_constraint_self_check", "no_protected_passage_diluted"], "yes"
            )
        ),
    ),
    "io_apply.output.hard_constraint_self_check.no_code_block_changed": (
        _bundle(),
        _bundle(apply_output=APPLY_OUTPUT_SELF_CHECK_NOT_BOOL),
    ),
    "io_apply.output.hard_constraint_self_check_notes_populated_on_failure": (
        _bundle(),
        _bundle(apply_output=APPLY_OUTPUT_SELF_CHECK_FALSE_NO_NOTES),
    ),
    "meta.amendment_1_supersedes_base_contract_for_agent_identified_findings": (
        _bundle(),
        _bundle(evaluate_output=EVALUATE_OUTPUT_MISSING_AGENT_TEXT_FIELD),
    ),
}

# Extra absent-key violating bundles for representative *_present checks (see README).
DELETED_KEY_VIOLATIONS: dict[str, PayloadBundle] = {
    "io_evaluate.output.item_id_present": _bundle(
        evaluate_output=_nested_set(
            EVALUATE_OUTPUT,
            ["items", 0],
            _drop(EVALUATE_OUTPUT["items"][0], "item_id"),
        )
    ),
    "io_evaluate.input.chapter_id_present": _bundle(
        evaluate_input=_drop(EVALUATE_INPUT, "chapter_id"),
    ),
    "playbook.evaluate.reason_field_present": _bundle(
        evaluate_output=_nested_set(
            EVALUATE_OUTPUT,
            ["items", 0],
            _drop(EVALUATE_OUTPUT["items"][0], "reason"),
        )
    ),
}


def make_case(requirement_id: str) -> Case:
    compliant, violating = CASE_BUILDERS[requirement_id]
    return Case(
        requirement_id=requirement_id,
        compliant=compliant,
        violating=violating,
        violating_absent_key=DELETED_KEY_VIOLATIONS.get(requirement_id),
    )


FILE_GROUPS: dict[str, list[str]] = {
    "test_playbook_role.py": [
        "playbook.role.exact_matching_io_contract_schema",
        "playbook.role.single_task_per_invocation",
    ],
    "test_hard_constraints.py": [
        "playbook.hard_constraint.apply_self_check_before_return",
        "playbook.hard_constraint.evaluate_rejection_out_of_scope",
        "playbook.hard_constraint.evaluate_skips_checklist",
        "playbook.hard_constraint.no_code_listing_changes",
    ],
    "test_playbook_evaluate_output.py": [
        "playbook.evaluate.agent_identified_origin_tag",
        "playbook.evaluate.convergence_computed_from_prior_rounds",
        "playbook.evaluate.essence_risk_present",
        "playbook.evaluate.hard_constraints_checked_first",
        "playbook.evaluate.priority_enum_values",
        "playbook.evaluate.priority_field_present",
        "playbook.evaluate.readability_impact_present",
        "playbook.evaluate.reason_field_present",
        "playbook.evaluate.recommendation_enum_values",
        "playbook.evaluate.recommendation_field_present",
        "playbook.evaluate.repetition_impact_present",
        "playbook.evaluate.return_evaluate_contract_only",
        "playbook.evaluate.seven_dimensions_always_written",
        "playbook.evaluate.signal_to_noise_impact_present",
        "playbook.evaluate.verbosity_impact_present",
    ],
    "test_playbook_apply.py": [
        "playbook.apply.change_log_per_approved_item",
        "playbook.apply.closing_bridge_no_chapter_number",
        "playbook.apply.closing_bridge_no_next_chapter_phrasing",
        "playbook.apply.hard_constraint_boolean_self_check_block",
        "playbook.apply.rejects_do_not_apply_as_input_error",
        "playbook.apply.restructure_flags_input_error",
        "playbook.apply.return_apply_contract_only",
    ],
    "test_evaluate_input_schema.py": [
        "io_evaluate.input.task_is_evaluate",
        "io_evaluate.input.chapter_id_present",
        "io_evaluate.input.chapter_text_present",
        "io_evaluate.input.pass_number_present",
        "io_evaluate.input.max_passes_present",
        "io_evaluate.input.review_comments_array",
        "io_evaluate.input.review_comments_may_be_empty",
        "io_evaluate.input.review_comment_id_and_text",
        "io_evaluate.input.governing_excerpts_present",
        "io_evaluate.input.governing_excerpts_defect_categories",
        "io_evaluate.input.governing_excerpts_seven_question_checklist",
        "io_evaluate.input.governing_excerpts_style_rules",
        "io_evaluate.input.governing_excerpts_protected_passages",
        "io_evaluate.input.next_chapter_context_nullable",
        "io_evaluate.input.prior_rounds_summary_empty_on_pass_one",
        "io_evaluate.input.prior_rounds_summary_entry_shape",
        "io_evaluate.input.direct_instructions_array",
        "io_evaluate.input.direct_instructions_id_and_text",
    ],
    "test_evaluate_output_schema.py": [
        "io_evaluate.output.items_array",
        "io_evaluate.output.item_id_present",
        "io_evaluate.output.item_origin_supplied_review",
        "io_evaluate.output.item_priority_present",
        "io_evaluate.output.item_priority_enum",
        "io_evaluate.output.signal_to_noise_impact_present",
        "io_evaluate.output.essence_risk_present",
        "io_evaluate.output.verbosity_impact_present",
        "io_evaluate.output.readability_impact_present",
        "io_evaluate.output.repetition_impact_present",
        "io_evaluate.output.recommendation_present",
        "io_evaluate.output.recommendation_enum_values",
        "io_evaluate.output.reason_present",
        "io_evaluate.output.minimal_corrected_text_field_present",
        "io_evaluate.output.minimal_corrected_text_nullability_matches_recommendation",
        "io_evaluate.output.hard_constraint_rejections_array",
        "io_evaluate.output.rejection_item_id_present",
        "io_evaluate.output.rejection_constraint_hit_present",
        "io_evaluate.output.rejection_note_present",
        "io_evaluate.output.hard_constraint_rejection_skips_checklist",
        "io_evaluate.output.agent_identified_findings_array",
        "io_evaluate.output.agent_identified_item_id_present",
        "io_evaluate.output.agent_identified_origin_value",
        "io_evaluate.output.agent_identified_defect_category_present",
        "io_evaluate.output.agent_identified_defect_category_matches_supplied",
        "io_evaluate.output.agent_identified_priority_present",
        "io_evaluate.output.agent_identified_recommendation_present",
        "io_evaluate.output.agent_identified_reason_present",
        "io_evaluate.output.agent_identified_finding_has_corrected_text_field",
        "io_evaluate.output.agent_identified_finding_corrected_text_nullability_matches_recommendation",
        "io_evaluate.output.supplied_and_agent_identified_corrected_text_same_nullability",
        "io_evaluate.output.convergence_assessment_present",
        "io_evaluate.output.scope_trend_present",
        "io_evaluate.output.scope_trend_enum_values",
        "io_evaluate.output.comparison_note_present",
    ],
    "test_apply_input_schema.py": [
        "io_apply.input.task_is_apply",
        "io_apply.input.chapter_id_present",
        "io_apply.input.chapter_text_present",
        "io_apply.input.pass_number_present",
        "io_apply.input.approved_items_array",
        "io_apply.input.approved_item_id_present",
        "io_apply.input.approved_item_recommendation_present",
        "io_apply.input.approved_item_minimal_corrected_text_present",
        "io_apply.input.direct_instructions_array",
        "io_apply.input.direct_instruction_action_field",
        "io_apply.input.next_chapter_context",
        "io_apply.input.invalid_recommendation_reported_in_input_errors",
    ],
    "test_apply_hard_constraint_self_check.py": [
        "io_apply.output.hard_constraint_self_check.no_cross_reference_invalidated",
        "io_apply.output.hard_constraint_self_check.no_section_reordered_added_removed",
        "io_apply.output.hard_constraint_self_check.no_protected_passage_diluted",
        "io_apply.output.hard_constraint_self_check.no_code_block_changed",
        "io_apply.output.hard_constraint_self_check_notes_populated_on_failure",
    ],
    "test_apply_output_schema.py": [
        "io_apply.output.revised_chapter_text_present",
        "io_apply.output.change_log_array",
        "io_apply.output.change_log_item_id_present",
        "io_apply.output.change_log_section_present",
        "io_apply.output.change_log_before_excerpt_present",
        "io_apply.output.change_log_after_excerpt_present",
        "io_apply.output.deviations_from_review_wording_array",
        "io_apply.output.deviation_item_id_present",
        "io_apply.output.deviation_reason_present",
        "io_apply.output.input_errors_array",
        "io_apply.output.input_error_item_id_present",
        "io_apply.output.input_error_problem_present",
    ],
    "test_amendment_fields.py": [
        "meta.amendment_1_supersedes_base_contract_for_agent_identified_findings",
    ],
}

assert len(CASE_BUILDERS) == 111
assert sum(len(v) for v in FILE_GROUPS.values()) == 111
