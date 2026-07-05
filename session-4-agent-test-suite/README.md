# Session 4 — Agent Test Suite

## Run structural tests

```bash
cd session-4-agent-test-suite
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest tests/structural/ -v
```

### Scenario ID convention

Each structural test function name is the scenario ID consumed by Session 3's
`find_uncovered` tool: `test_` + the matrix `requirement_id` with `.` replaced
by `_`.

Example: `tests/structural/test_evaluate_output_schema.py::test_io_evaluate_output_item_priority_enum`
covers `io_evaluate.output.item_priority_enum`.

### Structural file groupings

| File | Rows | Grouping rationale |
|------|------|--------------------|
| `test_playbook_role.py` | 2 | Playbook invocation boundaries |
| `test_hard_constraints.py` | 4 | Hard-constraint enforcement (evaluate rejections + apply self-check) |
| `test_playbook_evaluate_output.py` | 15 | Playbook-mandated EVALUATE output shape |
| `test_playbook_apply.py` | 7 | Playbook-mandated APPLY output shape |
| `test_evaluate_input_schema.py` | 18 | `io-contract-evaluate.md` input |
| `test_evaluate_output_schema.py` | 35 | Evaluate output (base + amended agent findings) |
| `test_apply_input_schema.py` | 12 | `io-contract-apply.md` input |
| `test_apply_hard_constraint_self_check.py` | 5 | Self-check booleans + notes-on-failure |
| `test_apply_output_schema.py` | 12 | Remaining APPLY output fields |
| `test_amendment_fields.py` | 1 | Amendment supersession meta-row |

Fixtures live in `tests/structural/fixtures/`. Validators live in
`src/structural_suite/`. Reference matrix copy:
`reference/matrix.yaml`.

## Ambiguity resolutions

### `playbook.evaluate.seven_dimensions_always_written`

The matrix notes the playbook step 3 heading says "seven dimensions" but lists 8 bullets if `reason` is counted separately from `recommendation`. This suite adopts the **8-field reading**: all entries in `ITEM_DIMENSION_FIELDS` (`priority`, five impact fields, `recommendation`, `reason`), matching the EVALUATE output contract where `recommendation` and `reason` are always distinct keys. The compliant baseline fixture (`EVALUATE_ITEM`) includes all 8.

## Presence-check deleted-key variants

Three representative `*_present` requirements run an extra assertion inside the existing test function (via `run_pair`): after the empty-string violating case, the checker is also run against a bundle where the field **key is absent** (not merely empty). This verifies the distinct code paths for `_check_evaluate_output_item_string_field`, `_check_present`, and `_check_item_field_present` without duplicating all ~50 presence checks. Covered requirement IDs:

- `io_evaluate.output.item_id_present` — item string-field funnel (`.get()` + `_non_empty_string`)
- `io_evaluate.input.chapter_id_present` — `_check_present` (`part not in cur`)
- `playbook.evaluate.reason_field_present` — playbook item `_check_item_field_present`
