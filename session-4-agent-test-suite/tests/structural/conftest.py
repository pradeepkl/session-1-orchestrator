"""Shared structural test helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
import yaml

from structural_suite.checkers import PayloadBundle, StructuralViolation, check_requirement
from tests.structural.fixtures.evaluate_apply import (
    APPLY_INPUT,
    APPLY_OUTPUT,
    EVALUATE_INPUT,
    EVALUATE_OUTPUT,
    clone,
)

MATRIX_PATH = Path(__file__).resolve().parents[2] / "reference" / "matrix.yaml"

IN_SCOPE_DOCS = {
    "agent-judgment-playbook.md",
    "io-contract-evaluate.md",
    "io-contract-apply.md",
    "io-contract-evaluate.md (as amended by io-contract-evaluate-ammendum.md)",
    "io-contract-evaluate-ammendum.md",
}


def scenario_id(requirement_id: str) -> str:
    """Scenario ID = pytest node name: test_<requirement_id with dots -> underscores>."""
    return "test_" + requirement_id.replace(".", "_")


def load_in_scope_structural_ids() -> list[str]:
    matrix = yaml.safe_load(MATRIX_PATH.read_text())
    return sorted(
        entry["requirement_id"]
        for entry in matrix
        if entry["source_document"] in IN_SCOPE_DOCS
        and entry["classification"] == "STRUCTURAL"
    )


def default_bundle() -> PayloadBundle:
    return PayloadBundle(
        evaluate_input=clone(EVALUATE_INPUT),
        evaluate_output=clone(EVALUATE_OUTPUT),
        apply_input=clone(APPLY_INPUT),
        apply_output=clone(APPLY_OUTPUT),
    )


@dataclass
class Case:
    requirement_id: str
    compliant: PayloadBundle
    violating: PayloadBundle
    violating_absent_key: PayloadBundle | None = None


def assert_requirement_passes(requirement_id: str, bundle: PayloadBundle) -> None:
    check_requirement(requirement_id, bundle)


def assert_requirement_fails(requirement_id: str, bundle: PayloadBundle) -> None:
    with pytest.raises(StructuralViolation) as exc_info:
        check_requirement(requirement_id, bundle)
    assert exc_info.value.requirement_id == requirement_id


def run_pair(case: Case) -> None:
    assert_requirement_passes(case.requirement_id, case.compliant)
    assert_requirement_fails(case.requirement_id, case.violating)
    if case.violating_absent_key is not None:
        assert_requirement_fails(case.requirement_id, case.violating_absent_key)
