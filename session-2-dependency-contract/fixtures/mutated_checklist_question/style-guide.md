# Style Guide — Modern Java eBook

## Voice and Tone
- Formal but approachable
- Expert colleague explaining clearly to a peer
- Never condescending, never overly casual
- Consistent throughout all chapters

## Grammar Rules
- Active voice: "Java introduced records" not "Records were introduced"
- Oxford comma required: "records, sealed classes, and pattern matching"
- No first person ("I", "we") in body text
- Sentences starting with "However," not "But,"
- Sentences starting with "Therefore," not "So,"

## Prohibited Phrases
These apply to manuscript prose. This style guide, the tone reference, and KPI
files are exempt — they are instructions about the writing, not the writing
itself.
- basically, simply, just, easy, easily
- obviously, of course, needless to say
- as you can see, as mentioned above
- it is worth noting, it should be noted

## Technical Rules
- Define every term before first use — including plain-English concept names,
  not only Java syntax. A term with no equivalent in other mainstream
  languages (for example, checked exception) needs its distinction explained
  in prose before it is used as if already understood, even in an
  introduction.
- Acronyms spelled out on first use: "JVM (Java Virtual Machine)"
- Always cite Java version: "Java 21+" never "recent Java" or "newer Java"
- "modern Java" lowercase in body text
- API/class names in backticks: `Records`, `CompletableFuture`

## Structure Rules
- Every chapter opens with an introductory paragraph — no heading first
- Opening paragraphs must stand alone: generic, no forward continuation
  language ("picking up where we left off") and no chapter numbers
- Abstract problem stated before the domain example that illustrates it
- Every chapter's introduction ends with a short prose roadmap previewing
  the arc the chapter climbs — no bulleted or numbered list, no stated count
  ("six topics," "three forms"); the roadmap is prose, and its structure
  (acknowledgment → verification → survival across a boundary, for example)
  carries the organization instead of a list
- Whether the introduction holds literal syntax back for a paragraph or two
  is a per-chapter judgment call, not a fixed rule — both are valid models,
  and either way the abstract problem is still named in prose before any
  listing appears (see the rule above). A chapter introducing an unfamiliar
  or Java-specific concept (a checked exception has no equivalent in most
  other languages) benefits from grounding the reader in plain prose for
  longer, holding backticked syntax until the first table or listing formally
  introduces it. A chapter whose opening problem is well-known and mostly
  needs to be seen (a fragile base class silently discarding an invariant)
  can move from the prose statement of the problem into that listing sooner.
  Either way, plain-English concept names ("exception," "null," "Optional")
  are never treated as syntax to withhold — only backticked class/method
  names and code blocks are what a longer plain-English opening defers.
  Replacing a plain concept word with vaguer paraphrase (e.g. "hands back an
  empty result instead of saying so") makes prose harder to follow, not more
  approachable, regardless of which opening pace a chapter uses.
- Every chapter ends with ## Summary section
- The Summary looks forward (to what the next chapter builds on), not
  backward as a restatement of this chapter's content
- Every H2 section has a transition sentence leading to the next — except the
  final content section, whose transition leads into the Summary, and the
  Summary itself, which closes the chapter rather than handing off to another
  section within it
- Maximum sentence length: 35 words
- Paragraph length: 3 to 6 sentences — with one deliberate exception. A
  slowing-down paragraph (see Teaching Rhythm) is meant to be shorter, two or
  three short sentences, and must not be padded to reach this floor. The
  short length is the point.
- Every major section needs a "When NOT to use" note where applicable

## Cross-Chapter References
- In manuscript prose, never say "chapter" or reference chapter numbers — no
  "In Chapter 3," no "this chapter covers," no "the next chapter extends this
  to..." (This rule governs the book's prose only. Planning documents — this
  style guide, the tone reference, and KPI files — may cite chapter numbers
  freely, since their whole job is to reason about the book's structure.)
- Concepts introduced earlier are reused silently in manuscript prose, without
  a citation back to where they were taught
- Chapter numbers and cross-references stay confined to planning documents,
  never appearing in manuscript prose

## Prose Discipline
- No enumerated counts in prose ("five features," "three forms," "across six
  questions") — let structure (headings, listings, tables) carry
  organization instead of narrating a count
- No catalog-style sections that exist only to list every option
  exhaustively; a section teaches a decision, not a checklist
- Within a single sentence or paragraph, do not stack a second example or
  illustration onto a claim that has already landed — and do not use that
  second illustration to reach forward to a term the chapter has not yet
  introduced. One clean claim per landing point; let the next paragraph
  carry the next idea.
- Narrative voice — pain before abstraction: every section opens with a
  concrete, recognizable scenario (a swallowed exception, a distant
  NullPointerException, a declined refund treated as a system failure)
  before naming the abstract concept or mechanism that addresses it.
  Abstract nouns and thesis-level framing belong in headings and in KPI
  planning documents — never as the first sentence of a section's prose.

## Declarative Style as a Silent Discipline
- Expressing intent through declarative style — favoring exhaustive
  `switch`, `Optional` chaining, and sealed result types that state what
  should happen over imperative constructs that narrate the checks needed
  to get there — is a writing discipline the author checks against every
  listing, not reader-facing content.
- This point must never become its own section, heading, or callout. It
  shows up only as consistently tight, self-explanatory code — never as a
  taught topic with a name.
- The same economy applies to method signatures: a signature should carry
  exactly the failure modes or absence semantics that genuinely exist, no
  wider and no narrower — checked exceptions, `Optional<T>`, and sealed
  result types turn a signature into documentation by the same discipline
  that lets `var` retire a type the compiler already inferred (Chapter 1's
  founding idea, applied one level up).

## Teaching Rhythm — The Slowing-Down Paragraph
- After a mechanism has been built up across several sentences or a
  listing, the prose periodically pauses and restates its real point in two
  or three short, plain sentences, stripped of the machinery that just
  explained it. This is not new content — it is the same idea, said again,
  closer to the bone, giving the reader room to absorb it before the next
  mechanism arrives.
- Frequency: roughly once every two or three sections. Never so often that
  it becomes a recognizable tic, never absent so long that the prose turns
  into an unbroken wall of mechanism.
- Do not use one repeated sentence template. Rotate among distinct
  structures so the pattern is felt as a rhythm, not recognized as a
  formula:
  - **Negation, then restatement:** "X was never the real point. What
    matters is Y."
  - **Dismissal, then redirect:** "The wrapper itself is not the point.
    What changed is..."
  - **Inversion, delayed verb:** "Declaring three subclasses is not the
    achievement. Turning three into a fact the compiler checks — that is."
  - **Comparison, no negation:** "Whether a construct compiles matters far
    less than what it is honest about."
- No two consecutive instances in the same chapter may share a structure.
- Ground the paragraph in the specific listing or example just shown rather
  than restating the idea in the abstract — the strongest instances name the
  actual types or values from the code immediately above them.
- When a section's closing transition sentence can absorb this rhythm, fold
  it in rather than adding a new, separate paragraph immediately after
  another short one — stacking two short paragraphs back to back reads as
  padding, not rhythm.

## Formatting
- Code blocks always specify language: ```java not just ```
- Code lines maximum 80 characters
- 4-space indentation in all code — never tabs
- Every code block has a caption above it
- Every code block has a GitHub link below it — plain text link only, no
  emoji
- Listings capped at 18 lines; a listing that requires more content is a
  signal to split it, not to extend the ceiling. This 18-line limit is the
  manuscript-wide authority — any KPI file stating a different number (some
  currently say 20) is out of date and must be read as 18.
