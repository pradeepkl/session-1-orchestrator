"""Violating fixture payloads — one focused mutation per requirement domain."""

from __future__ import annotations

from tests.structural.fixtures.evaluate_apply import (
    APPLY_INPUT,
    APPLY_OUTPUT,
    EVALUATE_INPUT,
    EVALUATE_OUTPUT,
    clone,
)

# --- evaluate input violations ---

EVALUATE_INPUT_MISSING_CHAPTER_ID = clone(EVALUATE_INPUT)
del EVALUATE_INPUT_MISSING_CHAPTER_ID["chapter_id"]

EVALUATE_INPUT_PASS_ONE_WITH_PRIOR = clone(EVALUATE_INPUT)
EVALUATE_INPUT_PASS_ONE_WITH_PRIOR["pass_number"] = 1
EVALUATE_INPUT_PASS_ONE_WITH_PRIOR["prior_rounds_summary"] = [
    {
        "pass_number": 1,
        "item_count": 1,
        "severity_mix": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 1, "LOW": 0},
        "applied_count": 0,
        "do_not_apply_count": 1,
    }
]

# --- evaluate output violations ---

EVALUATE_OUTPUT_EXTRA_TOP_LEVEL = clone(EVALUATE_OUTPUT)
EVALUATE_OUTPUT_EXTRA_TOP_LEVEL["unexpected_field"] = True

EVALUATE_OUTPUT_REJECTED_IN_ITEMS = clone(EVALUATE_OUTPUT)
EVALUATE_OUTPUT_REJECTED_IN_ITEMS["items"].append(
    {
        "item_id": "c2",
        "origin": "supplied_review",
        "priority": "LOW",
        "signal_to_noise_impact": "n/a",
        "essence_risk": "n/a",
        "verbosity_impact": "n/a",
        "readability_impact": "n/a",
        "repetition_impact": "n/a",
        "recommendation": "DO_NOT_APPLY",
        "reason": "Should not be here.",
        "minimal_corrected_text": None,
    }
)

EVALUATE_OUTPUT_NO_REJECTIONS = clone(EVALUATE_OUTPUT)
EVALUATE_OUTPUT_NO_REJECTIONS["hard_constraint_rejections"] = []

EVALUATE_OUTPUT_WRONG_CODE_CONSTRAINT = clone(EVALUATE_OUTPUT)
EVALUATE_OUTPUT_WRONG_CODE_CONSTRAINT["hard_constraint_rejections"] = [
    {
        "item_id": "c9",
        "constraint_hit": "no_major_structural_changes",
        "note": "Wrong constraint for code-listing test.",
    }
]

EVALUATE_OUTPUT_CODE_LISTING_REJECTION = clone(EVALUATE_OUTPUT)
EVALUATE_OUTPUT_CODE_LISTING_REJECTION["hard_constraint_rejections"] = [
    {
        "item_id": "c9",
        "constraint_hit": "no_code_listing_changes",
        "note": "Comment requires modifying a fenced code block.",
    }
]

EVALUATE_OUTPUT_BAD_PRIORITY = clone(EVALUATE_OUTPUT)
EVALUATE_OUTPUT_BAD_PRIORITY["items"][0]["priority"] = "URGENT"

EVALUATE_OUTPUT_MISSING_AGENT_TEXT_FIELD = clone(EVALUATE_OUTPUT)
for finding in EVALUATE_OUTPUT_MISSING_AGENT_TEXT_FIELD["agent_identified_findings"]:
    if finding["recommendation"] == "APPLY_SELECTIVELY":
        del finding["minimal_corrected_text"]

EVALUATE_OUTPUT_AGENT_TEXT_WHEN_DNA = clone(EVALUATE_OUTPUT)
EVALUATE_OUTPUT_AGENT_TEXT_WHEN_DNA["agent_identified_findings"][0]["minimal_corrected_text"] = "should be null"

EVALUATE_OUTPUT_BAD_DEFECT_CATEGORY = clone(EVALUATE_OUTPUT)
EVALUATE_OUTPUT_BAD_DEFECT_CATEGORY["agent_identified_findings"][0]["defect_category"] = "not_a_real_category"

