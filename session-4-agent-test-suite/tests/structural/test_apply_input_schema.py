"""Structural tests — auto-generated case wiring; do not edit by hand."""

from __future__ import annotations

from tests.structural.case_map import make_case
from tests.structural.conftest import Case, run_pair

def test_io_apply_input_task_is_apply() -> None:
    """Covers: io_apply.input.task_is_apply"""
    run_pair(make_case('io_apply.input.task_is_apply'))

def test_io_apply_input_chapter_id_present() -> None:
    """Covers: io_apply.input.chapter_id_present"""
    run_pair(make_case('io_apply.input.chapter_id_present'))

def test_io_apply_input_chapter_text_present() -> None:
    """Covers: io_apply.input.chapter_text_present"""
    run_pair(make_case('io_apply.input.chapter_text_present'))

def test_io_apply_input_pass_number_present() -> None:
    """Covers: io_apply.input.pass_number_present"""
    run_pair(make_case('io_apply.input.pass_number_present'))

def test_io_apply_input_approved_items_array() -> None:
    """Covers: io_apply.input.approved_items_array"""
    run_pair(make_case('io_apply.input.approved_items_array'))

def test_io_apply_input_approved_item_id_present() -> None:
    """Covers: io_apply.input.approved_item_id_present"""
    run_pair(make_case('io_apply.input.approved_item_id_present'))

def test_io_apply_input_approved_item_recommendation_present() -> None:
    """Covers: io_apply.input.approved_item_recommendation_present"""
    run_pair(make_case('io_apply.input.approved_item_recommendation_present'))

def test_io_apply_input_approved_item_minimal_corrected_text_present() -> None:
    """Covers: io_apply.input.approved_item_minimal_corrected_text_present"""
    run_pair(make_case('io_apply.input.approved_item_minimal_corrected_text_present'))

def test_io_apply_input_direct_instructions_array() -> None:
    """Covers: io_apply.input.direct_instructions_array"""
    run_pair(make_case('io_apply.input.direct_instructions_array'))

def test_io_apply_input_direct_instruction_action_field() -> None:
    """Covers: io_apply.input.direct_instruction_action_field"""
    run_pair(make_case('io_apply.input.direct_instruction_action_field'))

def test_io_apply_input_next_chapter_context() -> None:
    """Covers: io_apply.input.next_chapter_context"""
    run_pair(make_case('io_apply.input.next_chapter_context'))

def test_io_apply_input_invalid_recommendation_reported_in_input_errors() -> None:
    """Covers: io_apply.input.invalid_recommendation_reported_in_input_errors"""
    run_pair(make_case('io_apply.input.invalid_recommendation_reported_in_input_errors'))

