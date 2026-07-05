"""Tests for requirements traceability matrix checker."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from traceability import RequirementRecord, find_uncovered, load_matrix

MATRIX_PATH = Path(__file__).resolve().parent.parent / "data" / "matrix.yaml"


def test_real_matrix_validates_against_schema() -> None:
    records = load_matrix(MATRIX_PATH)
    assert records, "matrix.yaml must contain at least one requirement entry"
    for record in records:
        assert record.classification in {"STRUCTURAL", "JUDGMENT"}
        assert record.requirement_id
        assert record.source_document
        assert record.source_locator
        assert record.statement
        assert record.classification_rationale
        assert isinstance(record.covering_test_scenario_ids, list)


def test_find_uncovered_empty_list_and_stale_scenario_ids() -> None:
    fixture = [
        RequirementRecord(
            requirement_id="fixture.uncovered.empty",
            source_document="fixture.md",
            source_locator="Fixture > empty",
            statement="Entry with no covering scenarios is uncovered.",
            classification="STRUCTURAL",
            classification_rationale="Fixture control.",
            covering_test_scenario_ids=[],
            notes=None,
        ),
        RequirementRecord(
            requirement_id="fixture.uncovered.stale_id",
            source_document="fixture.md",
            source_locator="Fixture > stale",
            statement="Entry citing a deleted scenario ID is uncovered.",
            classification="STRUCTURAL",
            classification_rationale="Fixture control.",
            covering_test_scenario_ids=["deleted-scenario"],
            notes=None,
        ),
        RequirementRecord(
            requirement_id="fixture.covered.valid",
            source_document="fixture.md",
            source_locator="Fixture > covered",
            statement="Entry citing an existing scenario ID is covered.",
            classification="STRUCTURAL",
            classification_rationale="Fixture control.",
            covering_test_scenario_ids=["active-scenario"],
            notes=None,
        ),
    ]

    uncovered = find_uncovered(fixture, {"active-scenario"})
    uncovered_ids = {record.requirement_id for record in uncovered}
    assert uncovered_ids == {
        "fixture.uncovered.empty",
        "fixture.uncovered.stale_id",
    }


def test_find_uncovered_all_covered_returns_empty() -> None:
    fixture = [
        RequirementRecord(
            requirement_id="fixture.covered.one",
            source_document="fixture.md",
            source_locator="Fixture > one",
            statement="Covered by scenario-a.",
            classification="STRUCTURAL",
            classification_rationale="Fixture control.",
            covering_test_scenario_ids=["scenario-a"],
            notes=None,
        ),
        RequirementRecord(
            requirement_id="fixture.covered.two",
            source_document="fixture.md",
            source_locator="Fixture > two",
            statement="Covered by scenario-b.",
            classification="STRUCTURAL",
            classification_rationale="Fixture control.",
            covering_test_scenario_ids=["scenario-b"],
            notes=None,
        ),
    ]

    assert find_uncovered(fixture, {"scenario-a", "scenario-b"}) == []


def test_amendment_seed_entries_present_as_structural() -> None:
    records = load_matrix(MATRIX_PATH)
    by_id = {record.requirement_id: record for record in records}

    required_ids = (
        "io_evaluate.output.agent_identified_finding_has_corrected_text_field",
        "io_evaluate.output.agent_identified_finding_corrected_text_nullability_matches_recommendation",
    )
    for requirement_id in required_ids:
        assert requirement_id in by_id, f"Missing seed entry {requirement_id!r}"
        assert by_id[requirement_id].classification == "STRUCTURAL"


def test_load_matrix_rejects_invalid_classification(tmp_path: Path) -> None:
    bad_matrix = [
        {
            "requirement_id": "bad.classification",
            "source_document": "fixture.md",
            "source_locator": "Fixture",
            "statement": "Bad classification value.",
            "classification": "MIXED",
            "classification_rationale": "Fixture.",
            "covering_test_scenario_ids": [],
            "notes": None,
        }
    ]
    path = tmp_path / "matrix.yaml"
    path.write_text(yaml.dump(bad_matrix), encoding="utf-8")

    with pytest.raises(ValueError, match="bad.classification"):
        load_matrix(path)
