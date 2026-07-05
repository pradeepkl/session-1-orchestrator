"""Structural tests — auto-generated case wiring; do not edit by hand."""

from __future__ import annotations

from tests.structural.case_map import make_case
from tests.structural.conftest import Case, run_pair

def test_io_evaluate_input_task_is_evaluate() -> None:
    """Covers: io_evaluate.input.task_is_evaluate"""
    run_pair(make_case('io_evaluate.input.task_is_evaluate'))

def test_io_evaluate_input_chapter_id_present() -> None:
    """Covers: io_evaluate.input.chapter_id_present"""
    run_pair(make_case('io_evaluate.input.chapter_id_present'))

def test_io_evaluate_input_chapter_text_present() -> None:
    """Covers: io_evaluate.input.chapter_text_present"""
    run_pair(make_case('io_evaluate.input.chapter_text_present'))

def test_io_evaluate_input_pass_number_present() -> None:
    """Covers: io_evaluate.input.pass_number_present"""
    run_pair(make_case('io_evaluate.input.pass_number_present'))

def test_io_evaluate_input_max_passes_present() -> None:
    """Covers: io_evaluate.input.max_passes_present"""
    run_pair(make_case('io_evaluate.input.max_passes_present'))

def test_io_evaluate_input_review_comments_array() -> None:
    """Covers: io_evaluate.input.review_comments_array"""
    run_pair(make_case('io_evaluate.input.review_comments_array'))

def test_io_evaluate_input_review_comments_may_be_empty() -> None:
    """Covers: io_evaluate.input.review_comments_may_be_empty"""
    run_pair(make_case('io_evaluate.input.review_comments_may_be_empty'))

def test_io_evaluate_input_review_comment_id_and_text() -> None:
    """Covers: io_evaluate.input.review_comment_id_and_text"""
    run_pair(make_case('io_evaluate.input.review_comment_id_and_text'))

def test_io_evaluate_input_governing_excerpts_present() -> None:
    """Covers: io_evaluate.input.governing_excerpts_present"""
    run_pair(make_case('io_evaluate.input.governing_excerpts_present'))

def test_io_evaluate_input_governing_excerpts_defect_categories() -> None:
    """Covers: io_evaluate.input.governing_excerpts_defect_categories"""
    run_pair(make_case('io_evaluate.input.governing_excerpts_defect_categories'))

def test_io_evaluate_input_governing_excerpts_seven_question_checklist() -> None:
    """Covers: io_evaluate.input.governing_excerpts_seven_question_checklist"""
    run_pair(make_case('io_evaluate.input.governing_excerpts_seven_question_checklist'))

def test_io_evaluate_input_governing_excerpts_style_rules() -> None:
    """Covers: io_evaluate.input.governing_excerpts_style_rules"""
    run_pair(make_case('io_evaluate.input.governing_excerpts_style_rules'))

def test_io_evaluate_input_governing_excerpts_protected_passages() -> None:
    """Covers: io_evaluate.input.governing_excerpts_protected_passages"""
    run_pair(make_case('io_evaluate.input.governing_excerpts_protected_passages'))

def test_io_evaluate_input_next_chapter_context_nullable() -> None:
    """Covers: io_evaluate.input.next_chapter_context_nullable"""
    run_pair(make_case('io_evaluate.input.next_chapter_context_nullable'))

def test_io_evaluate_input_prior_rounds_summary_empty_on_pass_one() -> None:
    """Covers: io_evaluate.input.prior_rounds_summary_empty_on_pass_one"""
    run_pair(make_case('io_evaluate.input.prior_rounds_summary_empty_on_pass_one'))

def test_io_evaluate_input_prior_rounds_summary_entry_shape() -> None:
    """Covers: io_evaluate.input.prior_rounds_summary_entry_shape"""
    run_pair(make_case('io_evaluate.input.prior_rounds_summary_entry_shape'))

def test_io_evaluate_input_direct_instructions_array() -> None:
    """Covers: io_evaluate.input.direct_instructions_array"""
    run_pair(make_case('io_evaluate.input.direct_instructions_array'))

def test_io_evaluate_input_direct_instructions_id_and_text() -> None:
    """Covers: io_evaluate.input.direct_instructions_id_and_text"""
    run_pair(make_case('io_evaluate.input.direct_instructions_id_and_text'))

