# spec.md — Traceability Tool (Session 3)
### Authored upstream (orchestrating session). Implementing session builds
### and tests against this document as fixed ground truth. Any perceived
### defect here is flagged back as a question, not silently corrected.

## 0. Source documents

This spec is drawn from six source documents, effective-combined where an
amendment applies:

1. `agent-judgment-playbook.md`
2. `io-contract-evaluate.md` **as amended by** `io-contract-evaluate-ammendum.md`
   (Amendment 1: `agent_identified_findings[].minimal_corrected_text` — see
   section 4)
3. `io-contract-apply.md`
4. `session-1-orchestrator-spec.md`
5. `session-2-dependency-contract/spec.md`

**Treat `io-contract-evaluate.md` + its Amendment 1 as one effective
schema, not two separate sources.** Every requirement entry derived from
`agent_identified_findings` must reflect the *amended* shape (field
present, conditionally non-null) — the pre-amendment shape no longer
exists and should not appear in the matrix except as a superseded note if
useful for history.

Per the amendment's own rationale, this was a genuine contract gap
surfaced by Session 1's build, not a workaround — so this matrix treats
the amended field as a first-class requirement with its own STRUCTURAL
entry, same as any other output field's presence/nullability rule.

Confirmed via repo-wide search (`find . -iname "*ammendum*" -o -iname
"*amendment*" -o -iname "*addendum*"` from repo root): this is the only
amendment file affecting any of the five source documents above. (The
other hits from that search were Session 2's own fixture copies of the
unrelated editorial go-no-go addendum — already accounted for, not a
second amendment to any of this session's inputs.)

## 1. Purpose

A traceability record format and a tool that answers one question: **for
every distinct requirement across the agent playbook, its two I/O
contracts, the orchestrator spec, and the dependency-contract spec, is
there at least one test scenario that actually exercises it?** This is not
a test suite itself (that's Session 4) — it's the map that tells Session 4
what it must cover, and later tells anyone editing an upstream document
what test coverage has gone stale.

## 2. Requirement record format

One entry per **distinct, independently-statable** requirement.

```yaml
- requirement_id: string          # stable, human-readable, namespaced by
                                   # source, e.g. "playbook.hard_constraint.no_code_listing_changes"
  source_document: string          # exact filename (or "filename as amended
                                   # by amendment-filename" per section 0)
  source_locator: string           # heading / field name / bullet text,
                                   # precise enough a human can find it in
                                   # 10 seconds without searching the whole file
  statement: string                # one plain-language sentence: what must
                                   # be true for this requirement to hold
  classification: STRUCTURAL | JUDGMENT
  classification_rationale: string # one line: why this classification,
                                   # not the other
  covering_test_scenario_ids: list[string]  # empty list is valid and
                                   # expected pre-Session-4 — that's the
                                   # gap this tool exists to surface
  notes: string | null             # optional — ambiguity, cross-reference
                                   # to a related requirement, etc.
```

### Granularity rule (the hardest part to get right)

A requirement is **one entry** if it can fail independently of every other
entry — i.e., you can construct a test scenario that violates *only* this
requirement and nothing else. Consequences:

- The playbook's 5 Hard Constraints are **5 separate entries**, not one
  "hard constraints" entry — each can be violated independently.
- The APPLY output's `hard_constraint_self_check` block has **4 boolean
  sub-fields**; these are 4 separate entries (each can independently be
  true/false), plus one more entry for "the `notes` field is populated
  whenever any flag above is false" (a relationship between fields, not a
  field itself — still independently testable, still its own entry).
- A single schema field's mere *existence* (e.g. "`item_id` is present on
  every EVALUATE item") is one entry; a *rule about that field's value*
  (e.g. "`recommendation` for a Hard-Constraint-failing comment is always
  exactly `DO_NOT_APPLY`, never any other value") is a **separate** entry,
  even though both concern the same field — existence and value-behavior
  fail independently. This same presence-vs-value split applies to the
  amendment's `minimal_corrected_text` field (see the two seed entries in
  section 4) — don't collapse them into one entry.
- Don't split a single indivisible sentence into multiple entries just to
  inflate the count (e.g. don't split "no reordering, adding, or removing
  sections" into three entries unless you can show a scenario that
  violates only "removing" without also being a reordering-adjacent
  case — if in doubt, keep it as one entry and say so in `notes`).

### STRUCTURAL vs. JUDGMENT — classification rule

- **STRUCTURAL**: a pure-Python assertion against a fixture payload
  settles it with no reading comprehension required — schema shape,
  field presence, an enum value, a count, a boolean flag, a routing/edge
  condition, a cap being enforced. If Session 2's spec.md already listed
  it as "mechanically checkable," it's STRUCTURAL here too.
- **JUDGMENT**: settling it requires an agent's (or human's) qualitative
  read of content — is this `reason` string actually convergence-framed,
  is this `essence_risk` assessment correct, did the seven-question
  checklist get applied with sound reasoning. These need an
  expert-authored expected answer and a graded rubric (Session 4's job),
  not a hard equality assertion.
- A requirement that's *structurally checkable in form* but whose
  *correctness* is judgment (e.g. "`reason` is a non-empty string" is
  STRUCTURAL; "`reason` is actually convergence-framed" is JUDGMENT) gets
  **two separate entries**, one per classification — don't collapse them
  into one entry with a mixed classification, since that would let a
  JUDGMENT gap hide behind a passing STRUCTURAL test.

## 3. Tool behavior — `src/traceability.py`

```python
def load_matrix(path: str | Path) -> list[RequirementRecord]:
    """Load and validate data/matrix.yaml against the schema in section 2."""

def find_uncovered(
    matrix: list[RequirementRecord],
    existing_scenario_ids: set[str],
) -> list[RequirementRecord]:
    """Return every requirement whose covering_test_scenario_ids is empty,
    OR whose listed IDs are all absent from existing_scenario_ids (a
    requirement citing a scenario ID that doesn't actually exist is exactly
    as uncovered as one citing nothing)."""
```

`find_uncovered` must not just check "is the list non-empty" — a
requirement listing a scenario ID that was later deleted or renamed is a
regression this tool must also catch, not a pass.

## 4. `data/matrix.yaml` — population requirement

Populated exhaustively from all five source documents (six counting the
amendment), not a representative sample. This spec seeds a
**non-exhaustive** set of example entries below to fix the granularity and
classification conventions — the implementing session extracts the rest
directly from the source text, following these conventions, and must be
able to justify any entry by pointing at the exact source sentence.

### Seed examples (illustrative, not exhaustive — include these verbatim, then continue in the same style)

```yaml
- requirement_id: playbook.hard_constraint.no_breaking_changes
  source_document: agent-judgment-playbook.md
  source_locator: "Hard Constraints > No breaking changes"
  statement: "An applied edit must not invalidate any cross-reference, listing number, or claim elsewhere in the chapter."
  classification: JUDGMENT
  classification_rationale: "Detecting an invalidated cross-reference requires reading the chapter's other claims, not a schema check."
  covering_test_scenario_ids: []
  notes: null

- requirement_id: playbook.hard_constraint.no_code_listing_changes
  source_document: agent-judgment-playbook.md
  source_locator: "Hard Constraints > No code listing changes"
  statement: "A comment whose only fix requires touching a code block is DO_NOT_APPLY with reason requires_code_change."
  classification: STRUCTURAL
  classification_rationale: "Given a fixture comment tagged as code-only, the output recommendation/reason pair is a fixed expected value — pure equality check."
  covering_test_scenario_ids: []
  notes: null

- requirement_id: playbook.evaluate.seven_dimensions_always_written
  source_document: agent-judgment-playbook.md
  source_locator: "Task: EVALUATE, step 3"
  statement: "Every comment's write-up includes all seven listed fields regardless of the checklist outcome."
  classification: STRUCTURAL
  classification_rationale: "Field presence on every item is a schema check against a fixture batch."
  covering_test_scenario_ids: []
  notes: "See session-2-dependency-contract spec.md Q5 — playbook's own bullet list under this step has 8 entries, not 7, if 'reason' is counted separately from 'recommendation.' Flag, don't silently pick one reading."

- requirement_id: playbook.evaluate.convergence_is_factual_not_a_recommendation
  source_document: agent-judgment-playbook.md
  source_locator: "Task: EVALUATE, step 7"
  statement: "convergence_assessment.comparison_note states scope trend factually and never recommends stopping or continuing."
  classification: JUDGMENT
  classification_rationale: "Whether a sentence 'recommends stopping' vs. 'states a fact' is a reading-comprehension judgment, not a keyword check."
  covering_test_scenario_ids: []
  notes: null

- requirement_id: io_evaluate.output.hard_constraint_rejection_skips_checklist
  source_document: io-contract-evaluate.md
  source_locator: "Output schema > hard_constraint_rejections"
  statement: "An item appearing in hard_constraint_rejections must not also appear in items with a non-DO_NOT_APPLY recommendation."
  classification: STRUCTURAL
  classification_rationale: "Cross-array consistency check against a fixture output — pure logic, no reading required."
  covering_test_scenario_ids: []
  notes: null

- requirement_id: io_evaluate.output.agent_identified_finding_has_corrected_text_field
  source_document: io-contract-evaluate.md (as amended by io-contract-evaluate-ammendum.md)
  source_locator: "Amendment 1 > Change"
  statement: "Every entry in agent_identified_findings includes a minimal_corrected_text field (present, not merely optional-by-omission)."
  classification: STRUCTURAL
  classification_rationale: "Field presence on every array entry is a schema check against a fixture EVALUATE output."
  covering_test_scenario_ids: []
  notes: "Field did not exist pre-Amendment-1; any fixture/test built before this amendment is now stale and must be re-checked, not assumed still valid."

- requirement_id: io_evaluate.output.agent_identified_finding_corrected_text_nullability_matches_recommendation
  source_document: io-contract-evaluate.md (as amended by io-contract-evaluate-ammendum.md)
  source_locator: "Amendment 1 > Change (inline schema comment)"
  statement: "minimal_corrected_text is non-null when recommendation is APPLY / APPLY_SELECTIVELY / APPLY_WITH_CARE, and null otherwise (e.g. for DO_NOT_APPLY-recommended agent-identified findings)."
  classification: STRUCTURAL
  classification_rationale: "A direct conditional check (recommendation value implies non-null/null) against fixture output — no reading comprehension needed."
  covering_test_scenario_ids: []
  notes: "Mirrors the existing supplied_review item rule for minimal_corrected_text (io-contract-evaluate.md, Output schema > items) — worth a cross-reference entry confirming both rules use the same nullability logic, since the amendment's rationale explicitly says this was modeled on that existing field."

- requirement_id: meta.amendment_1_supersedes_base_contract_for_agent_identified_findings
  source_document: io-contract-evaluate-ammendum.md
  source_locator: "Compatibility note"
  statement: "Any code path that constructs or consumes agent_identified_findings for an APPLY-recommended item must handle minimal_corrected_text; DO_NOT_APPLY-recommended findings are unaffected by this amendment."
  classification: STRUCTURAL
  classification_rationale: "A fixture pair (pre-amendment-shaped DO_NOT_APPLY finding vs. amended-shape APPLY finding) settles this without judgment."
  covering_test_scenario_ids: []
  notes: "This entry exists specifically so a future re-scan of io-contract-evaluate.md alone (without checking for amendments) doesn't silently regenerate a matrix missing this field — the exact failure mode Session 2 was built to catch, applied here to this project's own upstream contracts."

- requirement_id: io_apply.output.hard_constraint_self_check_notes_populated_on_failure
  source_document: io-contract-apply.md
  source_locator: "Output schema > hard_constraint_self_check.notes"
  statement: "notes is non-empty whenever any of the four boolean flags is false."
  classification: STRUCTURAL
  classification_rationale: "Direct boolean-implies-string-nonempty check against fixture output."
  covering_test_scenario_ids: []
  notes: null

- requirement_id: orchestrator.pass_cap.fourth_evaluate_refused
  source_document: session-1-orchestrator-spec.md
  source_locator: "Section 5, conditional edges, last bullet"
  statement: "A 4th evaluate_node call is refused once pass_number > max_passes (fixed at 3)."
  classification: STRUCTURAL
  classification_rationale: "Graph-state assertion against a scripted 4-pass scenario — deterministic pass/fail."
  covering_test_scenario_ids: []
  notes: null

- requirement_id: orchestrator.gate.evaluate_gate_always_reached
  source_document: session-1-orchestrator-spec.md
  source_locator: "Section 5, conditional edges, first bullet"
  statement: "evaluate_node always transitions to evaluate_gate_node; no path bypasses this gate for any EVALUATE outcome, regardless of severity."
  classification: STRUCTURAL
  classification_rationale: "Graph-edge assertion — deterministic given any EVALUATE output fixture, including a trivial all-LOW-priority one."
  covering_test_scenario_ids: []
  notes: null

- requirement_id: dependency_contract.defect_category_count_self_referential
  source_document: session-2-dependency-contract/spec.md
  source_locator: "Section 3, defect_category_count row"
  statement: "The checker's expected count is derived from editorial-review-process.md's own number-word claim, not a hardcoded constant, and fails explicitly (not silently) when that claim can't be located."
  classification: STRUCTURAL
  classification_rationale: "Already mechanically verified by Session 2's own test suite; this entry exists so Session 4/traceability knows the coverage already exists upstream and doesn't need re-testing here."
  covering_test_scenario_ids: []
  notes: "Cross-reference only — actual test lives in session-2-dependency-contract/tests/, not duplicated here."
```

## 5. Open questions — flagged back, not silently resolved

- **Q1 (resolved):** `io-contract-evaluate-ammendum.md` content was
  unknown at spec draft time — supplied and incorporated above.
- **Q2:** Session 2's spec.md Q5 ("seven dimensions" vs. 8 listed bullet
  fields) still affects entry count for that EVALUATE step — inherited,
  unresolved.
