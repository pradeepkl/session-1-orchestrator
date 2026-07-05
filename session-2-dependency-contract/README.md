# Session 2 — Dependency Contract

Mechanical checks that the six governing editorial documents stay internally
consistent. This package has **no runtime dependencies** beyond Python 3.11+;
development installs use **pytest only** via `pyproject.toml` optional
`dev` extras (no `requirements.txt`).

## Install

```bash
cd session-2-dependency-contract
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run before accepting governing-document edits

Use this as a pre-commit hook or CI step **before** any change to the six
canonical files is merged:

```bash
cd session-2-dependency-contract
pytest -q
```

One-shot check without installing the package (from this directory):

```bash
PYTHONPATH=src python -c "from dependency_contract import check_all_from_dir; import sys; sys.exit(any(not r.passed for r in check_all_from_dir('fixtures/canonical')))"
```

Exit code `0` means all mechanical assumptions passed; `1` means at least one
failed.

## Worked example — all pass (`fixtures/canonical/`)

```bash
cd session-2-dependency-contract
PYTHONPATH=src python -c "
from dependency_contract import check_all_from_dir
for r in check_all_from_dir('fixtures/canonical'):
    print(r)
"
```

```
CheckResult(assumption_id='defect_category_count', passed=True, expected=10, found=10, detail='editorial-review-process.md declares 10 recurring defect categories and lists 10 numbered ### headings in the defect section.')
CheckResult(assumption_id='checklist_question_count', passed=True, expected=7, found=7, detail='agent-judgment-playbook.md declares 7 checklist questions and editorial-review-process-addendum-go-no-go.md lists 7 numbered questions.')
CheckResult(assumption_id='evaluate_dimension_count', passed=True, expected=7, found=7, detail='agent-judgment-playbook.md declares 7 EVALUATE write-up dimensions and editorial-review-process.md Phase 1 lists 7 assessed dimensions.')
CheckResult(assumption_id='hard_constraint_count', passed=True, expected=5, found=5, detail='agent-judgment-playbook.md Hard Constraints section should list 5 bold-labeled bullets (`- **...**`) and currently lists 5.')
CheckResult(assumption_id='protected_callout_names_present', passed=True, expected={'opening_scenario_in_process': ['opening', 'scenario'], 'when_not_to_use_in_style_guide': ['when not to use'], 'summary_recap_in_process': ['summary', 'recap']}, found={'opening_scenario_in_process': ['opening', 'scenario'], 'when_not_to_use_in_style_guide': ['when not to use'], 'summary_recap_in_process': ['summary', 'recap']}, detail='Each check tests case-insensitive substring presence of individual keywords (not exact phrase match). Missing: none.')
CheckResult(assumption_id='recommendation_scale_consistency', passed=True, expected=['APPLY', 'APPLY SELECTIVELY', 'APPLY WITH CARE', 'DO NOT APPLY', 'RESOLVED AS SIDE EFFECT OF ANOTHER ITEM'], found={'editorial-review-process-addendum-go-no-go.md': ['APPLY', 'APPLY SELECTIVELY', 'APPLY WITH CARE', 'RESOLVED AS SIDE EFFECT', 'DO NOT APPLY'], 'agent-judgment-playbook.md': ['APPLY', 'APPLY SELECTIVELY', 'APPLY WITH CARE', 'RESOLVED AS SIDE EFFECT', 'DO NOT APPLY']}, detail='Recommendation scale tokens in the addendum and playbook normalize to the editorial-review-process.md scale; mismatches: none.')
CheckResult(assumption_id='closing_bridge_convention_defined', passed=True, expected=['forward-pointing bridge', 'never a chapter number', 'Pattern:'], found=['forward-pointing bridge', 'never a chapter number', 'Pattern:'], detail="editorial-review-process.md must include 'The Closing-Bridge Convention' with required markers; missing: none.")
```

## Worked example — single failure (`fixtures/mutated_defect_category/`)

Deleting defect category `### 10.` from `editorial-review-process.md` yields:

```
CheckResult(assumption_id='defect_category_count', passed=False, expected=10, found=9, detail='editorial-review-process.md declares 10 recurring defect categories and lists 9 numbered ### headings in the defect section.')
```

All other checks in that run still pass.

## How to add a new assumption

1. Add the assumption to `spec.md` section 3 with a stable `assumption_id`,
   which document(s) it reads, and the exact mechanical rule.
2. Implement one typed function in `src/dependency_contract.py` returning
   `CheckResult`, with a plain-language docstring naming the source document(s).
3. Register it in `_ALL_CHECKERS` inside `check_all()` (keep non-short-circuit
   behaviour: always return the full list).
4. Add a passing assertion against `fixtures/canonical/` and, if possible, a
   mutated fixture that fails **only** that check.
5. If the assumption is judgment-only, list it in `spec.md` section 4 and add
   its `assumption_id` to `NOT_AUTOMATABLE_ASSUMPTION_IDS` in the test file —
   do **not** implement a mechanical checker for it.
