# spec.md — Agent Test Suite (Session 4)
### Authored upstream (orchestrating session). Implementing session builds
### and tests against this document as fixed ground truth. Any perceived
### defect here is flagged back as a question, not silently corrected.

## 0. Scope — Q3 resolved, not carried forward

Session 3's `data/matrix.yaml` has 210 requirement entries from five source
groupings. This session is **in scope only for the 143 entries whose
`source_document` is one of the three canonical agent files**:
`agent-judgment-playbook.md`, `io-contract-evaluate.md` (as amended by
`io-contract-evaluate-ammendum.md`), `io-contract-apply.md`.

The remaining 67 entries — sourced from `session-1-orchestrator-spec.md`
(orchestrator rows) and `session-2-dependency-contract/spec.md`
(dependency-contract rows) — are **out of scope**. They are already covered
by those sessions' own accepted test suites (`session-1-orchestrator/tests/`,
`session-2-dependency-contract/tests/`). Do not duplicate that coverage
here. Do not write a structural test for
`orchestrator.pass_cap.fourth_evaluate_refused` or
`dependency_contract.hard_constraint_count`, for example — those already
have real tests upstream.

This resolves an ambiguity in how "at least 8 judgment scenarios" (a floor
in the original plan) interacts with "every JUDGMENT row has a judgment
test" (an exhaustiveness standard in the same plan's own verification
checklist): this spec follows the exhaustive standard for every in-scope
JUDGMENT row, and treats "at least 8" as a number that exhaustive coverage
should comfortably clear, not a target to stop at.

## 1. Purpose

Three coordinated pytest suites, each testing a different kind of claim
about the agent's behavior, all traceable back to specific rows in
Session 3's matrix:

- **`tests/structural/`** — pure Python assertions against fixture
  EVALUATE/APPLY payloads. No agent call. Validates the 118 in-scope
  STRUCTURAL rows: schema shape, field presence, enum membership,
  boolean-implies-string-nonempty rules, cross-array consistency.
- **`tests/judgment/`** — a fixture input, an expert-authored expected
  answer, and a rubric-scoring function. Calls a real or stubbed agent and
  *grades* the response; never a hard equality assertion. Covers the
  25 in-scope JUDGMENT rows.
- **`tests/multiturn/`** — scripted pass-1→2→3 scenarios exercising
  state that must persist or evolve correctly across rounds
  (working-file persistence, convergence-assessment correctness,
  pass-3-cap deferred-item reporting) — these are properties of a
  *sequence* of calls, not any single EVALUATE/APPLY invocation, so they
  don't map to one matrix row each; state that explicitly in each test's
  docstring instead of forcing a 1:1 row citation.

## 2. Matrix-row traceability convention

Every test function's docstring or a adjacent comment states which
matrix `requirement_id`(s) it covers, using this exact format so Session
3's `find_uncovered` tool can eventually be pointed at this suite's real
scenario IDs:

```python
def test_priority_enum_values_are_valid() -> None:
    """Covers: playbook.evaluate.priority_enum_values,
    io_evaluate.output.item_priority_enum"""
    ...
```

Each test function name IS the scenario ID Session 3's `find_uncovered`
will eventually check against — e.g.
`tests/structural/test_evaluate_fields.py::test_priority_enum_values_are_valid`
or a shorter derived ID you define consistently; state your exact
scenario-ID convention in `README.md` since Session 3's tool needs it
verbatim, not paraphrased.

## 3. `tests/structural/` — requirements

One file per logical grouping of the 118 in-scope STRUCTURAL rows (e.g.
`test_hard_constraints.py`, `test_evaluate_output_schema.py`,
`test_apply_output_schema.py`, `test_amendment_fields.py` — your choice
of file boundaries, state and justify the grouping in README.md).

- Fixture payloads live in `tests/structural/fixtures/` (or `src/fixtures/`
  if shared with judgment tests — your choice, document it) as literal
  dict/JSON matching the I/O contracts exactly.
- No agent calls, no stubs that pretend to be an agent — pure assertions
  against hand-authored fixture payloads representing both compliant and
  violating cases.
