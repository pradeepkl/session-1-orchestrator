"""Structural tests — auto-generated case wiring; do not edit by hand."""

from __future__ import annotations

from tests.structural.case_map import make_case
from tests.structural.conftest import Case, run_pair

def test_playbook_role_exact_matching_io_contract_schema() -> None:
    """Covers: playbook.role.exact_matching_io_contract_schema"""
    run_pair(make_case('playbook.role.exact_matching_io_contract_schema'))

def test_playbook_role_single_task_per_invocation() -> None:
    """Covers: playbook.role.single_task_per_invocation"""
    run_pair(make_case('playbook.role.single_task_per_invocation'))

