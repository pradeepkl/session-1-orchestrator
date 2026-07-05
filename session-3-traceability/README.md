# Session 3 — Traceability

Requirements traceability matrix and checker for editorial automation sessions.
Runtime dependency is **PyYAML only** (plus Python 3.11+); development installs use
**pytest** via `pyproject.toml` optional `dev` extras.

## Install

```bash
cd session-3-traceability
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run tests

```bash
pytest -q
```

## Project layout

```
session-3-traceability/
├── README.md
├── pyproject.toml
├── spec.md
├── src/traceability.py
├── data/matrix.yaml
└── tests/test_traceability.py
```

Implement against `spec.md` as fixed ground truth.

## Regenerating `data/matrix.yaml` when upstream specs change

1. **Identify which source document changed** among the six effective inputs
   listed in `spec.md` section 0:
   - `agent-judgment-playbook.md`
   - `io-contract-evaluate.md` **plus** any `io-contract-evaluate-ammendum.md`
     (treat as one effective schema)
   - `io-contract-apply.md`
   - `session-1-orchestrator-spec.md` (canonical `spec.md` in
     `session-1-orchestrator/docs/` plus its addendum file)
   - `session-2-dependency-contract/spec.md`

2. **Re-scan only the changed document(s)** and re-derive requirement entries
   using section 2's granularity and classification rules. For each new or
   changed requirement, assign a stable `requirement_id` and empty
   `covering_test_scenario_ids` until Session 4 maps scenarios.

3. **Preserve `covering_test_scenario_ids` for unchanged requirements.** When
   merging an updated matrix, match on `requirement_id` (or on
   `source_document` + `source_locator` + `statement` if an ID was renamed).
   Copy the existing scenario ID list onto entries whose underlying requirement
   text did not change. Re-derive entries whose source sentence changed and
   reset their scenario list to `[]`.

4. **Amendment-combining convention** (`spec.md` section 0): when an amendment
   file changes an I/O contract, **supersede** the base-matrix entry for the
   pre-amendment shape — do not keep a parallel entry for the old field layout.
   Add one additional `meta.*` entry documenting what changed and how downstream
   code must handle the amended shape (see
   `meta.amendment_1_supersedes_base_contract_for_agent_identified_findings` in
   section 4). Future amendments follow the same pattern.

Canonical source paths in this repo:

| Logical document | Repo path |
|---|---|
| Playbook | `session-1-orchestrator/docs/agent-judgment-playbook.md` |
| EVALUATE contract | `session-1-orchestrator/docs/io-contract-evaluate.md` |
| EVALUATE amendment | `session-1-orchestrator/docs/io-contract-evaluate-ammendum.md` |
| APPLY contract | `session-1-orchestrator/docs/io-contract-apply.md` |
| Orchestrator spec | `session-1-orchestrator/docs/spec.md` + `session-1-orchestrator/docs/session-1-orchestrator-spec.md` |
| Dependency contract | `session-2-dependency-contract/spec.md` |

## CI gate: `find_uncovered` before accepting Session 4 test changes

Once Session 4 defines scenario IDs, run this before merging test-suite changes:

```python
from pathlib import Path
from traceability import find_uncovered, load_matrix

MATRIX = Path("data/matrix.yaml")
# Replace with the authoritative scenario ID list from Session 4's registry:
EXISTING_SCENARIO_IDS = {
    "scenario.evaluate.hard_constraint_code_only",
    # ... full set from Session 4 ...
}

matrix = load_matrix(MATRIX)
gaps = find_uncovered(matrix, EXISTING_SCENARIO_IDS)
if gaps:
    ids = ", ".join(r.requirement_id for r in gaps)
    raise SystemExit(f"Uncovered requirements ({len(gaps)}): {ids}")
```

In CI, fail the job when `gaps` is non-empty. A requirement listing a scenario
ID that was deleted or renamed counts as uncovered — the tool checks that at
least one cited ID exists in `EXISTING_SCENARIO_IDS`, not merely that the list
is non-empty.