- For every Hard Constraint (5 rows) and every `hard_constraint_self_check`
  sub-field (4 rows) that is STRUCTURAL, include both a fixture that
  satisfies it and one that violates it, asserting the checker/test
  correctly distinguishes them — same "prove precision, not just
  detection" standard Session 2's tests were held to.
- Every matrix row you claim to cover must have at least one assertion
  that would fail if that specific requirement were violated — a test
  that merely instantiates a fixture and checks `assert True`-equivalent
  conditions doesn't count as coverage.

## 4. `tests/judgment/` — requirements

- One `src/judgment_scoring.py` module: a rubric-scoring helper, or
  small set of them, that takes an agent's actual response and an
  expert-authored expected answer/rubric and returns a graded result
  (e.g. a score, or a pass/fail against named rubric criteria) — not a
  hard equality check against expected text.
- For each in-scope JUDGMENT row, one scenario: a realistic fixture
  input (chapter excerpt + review comment(s), matching the EVALUATE or
  APPLY input schema), an expert-authored expected answer (what a
  correct EVALUATE/APPLY response should contain, written by you,
  justified against the playbook's own criteria — not invented
  arbitrarily), and a rubric that scores a real or stubbed agent's
  actual output against that expected answer.
- The stub/real-agent call itself must be injectable (same pattern as
  Session 1's orchestrator) so these tests can run against a stub during
  CI and against a real model on demand — do not hardcode a specific
  LLM API call inside a test.
- Since these are graded, not equality-asserted: state in each test what
  scoring threshold constitutes a pass (e.g. "at least 3 of 4 rubric
  criteria met") and justify that threshold, don't leave it arbitrary.

## 5. `tests/multiturn/` — requirements

At least 3 scripted multi-pass scenarios (pass 1 → 2 → 3), each proving
state genuinely carries forward rather than three independent tests
loosely stapled together:

1. **Working-file persistence** — the chapter text modified in pass 1's
   APPLY is what pass 2's EVALUATE actually receives (not a re-fetch of
   the original source) — this test must fail if pass 2 were accidentally
   given the pre-pass-1 text, so include an assertion that would catch
   that regression specifically, not just "the graph completed."
2. **`convergence_assessment` correctness across rounds** — pass 2 and
   pass 3's convergence assessment genuinely reflects pass 1/2's actual
   item counts and severity mix (from `prior_rounds_summary`), not a
   static or default value.
3. **Pass-3-cap deferred-item reporting** — when `max_passes` is hit with
   items still unresolved, those items are reported as deferred rather
   than silently dropped or silently marked resolved.

Each scenario's test must assert on data threaded from an earlier
simulated pass's *output*, not on three independently-constructed fixture
inputs that happen to share a `chapter_id`.

## 6. Injectable agent dependency

All three suites (especially judgment and multiturn) call the agent
through one injectable interface — a stub by default (deterministic,
no network, no real LLM cost in CI), swappable for a real model call.
Define this interface once, likely in `src/agent_client.py`, reused
across all three test directories. Document in README.md exactly how to
swap in a real model.

## 7. `README.md` requirements

- How to run each suite independently: `pytest tests/structural/`,
  `pytest tests/judgment/`, `pytest tests/multiturn/`, and all together.
- How to swap the stub agent for a real model in judgment/multiturn runs.
- The exact scenario-ID convention used (per section 2), so it can be fed
  directly into Session 3's `find_uncovered` tool without translation.
- A note that 67 matrix rows (orchestrator + dependency-contract sourced)
  are intentionally out of scope here per section 0, with a pointer to
  where their real coverage lives.

## 8. Definition of done (mirrors Sessions 2/3's discipline)

- [ ] Every in-scope STRUCTURAL row (118) has a real structural test that
      would fail if the requirement were violated — spot-checked, not
      trusted by count.
- [ ] Every in-scope JUDGMENT row (25) has a judgment scenario with a
      justified expected answer and a scored (not equality-asserted) test.
- [ ] At least 3 multiturn scenarios, each genuinely threading state from
      a prior simulated pass, not independently stapled fixtures.
- [ ] Structural suite actually run (`pytest tests/structural/ -v`), full
      output pasted.
- [ ] Judgment and multiturn suites run against the stub agent at minimum;
      full output pasted, not a summary.
- [ ] README documents the scenario-ID convention precisely enough that
      Session 3's `find_uncovered` could consume it directly.