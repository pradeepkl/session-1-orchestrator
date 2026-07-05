"""Shared enum and schema constants from the I/O contracts."""

from __future__ import annotations

PRIORITY_VALUES = frozenset({"CRITICAL", "HIGH", "MEDIUM", "LOW"})

RECOMMENDATION_VALUES = frozenset(
    {
        "APPLY",
        "APPLY_SELECTIVELY",
        "APPLY_WITH_CARE",
        "RESOLVED_AS_SIDE_EFFECT",
        "DO_NOT_APPLY",
    }
)

APPLY_ELIGIBLE_RECOMMENDATIONS = frozenset(
    {"APPLY", "APPLY_SELECTIVELY", "APPLY_WITH_CARE"}
)

SCOPE_TREND_VALUES = frozenset(
    {"shrinking", "flat", "growing", "baseline_round_1"}
)

HARD_CONSTRAINT_HITS = frozenset(
    {
        "no_breaking_changes",
        "no_major_structural_changes",
        "no_section_dilution",
        "no_code_listing_changes",
        "purely_editorial",
    }
)

EVALUATE_OUTPUT_TOP_LEVEL_KEYS = frozenset(
    {
        "items",
        "hard_constraint_rejections",
        "agent_identified_findings",
        "convergence_assessment",
    }
)

APPLY_OUTPUT_TOP_LEVEL_KEYS = frozenset(
    {
        "revised_chapter_text",
        "change_log",
        "deviations_from_review_wording",
        "hard_constraint_self_check",
        "input_errors",
    }
)

SELF_CHECK_BOOLEAN_KEYS = frozenset(
    {
        "no_cross_reference_invalidated",
        "no_section_reordered_added_removed",
        "no_protected_passage_diluted",
        "no_code_block_changed",
    }
)

ITEM_DIMENSION_FIELDS = (
    "priority",
    "signal_to_noise_impact",
    "essence_risk",
    "verbosity_impact",
    "readability_impact",
    "repetition_impact",
    "recommendation",
    "reason",
)
