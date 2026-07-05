"""Cross-check structural suite registration against reference matrix."""

from __future__ import annotations

from structural_suite.checkers import REGISTRY
from tests.structural.conftest import load_in_scope_structural_ids, scenario_id
from tests.structural.case_map import FILE_GROUPS


def test_registry_covers_all_in_scope_structural_rows() -> None:
    """Covers: matrix cross-check — every in-scope STRUCTURAL row has a checker."""
    expected = set(load_in_scope_structural_ids())
    assert set(REGISTRY) == expected


def test_case_map_covers_all_in_scope_structural_rows() -> None:
    """Covers: matrix cross-check — every in-scope STRUCTURAL row has compliant/violating cases."""
    from tests.structural.case_map import CASE_BUILDERS

    expected = set(load_in_scope_structural_ids())
    assert set(CASE_BUILDERS) == expected


def test_file_groups_account_for_all_structural_rows() -> None:
    """Covers: matrix cross-check — file groupings partition the 111 rows."""
    grouped: list[str] = []
    for req_ids in FILE_GROUPS.values():
        grouped.extend(req_ids)
    assert len(grouped) == 111
    assert len(set(grouped)) == 111