EVALUATE_OUTPUT_BAD_SCOPE_TREND = clone(EVALUATE_OUTPUT)
EVALUATE_OUTPUT_BAD_SCOPE_TREND["convergence_assessment"]["scope_trend"] = "unknown"

# --- apply violations ---

APPLY_OUTPUT_EXTRA_TOP_LEVEL = clone(APPLY_OUTPUT)
APPLY_OUTPUT_EXTRA_TOP_LEVEL["debug"] = True

APPLY_OUTPUT_CHAPTER_NUMBER_BRIDGE = clone(APPLY_OUTPUT)
APPLY_OUTPUT_CHAPTER_NUMBER_BRIDGE["revised_chapter_text"] = (
    APPLY_OUTPUT["revised_chapter_text"] + "\n\nChapter 7 picks up the thread."
)

APPLY_OUTPUT_NEXT_CHAPTER_PHRASING = clone(APPLY_OUTPUT)
APPLY_OUTPUT_NEXT_CHAPTER_PHRASING["revised_chapter_text"] = (
    APPLY_OUTPUT["revised_chapter_text"] + "\n\nThe next chapter examines signatures."
)

APPLY_INPUT_DO_NOT_APPLY = clone(APPLY_INPUT)
APPLY_INPUT_DO_NOT_APPLY["approved_items"] = [
    {
        "item_id": "c9",
        "recommendation": "DO_NOT_APPLY",
        "minimal_corrected_text": "ignored",
    }
]

APPLY_OUTPUT_NO_INPUT_ERROR_FOR_DNA = clone(APPLY_OUTPUT)
APPLY_OUTPUT_NO_INPUT_ERROR_FOR_DNA["input_errors"] = []

APPLY_OUTPUT_RESTRUCTURE_ERROR = clone(APPLY_OUTPUT)
APPLY_OUTPUT_RESTRUCTURE_ERROR["input_errors"] = [
    {"item_id": "c9", "problem": "Approved item requires section restructure."}
]

APPLY_OUTPUT_MISSING_CHANGE_LOG_FOR_APPROVED = clone(APPLY_OUTPUT)
APPLY_OUTPUT_MISSING_CHANGE_LOG_FOR_APPROVED["change_log"] = []

APPLY_OUTPUT_MISSING_SELF_CHECK = clone(APPLY_OUTPUT)
del APPLY_OUTPUT_MISSING_SELF_CHECK["hard_constraint_self_check"]

APPLY_OUTPUT_SELF_CHECK_FALSE_NO_NOTES = clone(APPLY_OUTPUT)
APPLY_OUTPUT_SELF_CHECK_FALSE_NO_NOTES["hard_constraint_self_check"] = {
    "no_cross_reference_invalidated": False,
    "no_section_reordered_added_removed": True,
    "no_protected_passage_diluted": True,
    "no_code_block_changed": True,
    "notes": "",
}

APPLY_OUTPUT_SELF_CHECK_NOTES_WHEN_ALL_TRUE = clone(APPLY_OUTPUT)
APPLY_OUTPUT_SELF_CHECK_NOTES_WHEN_ALL_TRUE["hard_constraint_self_check"]["notes"] = (
    "Should be empty when all checks pass."
)

APPLY_OUTPUT_SELF_CHECK_NOT_BOOL = clone(APPLY_OUTPUT)
APPLY_OUTPUT_SELF_CHECK_NOT_BOOL["hard_constraint_self_check"]["no_code_block_changed"] = "yes"

APPLY_INPUT_WRONG_TASK = clone(APPLY_INPUT)
APPLY_INPUT_WRONG_TASK["task"] = "EVALUATE"

EVALUATE_INPUT_WRONG_TASK = clone(EVALUATE_INPUT)
EVALUATE_INPUT_WRONG_TASK["task"] = "APPLY"

APPLY_OUTPUT_BAD_TOP_LEVEL_KEYS = clone(APPLY_OUTPUT)
del APPLY_OUTPUT_BAD_TOP_LEVEL_KEYS["input_errors"]

EVALUATE_OUTPUT_BAD_TOP_LEVEL_KEYS = clone(EVALUATE_OUTPUT)
del EVALUATE_OUTPUT_BAD_TOP_LEVEL_KEYS["convergence_assessment"]
