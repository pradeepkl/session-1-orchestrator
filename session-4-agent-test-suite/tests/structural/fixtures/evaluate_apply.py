"""Hand-authored compliant baseline payloads for structural tests."""

from __future__ import annotations

from copy import deepcopy

DEFECT_CATEGORIES = [
    "factual_error",
    "internal_inconsistency",
    "undefined_term",
    "missing_context",
    "overclaim",
    "underclaim",
    "structural_break",
    "voice_drift",
    "redundancy",
    "formatting",
]

SEVEN_QUESTION_CHECKLIST = [
    "Structural break?",
    "Genuine technical error vs stylistic preference?",
    "Chapter spine alignment?",
    "Book spine alignment?",
    "Readability/flow impact?",
    "Conciseness?",
    "Tone?",
]

STYLE_RULES = [
    "Do not reference chapter numbers in body prose.",
    "Avoid hedge words introduced for false precision.",
]

CHAPTER_TEXT = """# Chapter Six

A method throws an exception instead of returning a value.

## Summary

A bare `throw` and a bare, nullable return both hide uncertainty from callers.
"""

NEXT_CHAPTER_CONTEXT = "The next concept builds on visible uncertainty in signatures."

EVALUATE_INPUT = {
    "task": "EVALUATE",
    "chapter_id": "chapter06",
    "pass_number": 2,
    "max_passes": 3,
    "chapter_text": CHAPTER_TEXT,
    "review_comments": [
        {"comment_id": "c1", "text": "Optional is not the same as checked exceptions."},
        {"comment_id": "c2", "text": "Add a new section on generics."},
    ],
    "governing_excerpts": {
        "defect_categories": DEFECT_CATEGORIES,
        "seven_question_checklist": SEVEN_QUESTION_CHECKLIST,
        "style_rules": STYLE_RULES,
        "protected_passages": [
            {
                "name": "opening_scenario",
                "text_anchor": "A method throws an exception",
            },
            {
                "name": "summary_recap",
                "text_anchor": "A bare `throw` and a bare, nullable return",
            },
        ],
    },
    "next_chapter_context": NEXT_CHAPTER_CONTEXT,
    "prior_rounds_summary": [
        {
            "pass_number": 1,
            "item_count": 14,
            "severity_mix": {"CRITICAL": 2, "HIGH": 3, "MEDIUM": 5, "LOW": 4},
            "applied_count": 9,
            "do_not_apply_count": 5,
        }
    ],
    "direct_instructions": [
        {"instruction_id": "d1", "text": "chapter title should be Chapter Six"},
    ],
}

EVALUATE_ITEM = {
    "item_id": "c1",
    "origin": "supplied_review",
    "priority": "CRITICAL",
    "signal_to_noise_impact": "Removes a false equivalence.",
    "essence_risk": "Touches precision of the central thesis only.",
    "verbosity_impact": "neutral, same length",
    "readability_impact": "positive",
    "repetition_impact": "none",
    "recommendation": "APPLY",
    "reason": "Genuine technical error in the exception discussion.",
    "minimal_corrected_text": "Checked exceptions and Optional surface uncertainty differently.",
}

EVALUATE_OUTPUT = {
    "items": [deepcopy(EVALUATE_ITEM)],
    "hard_constraint_rejections": [
        {
            "item_id": "c2",
            "constraint_hit": "no_major_structural_changes",
            "note": "Comment requests adding a section, which violates no major structural changes.",
        }
    ],
    "agent_identified_findings": [
        {
            "item_id": "agent-1",
            "origin": "agent_identified",
            "defect_category": "redundancy",
            "priority": "LOW",
            "recommendation": "DO_NOT_APPLY",
            "reason": "Leaving the repeated phrase does not block finalizing the chapter.",
            "minimal_corrected_text": None,
        },
        {
            "item_id": "agent-2",
            "origin": "agent_identified",
            "defect_category": "factual_error",
            "priority": "MEDIUM",
            "recommendation": "APPLY_SELECTIVELY",
            "reason": "Minor factual imprecision in an example.",
            "minimal_corrected_text": "A method may throw instead of returning a value.",
        },
    ],
    "convergence_assessment": {
        "scope_trend": "shrinking",
        "comparison_note": "Round 2 raised 3 items vs round 1's 14; severity mix shifted toward LOW.",
    },
}

APPLY_INPUT = {
    "task": "APPLY",
    "chapter_id": "chapter06",
    "pass_number": 2,
    "chapter_text": CHAPTER_TEXT,
    "approved_items": [
        {
            "item_id": "c1",
            "recommendation": "APPLY",
            "minimal_corrected_text": "Checked exceptions and Optional surface uncertainty differently.",
        }
    ],
    "direct_instructions": [
        {
            "instruction_id": "d1",
            "text": "chapter title should be Chapter Six",
            "action": "apply_verbatim",
        }
    ],
    "next_chapter_context": NEXT_CHAPTER_CONTEXT,
}

REVISED_CHAPTER_TEXT = """# Chapter Six

Checked exceptions and Optional surface uncertainty differently.

## Summary

Visible uncertainty in signatures prepares readers for the design trade space ahead.
"""

APPLY_OUTPUT = {
    "revised_chapter_text": REVISED_CHAPTER_TEXT,
    "change_log": [
        {
            "item_id": "c1",
            "section": "Opening paragraph",
            "before_excerpt": "A method throws an exception instead of returning a value.",
            "after_excerpt": "Checked exceptions and Optional surface uncertainty differently.",
        }
    ],
    "deviations_from_review_wording": [
        {
            "item_id": "c1",
            "reason": "Review wording was longer than necessary for the sentence-level fix.",
        }
    ],
    "hard_constraint_self_check": {
        "no_cross_reference_invalidated": True,
        "no_section_reordered_added_removed": True,
        "no_protected_passage_diluted": True,
        "no_code_block_changed": True,
        "notes": "",
    },
    "input_errors": [],
}


def clone(payload: dict) -> dict:
    return deepcopy(payload)
