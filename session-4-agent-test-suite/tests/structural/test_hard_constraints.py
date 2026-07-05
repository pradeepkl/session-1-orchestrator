"""Structural tests — auto-generated case wiring; do not edit by hand."""

from __future__ import annotations

from tests.structural.case_map import make_case
from tests.structural.conftest import Case, run_pair

def test_playbook_hard_constraint_apply_self_check_before_return() -> None:
    """Covers: playbook.hard_constraint.apply_self_check_before_return"""
    run_pair(make_case('playbook.hard_constraint.apply_self_check_before_return'))

def test_playbook_hard_constraint_evaluate_rejection_out_of_scope() -> None:
    """Covers: playbook.hard_constraint.evaluate_rejection_out_of_scope"""
    run_pair(make_case('playbook.hard_constraint.evaluate_rejection_out_of_scope'))

def test_playbook_hard_constraint_evaluate_skips_checklist() -> None:
    """Covers: playbook.hard_constraint.evaluate_skips_checklist"""
    run_pair(make_case('playbook.hard_constraint.evaluate_skips_checklist'))

def test_playbook_hard_constraint_no_code_listing_changes() -> None:
    """Covers: playbook.hard_constraint.no_code_listing_changes"""
    run_pair(make_case('playbook.hard_constraint.no_code_listing_changes'))

