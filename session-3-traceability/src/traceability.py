"""Requirements traceability matrix checker."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import yaml

Classification = Literal["STRUCTURAL", "JUDGMENT"]

VALID_CLASSIFICATIONS: frozenset[str] = frozenset({"STRUCTURAL", "JUDGMENT"})

REQUIRED_FIELDS: tuple[str, ...] = (
    "requirement_id",
    "source_document",
    "source_locator",
    "statement",
    "classification",
    "classification_rationale",
    "covering_test_scenario_ids",
    "notes",
)


@dataclass(frozen=True)
class RequirementRecord:
    requirement_id: str
    source_document: str
    source_locator: str
    statement: str
    classification: Classification
    classification_rationale: str
    covering_test_scenario_ids: list[str]
    notes: str | None


def _validate_entry(raw: dict[str, Any], index: int) -> RequirementRecord:
    if not isinstance(raw, dict):
        raise ValueError(
            f"Matrix entry at index {index} must be a mapping, got {type(raw).__name__}"
        )

    requirement_id = raw.get("requirement_id")
    if not isinstance(requirement_id, str) or not requirement_id:
        bad_id = requirement_id if isinstance(requirement_id, str) else f"index-{index}"
        raise ValueError(f"requirement_id must be a non-empty string for entry {bad_id!r}")

    missing = [field for field in REQUIRED_FIELDS if field not in raw]
    if missing:
        raise ValueError(
            f"Requirement {requirement_id!r} is missing required field(s): "
            f"{', '.join(missing)}"
        )

    classification = raw["classification"]
    if classification not in VALID_CLASSIFICATIONS:
        raise ValueError(
            f"Requirement {requirement_id!r} has invalid classification "
            f"{classification!r}; expected one of {sorted(VALID_CLASSIFICATIONS)}"
        )

    covering = raw["covering_test_scenario_ids"]
    if not isinstance(covering, list) or not all(isinstance(item, str) for item in covering):
        raise ValueError(
            f"Requirement {requirement_id!r} covering_test_scenario_ids "
            "must be a list of strings"
        )

    notes = raw["notes"]
    if notes is not None and not isinstance(notes, str):
        raise ValueError(f"Requirement {requirement_id!r} notes must be a string or null")

    for field in ("source_document", "source_locator", "statement", "classification_rationale"):
        value = raw[field]
        if not isinstance(value, str) or not value:
            raise ValueError(
                f"Requirement {requirement_id!r} field {field!r} must be a non-empty string"
            )

    return RequirementRecord(
        requirement_id=requirement_id,
        source_document=raw["source_document"],
        source_locator=raw["source_locator"],
        statement=raw["statement"],
        classification=classification,
        classification_rationale=raw["classification_rationale"],
        covering_test_scenario_ids=list(covering),
        notes=notes,
    )


def load_matrix(path: str | Path) -> list[RequirementRecord]:
    """Load and validate data/matrix.yaml against the schema in spec.md section 2."""
    matrix_path = Path(path)
    with matrix_path.open(encoding="utf-8") as handle:
        raw_matrix = yaml.safe_load(handle)

    if not isinstance(raw_matrix, list):
        raise ValueError(f"Matrix file {matrix_path} must contain a YAML list at the top level")

    records: list[RequirementRecord] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(raw_matrix):
        record = _validate_entry(raw, index)
        if record.requirement_id in seen_ids:
            raise ValueError(f"Duplicate requirement_id {record.requirement_id!r}")
        seen_ids.add(record.requirement_id)
        records.append(record)

    return records


def find_uncovered(
    matrix: list[RequirementRecord],
    existing_scenario_ids: set[str],
) -> list[RequirementRecord]:
    """Return requirements with no valid covering scenario IDs."""
    uncovered: list[RequirementRecord] = []
    for record in matrix:
        cited = record.covering_test_scenario_ids
        if not cited:
            uncovered.append(record)
            continue
        if not any(scenario_id in existing_scenario_ids for scenario_id in cited):
            uncovered.append(record)
    return uncovered
