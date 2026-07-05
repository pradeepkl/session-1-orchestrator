"""Mechanical dependency checks for the six governing editorial documents."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

DOC_FILENAMES = (
    "editorial-review-process.md",
    "editorial-review-process-addendum-go-no-go.md",
    "style-guide.md",
    "tone-reference.md",
    "narrative-voice-directive.md",
    "agent-judgment-playbook.md",
)

_NUMBER_WORDS: dict[str, int] = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "thirteen": 13,
    "fourteen": 14,
    "fifteen": 15,
    "sixteen": 16,
    "seventeen": 17,
    "eighteen": 18,
    "nineteen": 19,
    "twenty": 20,
}


@dataclass(frozen=True)
class CheckResult:
    assumption_id: str
    passed: bool
    expected: object
    found: object
    detail: str


def number_word_to_int(word: str) -> int | None:
    """Convert a lowercase English number word (one..twenty) to an integer."""
    return _NUMBER_WORDS.get(word.lower())


def _extract_section(text: str, heading: str) -> str:
    pattern = re.compile(rf"^## {re.escape(heading)}\s*$", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^## ", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end]


def _first_number_word_in(text: str, *context_terms: str) -> int | None:
    """Return the first number word appearing near any of the context terms."""
    lowered = text.lower()
    for term in context_terms:
        for match in re.finditer(re.escape(term.lower()), lowered):
            window = lowered[max(0, match.start() - 80) : match.end() + 80]
            for word, value in _NUMBER_WORDS.items():
                if re.search(rf"\b{word}\b", window):
                    return value
    return None


def _normalize_scale_token(token: str) -> str:
    normalized = token.upper().replace("_", " ")
    return re.sub(r"\s+", " ", normalized).strip()


def _collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _capture_recommendation_scale_blocks(text: str) -> list[str]:
    """Collect multi-line recommendation-scale fragments before slash splitting."""
    blocks: list[str] = []
    capture = False
    current: list[str] = []
    paren_depth = 0

    for line in text.splitlines():
        lower = line.lower()
        if not capture and "recommendation" in lower and "/" in line:
            capture = True
            current = [line]
            paren_depth = line.count("(") - line.count(")")
            if paren_depth <= 0 and not line.rstrip().endswith("/"):
                blocks.append(_collapse_whitespace("\n".join(current)))
                capture = False
                current = []
            continue
        if capture:
            current.append(line)
            paren_depth += line.count("(") - line.count(")")
            if paren_depth <= 0 and not line.rstrip().endswith("/"):
                blocks.append(_collapse_whitespace("\n".join(current)))
                capture = False
                current = []
            continue
        capture = False
    return blocks


def _slash_scale_region(collapsed: str) -> str:
    paren = re.search(r"\(([^)]*/[^)]*)\)", collapsed)
    if paren:
        return paren.group(1)
    if "—" in collapsed:
        collapsed = collapsed.split("—", 1)[1]
    elif "`recommendation`" in collapsed.lower():
        collapsed = re.sub(r"^.*`recommendation`\s*:\s*", "", collapsed, flags=re.I)
    collapsed = re.sub(r"\s*\(with reason\)\s*$", "", collapsed, flags=re.I)
    return collapsed.strip(" )")


def _extract_recommendation_scales(text: str) -> list[str]:
    tokens: list[str] = []
    for block in _capture_recommendation_scale_blocks(text):
        region = _slash_scale_region(block)
        if "/" not in region:
            continue
        for part in region.split("/"):
            token = _normalize_scale_token(part)
            if token:
                tokens.append(token)
    return tokens


def _scales_compatible(canonical: str, other: str) -> bool:
    left = _normalize_scale_token(canonical)
    right = _normalize_scale_token(other)
    if left == right:
        return True
    if left.startswith(right) or right.startswith(left):
        return True
    if "RESOLVED AS SIDE EFFECT" in left and "RESOLVED AS SIDE EFFECT" in right:
        return True
    return False


def defect_category_count(docs: dict[str, str]) -> CheckResult:
    """Checks editorial-review-process.md: recurring defect category count matches prose."""
    process = docs["editorial-review-process.md"]
    section = _extract_section(process, "Recurring Defect Categories (check every chapter for these)")
    found = len(re.findall(r"^### \d+\.", section, re.MULTILINE))
    expected = _first_number_word_in(process, "recurring defect categor")
    if expected is None:
        return CheckResult(
            "defect_category_count",
            False,
            None,
            found,
            "could not find a stated category count near 'recurring defect categor' "
            "in editorial-review-process.md — cannot verify defect_category_count",
        )
    passed = expected == found
    detail = (
        f"editorial-review-process.md declares {expected} recurring defect categories "
        f"and lists {found} numbered ### headings in the defect section."
    )
    return CheckResult("defect_category_count", passed, expected, found, detail)


def checklist_question_count(docs: dict[str, str]) -> CheckResult:
    """Checks addendum question count against the playbook's stated checklist size."""
    addendum = docs["editorial-review-process-addendum-go-no-go.md"]
    playbook = docs["agent-judgment-playbook.md"]
    questions_section = _extract_section(addendum, "The seven questions")
    found = len(re.findall(r"^\d+\.\s+\*\*", questions_section, re.MULTILINE))
    expected = _first_number_word_in(playbook, "seven-question checklist", "seven question checklist")
    if expected is None:
        return CheckResult(
            "checklist_question_count",
            False,
            None,
            found,
            "could not find a stated question count near 'seven-question checklist' "
            "in agent-judgment-playbook.md — cannot verify checklist_question_count",
        )
    passed = expected == found
    detail = (
        f"agent-judgment-playbook.md declares {expected} checklist questions and "
        f"editorial-review-process-addendum-go-no-go.md lists {found} numbered questions."
    )
    return CheckResult("checklist_question_count", passed, expected, found, detail)


