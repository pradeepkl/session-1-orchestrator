"""Structural tests — auto-generated case wiring; do not edit by hand."""

from __future__ import annotations

from tests.structural.case_map import make_case
from tests.structural.conftest import Case, run_pair

def test_playbook_apply_change_log_per_approved_item() -> None:
    """Covers: playbook.apply.change_log_per_approved_item"""
    run_pair(make_case('playbook.apply.change_log_per_approved_item'))

def test_playbook_apply_closing_bridge_no_chapter_number() -> None:
    """Covers: playbook.apply.closing_bridge_no_chapter_number"""
    run_pair(make_case('playbook.apply.closing_bridge_no_chapter_number'))

def test_playbook_apply_closing_bridge_no_next_chapter_phrasing() -> None:
    """Covers: playbook.apply.closing_bridge_no_next_chapter_phrasing"""
    run_pair(make_case('playbook.apply.closing_bridge_no_next_chapter_phrasing'))

def test_playbook_apply_hard_constraint_boolean_self_check_block() -> None:
    """Covers: playbook.apply.hard_constraint_boolean_self_check_block"""
    run_pair(make_case('playbook.apply.hard_constraint_boolean_self_check_block'))

def test_playbook_apply_rejects_do_not_apply_as_input_error() -> None:
    """Covers: playbook.apply.rejects_do_not_apply_as_input_error"""
    run_pair(make_case('playbook.apply.rejects_do_not_apply_as_input_error'))

def test_playbook_apply_restructure_flags_input_error() -> None:
    """Covers: playbook.apply.restructure_flags_input_error"""
    run_pair(make_case('playbook.apply.restructure_flags_input_error'))

def test_playbook_apply_return_apply_contract_only() -> None:
    """Covers: playbook.apply.return_apply_contract_only"""
    run_pair(make_case('playbook.apply.return_apply_contract_only'))