- **Q3:** Should entries already covered by an *upstream* session's own
  test suite (e.g. the `dependency_contract` example) be marked covered
  by reference, or duplicated into Session 4's suite? Assumed
  reference-only here; flagged for confirmation before Session 4 is
  briefed.
- **Q4 (resolved):** Confirmed via repo-wide search that
  `io-contract-evaluate-ammendum.md` is the only amendment file affecting
  any of this session's five source documents.

## 6. `tests/test_traceability.py` requirements

- Load a real `data/matrix.yaml`, confirm every entry validates against
  the schema in section 2 (required fields present, classification is one
  of the two literal values).
- Construct a fixture matrix with one deliberately-uncovered entry
  (`covering_test_scenario_ids: []`) and one entry citing a scenario ID
  that doesn't exist in a supplied `existing_scenario_ids` set. Assert
  `find_uncovered` returns **both**, not just the empty-list case.
- Construct a fixture where every entry is validly covered; assert
  `find_uncovered` returns `[]`.
- Assert the two amendment-derived seed entries
  (`io_evaluate.output.agent_identified_finding_has_corrected_text_field`
  and
  `io_evaluate.output.agent_identified_finding_corrected_text_nullability_matches_recommendation`)
  are present in the real matrix with classification `STRUCTURAL` —
  proving the amendment was actually incorporated, not silently dropped.

## 7. `README.md` requirements

- How to regenerate/update the matrix when an upstream spec changes
  (which file to re-scan, how to preserve `covering_test_scenario_ids`
  for requirements that didn't change while re-deriving ones that did).
- The amendment-combining convention from section 0: a future amendment
  to any source document supersedes the base entry (don't add a parallel
  entry for the pre-amendment shape) and gets one additional `meta.*`
  entry noting what changed, per the pattern in section 4.
- How to run `find_uncovered` against Session 4's actual scenario ID list
  once that exists, as a CI gate before accepting new test-suite changes.