def evaluate_dimension_count(docs: dict[str, str]) -> CheckResult:
    """Checks editorial-review-process.md Phase 1 and agent-judgment-playbook.md dimension count."""
    process = docs["editorial-review-process.md"]
    playbook = docs["agent-judgment-playbook.md"]
    assess_match = re.search(
        r"For each review item, assess:\s*\n(.*?)\n\nClose the evaluation",
        process,
        re.DOTALL,
    )
    assess_block = assess_match.group(1) if assess_match else ""
    found = len(re.findall(r"^\d+\. \*\*", assess_block, re.MULTILINE))
    expected = _first_number_word_in(playbook, "seven dimensions", "all seven dimensions")
    if expected is None:
        return CheckResult(
            "evaluate_dimension_count",
            False,
            None,
            found,
            "could not find a stated dimension count near 'seven dimensions' "
            "in agent-judgment-playbook.md — cannot verify evaluate_dimension_count",
        )
    passed = expected == found
    detail = (
        f"agent-judgment-playbook.md declares {expected} EVALUATE write-up dimensions and "
        f"editorial-review-process.md Phase 1 lists {found} assessed dimensions."
    )
    return CheckResult("evaluate_dimension_count", passed, expected, found, detail)


_HARD_CONSTRAINT_EXPECTED = 5


def hard_constraint_count(docs: dict[str, str]) -> CheckResult:
    """Checks agent-judgment-playbook.md: Hard Constraints bold-labeled bullet count."""
    playbook = docs["agent-judgment-playbook.md"]
    section_match = re.search(
        r"^## Hard Constraints.*?\n(.*?)(?:\n---|\n## )",
        playbook,
        re.MULTILINE | re.DOTALL,
    )
    section = section_match.group(1) if section_match else ""
    found = len(re.findall(r"^- \*\*[^*]+\*\*", section, re.MULTILINE))
    expected = _HARD_CONSTRAINT_EXPECTED
    passed = expected == found
    detail = (
        f"agent-judgment-playbook.md Hard Constraints section should list {expected} "
        f"bold-labeled bullets (`- **...**`) and currently lists {found}."
    )
    return CheckResult("hard_constraint_count", passed, expected, found, detail)


_PROTECTED_CALLOUT_CHECKS = (
    {
        "id": "opening_scenario_in_process",
        "doc": "editorial-review-process.md",
        "section": "What NOT to Touch by Default",
        "keywords": ("opening", "scenario"),
    },
    {
        "id": "when_not_to_use_in_style_guide",
        "doc": "style-guide.md",
        "section": None,
        "keywords": ("when not to use",),
    },
    {
        "id": "summary_recap_in_process",
        "doc": "editorial-review-process.md",
        "section": "What NOT to Touch by Default",
        "keywords": ("summary", "recap"),
    },
)


def _protected_callout_search_text(docs: dict[str, str], doc: str, section: str | None) -> str:
    text = docs[doc]
    if section:
        return _extract_section(text, section)
    return text


