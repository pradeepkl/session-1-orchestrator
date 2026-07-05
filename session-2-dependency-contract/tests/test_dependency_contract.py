"""Tests for mechanical governing-document dependency checks."""

from __future__ import annotations

from pathlib import Path

from dependency_contract import (
    DOC_FILENAMES,
    checklist_question_count,
    hard_constraint_count,
    check_all_from_dir,
)

ROOT = Path(__file__).resolve().parent.parent
CANONICAL = ROOT / "fixtures" / "canonical"

NOT_AUTOMATABLE_ASSUMPTION_IDS = (
    "hard_constraint_source_verbatim_match",
    "defect_category_description_accuracy",
    "checklist_question_substance_validity",
    "book_spine_precedent_alignment",
    "protected_callout_semantic_equivalence",
)


def _result_by_id(results, assumption_id: str):
    return next(r for r in results if r.assumption_id == assumption_id)


def test_canonical_fixtures_all_pass():
    results = check_all_from_dir(CANONICAL)
    for result in results:
        print(result)
    assert results, "expected at least one CheckResult"
    for result in results:
        assert result.passed is True, result


def test_mutated_defect_category_only_defect_count_fails():
    results = check_all_from_dir(ROOT / "fixtures" / "mutated_defect_category")
    defect = _result_by_id(results, "defect_category_count")
    assert defect.passed is False
    assert defect.expected == 10
    assert defect.found == 9
    for result in results:
        if result.assumption_id == "defect_category_count":
            continue
        assert result.passed is True, result


def test_mutated_checklist_question_only_checklist_count_fails():
    results = check_all_from_dir(ROOT / "fixtures" / "mutated_checklist_question")
    checklist = _result_by_id(results, "checklist_question_count")
    assert checklist.passed is False
    assert checklist.expected == 7
    assert checklist.found == 6
    for result in results:
        if result.assumption_id == "checklist_question_count":
            continue
        assert result.passed is True, result


def test_mutated_protected_callout_only_protected_names_fail():
    results = check_all_from_dir(ROOT / "fixtures" / "mutated_protected_callout")
    protected = _result_by_id(results, "protected_callout_names_present")
    assert protected.passed is False
    assert "recap" in protected.detail.lower()
    assert "recap" in protected.expected["summary_recap_in_process"]
    assert "recap" not in protected.found["summary_recap_in_process"]
    for result in results:
        if result.assumption_id == "protected_callout_names_present":
            continue
        assert result.passed is True, result


def test_missing_stated_count_fails_instead_of_silent_pass():
    docs = {name: (CANONICAL / name).read_text(encoding="utf-8") for name in DOC_FILENAMES}
    docs["agent-judgment-playbook.md"] = docs["agent-judgment-playbook.md"].replace(
        "seven-question checklist", "multi-part checklist"
    )
    addendum = docs["editorial-review-process-addendum-go-no-go.md"]
    start = addendum.index("7. **Conversational tone**")
    end = addendum.index("\n\n## Decision rule")
    docs["editorial-review-process-addendum-go-no-go.md"] = addendum[:start] + addendum[end:]

    result = checklist_question_count(docs)
    assert result.passed is False
    assert result.expected is None
    assert result.found == 6
    assert "could not find" in result.detail.lower()
    assert "cannot verify checklist_question_count" in result.detail


def test_sixth_hard_constraint_bullet_fails_count():
    docs = {name: (CANONICAL / name).read_text(encoding="utf-8") for name in DOC_FILENAMES}
    docs["agent-judgment-playbook.md"] = docs["agent-judgment-playbook.md"].replace(
        "- **Purely editorial** —",
        "- **Extra constraint** — should not be here.\n- **Purely editorial** —",
    )

    result = hard_constraint_count(docs)
    assert result.passed is False
    assert result.expected == 5
    assert result.found == 6


def test_recommendation_scale_parses_line_wrapped_apply_with_care():
    from dependency_contract import _extract_recommendation_scales

    text = (
        "replace the existing recommendation scale (APPLY / APPLY SELECTIVELY / APPLY\n"
        "WITH CARE / RESOLVED AS SIDE EFFECT / DO NOT APPLY)"
    )
    tokens = _extract_recommendation_scales(text)
    assert tokens == [
        "APPLY",
        "APPLY SELECTIVELY",
        "APPLY WITH CARE",
        "RESOLVED AS SIDE EFFECT",
        "DO NOT APPLY",
    ]


def test_not_automatable_assumptions_are_not_implemented():
    results = check_all_from_dir(CANONICAL)
    implemented_ids = {result.assumption_id for result in results}
    for assumption_id in NOT_AUTOMATABLE_ASSUMPTION_IDS:
        assert assumption_id not in implemented_ids