def protected_callout_names_present(docs: dict[str, str]) -> CheckResult:
    """Checks protected-callout keyword presence across editorial-review-process.md and style-guide.md.

    Three independent checks (per spec.md), each requiring every listed keyword to appear
    as a case-insensitive substring in the named document/section — not an exact phrase
    match against the full expected string. For example, the keywords ``("summary", "recap")``
    pass when those words appear anywhere in the protected list, even if separated by
    other words (e.g. "The Summary's core recap paragraph").
    """
    expected: dict[str, list[str]] = {}
    found: dict[str, list[str]] = {}
    missing: list[str] = []

    for check in _PROTECTED_CALLOUT_CHECKS:
        check_id = check["id"]
        keywords = check["keywords"]
        haystack = _protected_callout_search_text(docs, check["doc"], check["section"])
        expected[check_id] = list(keywords)
        present = [kw for kw in keywords if kw.lower() in haystack.lower()]
        found[check_id] = present
        for kw in keywords:
            if kw.lower() not in haystack.lower():
                missing.append(f"{check_id}: {kw!r}")

    passed = not missing
    detail = (
        "Each check tests case-insensitive substring presence of individual keywords "
        "(not exact phrase match). "
        f"Missing: {missing or 'none'}."
    )
    return CheckResult("protected_callout_names_present", passed, expected, found, detail)


def recommendation_scale_consistency(docs: dict[str, str]) -> CheckResult:
    """Checks recommendation scale labels across editorial-review-process.md, addendum, and playbook."""
    process = docs["editorial-review-process.md"]
    addendum = docs["editorial-review-process-addendum-go-no-go.md"]
    playbook = docs["agent-judgment-playbook.md"]

    canonical_tokens = _extract_recommendation_scales(process)
    if not canonical_tokens:
        canonical_tokens = [
            "APPLY",
            "APPLY SELECTIVELY",
            "APPLY WITH CARE",
            "RESOLVED AS SIDE EFFECT OF ANOTHER ITEM",
            "DO NOT APPLY",
        ]
    canonical_normalized = {_normalize_scale_token(t) for t in canonical_tokens}

    mismatches: list[str] = []
    found_by_doc: dict[str, list[str]] = {}
    for doc_name, text in (
        ("editorial-review-process-addendum-go-no-go.md", addendum),
        ("agent-judgment-playbook.md", playbook),
    ):
        doc_tokens = _extract_recommendation_scales(text)
        found_by_doc[doc_name] = doc_tokens
        if len(doc_tokens) < len(canonical_normalized):
            mismatches.append(
                f"{doc_name}: expected {len(canonical_normalized)} scale tokens, "
                f"parsed {len(doc_tokens)} ({doc_tokens!r})"
            )
        for token in doc_tokens:
            if not any(_scales_compatible(canonical, token) for canonical in canonical_tokens):
                mismatches.append(f"{doc_name}: {token!r}")

    passed = not mismatches
    expected = sorted(canonical_normalized)
    detail = (
        "Recommendation scale tokens in the addendum and playbook normalize to the "
        f"editorial-review-process.md scale; mismatches: {mismatches or 'none'}."
    )
    return CheckResult(
        "recommendation_scale_consistency",
        passed,
        expected,
        found_by_doc,
        detail,
    )


def closing_bridge_convention_defined(docs: dict[str, str]) -> CheckResult:
    """Checks editorial-review-process.md defines the Closing-Bridge Convention section."""
    process = docs["editorial-review-process.md"]
    section = _extract_section(process, "The Closing-Bridge Convention")
    required_markers = (
        "forward-pointing bridge",
        "never a chapter number",
        "Pattern:",
    )
    missing = [marker for marker in required_markers if marker.lower() not in section.lower()]
    passed = bool(section.strip()) and not missing
    expected = list(required_markers)
    found = [marker for marker in required_markers if marker.lower() in section.lower()]
    detail = (
        "editorial-review-process.md must include 'The Closing-Bridge Convention' with "
        f"required markers; missing: {missing or 'none'}."
    )
    return CheckResult("closing_bridge_convention_defined", passed, expected, found, detail)


_ALL_CHECKERS = (
    defect_category_count,
    checklist_question_count,
    evaluate_dimension_count,
    hard_constraint_count,
    protected_callout_names_present,
    recommendation_scale_consistency,
    closing_bridge_convention_defined,
)


def check_all(docs: dict[str, str]) -> list[CheckResult]:
    """Run every mechanical checker and return the full result list (no short-circuit)."""
    return [checker(docs) for checker in _ALL_CHECKERS]


def check_all_from_dir(path: str | Path) -> list[CheckResult]:
    """Load the six governing documents from a directory and run check_all."""
    base = Path(path)
    docs = {name: (base / name).read_text(encoding="utf-8") for name in DOC_FILENAMES}
    return check_all(docs)
