# Manuscript guidance

## Reader and argument

- Use the project's stated audience for the main narrative.
  Preserve technical rigor through a progression from intuition to detail.
  Do not treat academic tone as a reason for abstract or compressed language.
- Reduce the reader's effort; do not require the reader to infer the intended
  conclusion.
- Write for the actual audience and make necessary context locally available.
- Center the thesis on one clear, reusable idea and tell a direct story:
  problem, importance, gap, proposed idea, evidence, and relation to prior work.
- Start the introduction broadly, narrow progressively to the exact research
  problem, and state the contributions explicitly.
- Prefer a concrete example over generic claims about a problem's importance.
- Make each contribution specific and refutable. Ensure the body supplies
  evidence for every contribution claim.
- Avoid a mechanical “the rest of this thesis is structured as follows” passage
  when narrative forward references can communicate the structure.

## Storyline and concept order

- For a major rewrite, outline the sequence of reader questions before editing
  paragraphs. Each chapter should resolve a question and make the next one
  natural. Avoid reproducing the project's development diary.
- Take the outline down to section level: **opening/transition** picks up the
  previous section's question; **storyline** gives the ideas in simple one-line
  sentences; **ending** states the takeaway and any question the next section
  answers. This is a planning aid, not a requirement to use identical openings
  and closing summaries in the finished prose.
- Carry the central problem through the chapters by showing what each component,
  comparison, and result contributes to it. Motivate the local question without
  repeating the full thesis introduction. A transition should name the actual
  connection, not merely announce the next section number.
- Record where each essential concept is motivated, explained, and used later.
  A glossary supports this plan but cannot replace an explanation in the text.
- Distinguish an early orientation from the detailed explanation. Mentioning
  a system's purpose in the introduction does not require its implementation
  details there.
- Give concepts a primary home. Later sections should apply the concept or add
  a necessary layer, rather than restart the same tutorial. A short reminder
  after a long gap helps; eliminating all repetition would make reading harder.
- Background earns space by explaining the problem, supporting a later choice
  or interpretation, or providing worthwhile historical context. Retain the
  relevant historical context where useful. Specialized names and method
  histories need only the detail that serves that purpose.
- Account for new work with a dated inventory when requested. Group commits by
  research consequence, identify work already covered, and map additions to the
  storyline. Do not give every implementation change a manuscript section.

## Explaining an unfamiliar idea

Use this progression where the reader needs it, without turning every paragraph
into a rigid template:

1. **Need:** what is the reader trying to understand, or what can go wrong?
2. **Example:** give a concrete situation, short timeline, or familiar analogy.
3. **Idea:** explain the relationship in ordinary language.
4. **Name and detail:** introduce the necessary term, mechanism, or equation.
5. **Consequence:** say what the idea lets the thesis decide or test.

For example, in a thesis about a sensor system, explain the observation and
decision first: what is measured, what the system estimates, and why the estimate
matters. Show one real input and output before introducing architecture names.
A concrete ambiguity can motivate a later processing stage. In another field,
choose an equally concrete example that fits the actual research question.

More generally, use a plausible starting approach, a concrete difficulty, and
the response to that difficulty to explain a design choice. Do not invent a
failure to make a preferred solution look necessary. Clearly labelled verbal
or arithmetic examples can teach a mechanism; plots of model behaviour need
recorded outputs.

For timing, a hypothetical estimate might identify an event at 10.0 seconds but
become available only at 10.2 seconds. That example explains why identifying the
event time and making an estimate available are different questions. Introduce
the relevant timestamps and latency metric after the distinction is understood.

Use analogies to explain a relationship, then return to the actual mechanism.
Do not let an analogy silently claim equivalence or experimental evidence.

## Paragraphs and sentences

- Prefer a clear reading pace over minimum word count. Simplify by unpacking
  ideas, not by deleting the explanation that connects them.
- Vary sentence length with the reasoning. A short sentence can emphasise a
  point; a longer one can connect familiar ideas through a cause, consequence,
  or qualification. Avoid chains of isolated short statements as well as long
  sentences packed with new concepts. Joining clauses mechanically fixes neither.
- Give each paragraph one topic. Open by defining its scope, make every sentence
  follow logically, and provide a takeaway or transition when useful. Avoid
  repetitive closing summaries on every paragraph. Develop the idea through
  explanation and examples rather than giving each fact a separate paragraph.
- Order paragraph topics deliberately; outline topics before polishing prose.
- Make connections explicit where the reader needs them: what causes a problem,
  why a choice addresses it, or how a finding changes the next question. Words
  such as “therefore” cannot supply a missing argument.
- Avoid ambiguous reference words such as “this,” “it,” and “that.” Repeat the
  precise noun when ambiguity is possible, especially across paragraphs.
- Cut padding and repeated scaffolding, while keeping words that explain a
  relationship, make an example vivid, or give an unfamiliar reader room to
  understand. Prefer “to” over “in order to” and concrete wording over vague
  intensifiers. Concision should not erase the author's voice.
- Inspect sentences containing several unfamiliar terms, parenthetical
  qualifications, stacked modifiers, or hyphenated compounds. Split the ideas
  and restore their causal relationship, rather than merely shortening clauses.
- Introduce the ordinary description before the specialist name. Use stable,
  short terms afterwards once their scope is established. Repeating qualifiers
  or an internal identifier does
  not add precision when the scope is already clear.
- Explain necessary acronyms at first use, and use them only when they help.
  An expanded acronym can still be incomprehensible without an example.
- Read revised prose aloud to expose missing words and awkward structure.

### Personality, callbacks, and pronouns

- Let personality come from the author's perspective, useful imaginative setups,
  and concrete scenes relevant to the subject. Return from an analogy to the actual
  mechanism. Keep the same approachable voice in technical chapters without
  adding jokes, decorative metaphors, or promotional claims merely to sound lively.
- Reuse an established example when it helps the next explanation. Recall its
  established setting rather than presenting it again as a new idea. A later
  example should reveal a
  new distinction, decision, or consequence, not repeat the original tutorial.
- For a single-author thesis, use the component or method as the actor when
  describing its behaviour, and “this thesis” for its scope. Use “I” for an
  individual choice where helpful, subject to the author's preference. Reserve
  reader-inclusive “we” for shared reasoning; do not
  imply a group of researchers when referring to work by one author.
- Prefer active voice when it identifies who or what acts. Passive voice is
  useful when the procedure or object matters more than the actor; do not impose
  it merely to sound academic or remove every occurrence mechanically.

## Section-specific checks

### Abstract or summary

- Tell the compact story of the problem, the proposed idea, the main finding,
  and its practical meaning. Keep the scope and any decisive limitation clear.
- Use ordinary descriptions before model names or metrics. Include numbers only
  when they clarify the central result; do not compress several comparisons into
  a sentence that a newcomer must decode.
- Develop a connected explanation that makes sense independently of the thesis.
  Avoid an inventory of components, acronyms, and unfinished tasks.

### Introduction

- Motivate the problem, narrow the scope, identify the gap, and state the exact
  contribution and evidence.
- Distinguish product intent from demonstrated results.
- Consider a self-explanatory visual abstract or system overview as Figure 1.
- Lead with the people and problem actually studied. Wider accessibility or
  health benefits can motivate future work but should not displace the evaluated
  application or imply evidence from an unstudied population.
- Keep the summary and introduction especially accessible. Readers should
  understand the research questions without knowing model or protocol names.
- Use terminology that the actual audience can interpret. Explain a specialized
  system role before abbreviating it, and do not imply that every illustrative
  example was evaluated.

### Related work

- Organize paragraphs by methods or ideas, not by papers.
- Define each paragraph's topic, synthesize relevant approaches, and conclude
  how they relate to the thesis method.
- Give prior work fair credit and acknowledge relevant strengths.
- Explain the comparison criteria before a compact table of approaches. Use
  columns that reveal the actual gap, such as setting, assumptions, outputs,
  evaluation protocol, and applicability. Verify entries
  from sources; do not use unchecked ticks to manufacture novelty.
- Define offline, online, causal, and real-time only as needed to understand a
  real distinction. Do not substitute one for another or repeat all four labels
  after their role is clear.

### Method

- Explain the local problem and why the design choice matters before its
  mechanics. Avoid repeating the thesis-wide motivation in every subsection.
- Explain each component's input, output, and role before architecture names,
  equations, settings, or implementation details.
- Keep dataset descriptions with the experimental setup unless a toy example is
  necessary to explain the method.
- Keep enough detail to evaluate the method in the main text. Move routine
  optimizer settings, exhaustive search ranges, byte layouts, and identifiers to
  tables or appendices. Do not move the central method itself out of sight.

### Experiments

- Make every experiment answer one explicit question.
- Present validation experiments before property investigations and comparisons.
- Group each question, setup, result, and interpretation as a coherent unit.
- Use focused tables or figures for the comparisons the reader must make.
- Explain learning, choosing settings, and final testing in plain language before
  introducing training/validation/test partitions and folds. Use “validation”
  consistently; distinguish model selection from checking a working device.
- Start a metric with the failure it detects, then explain its interpretation
  and needed formal definition. Avoid presenting a catalogue of scores.
- Explain why a comparison reference is appropriate and what changes between
  conditions. Before/after labels must identify the actual starting state.
- Interpret the main pattern and its application consequence. Do not narrate
  every table cell. Use plots when differences or error patterns are easier to
  see; use tables for exact values and settings.

### Discussion

- Briefly restore context, interpret the findings, and state limitations.
- Treat failure conditions and limits as research insight.
- Explain whether errors are isolated, consecutive, or associated with observed
  transitions when the evidence permits. Do not infer causes that were not
  measured, or equate better model scores with better user outcomes.

## Technical presentation

- Treat equations as grammatical parts of sentences and explain every symbol.
- Use symbols consistently and remind readers of distant definitions when
  needed.
- Make figures and tables self-contained. Captions must explain what is shown
  and state the conclusion the reader should draw.
- Use actual observations, saved outputs, or project artifacts
  for quantitative example and result plots. Keep provenance with the figure
  source. Distinguish reference values, predictions, and measurements; do not
  invent curves that resemble experimental evidence.
- For conceptual diagrams, establish the reader question and relationships to
  show. Follow the author's requested deliverable and existing visual conventions.
- Label axes, units, legends, and subfigures; keep lines and text legible.
- Keep glossary entries short, alphabetical, visibly separated, and linked to
  the full explanation. It should offer a quick reminder without replacing
  first-use explanations or becoming another dense theory section.
- Sort numeric citations and verify citation placement and support.

## Checking claims against the paper base

- Every sentence making a factual claim beyond original project findings needs
  suitable source support. This includes explanations that seem familiar:
  definitions, generalization, domain characteristics, method
  advantages, and evaluation assumptions. A citation elsewhere in the chapter,
  or a search hit, does not establish that support has been checked.
- Audit claims the task introduces, substantively changes, or puts under review,
  plus unsupported or questioned claims encountered in that work. Check an
  unverified premise when an interpretation or comparison depends on it. A
  requested full claim review covers the whole requested text; a structural
  outline review does not automatically extend to unrelated factual claims.
- Reuse previously checked passages for unchanged claims when the scope and
  relevant source content remain the same. Wording, rhythm, or sentence-boundary
  edits alone do not require another literature search. Recheck support if an
  edit changes the population, task, modality, comparison, causal implication,
  or strength of the claim, or if the relevant source or extraction changes.
- When support has not been established, search the project's configured
  Markdown literature collection.
  Use a clear passage and its context directly for ordinary paraphrases; follow
  [sources.md](sources.md) for targeted PDF checks rather than routinely
  reconfirming every passage in the PDF.
- Read the candidate paper's relevant passage and check the population, task,
  modality, comparison, and strength of evidence. A model study does not
  establish human behaviour; an analogy does not establish an equivalence.
  Where useful, retain a brief note of the claim, paper or citation key, relevant
  passage, and any PDF check or extraction defect. Reuse existing evidence notes;
  do not create an elaborate per-sentence registry for a small edit.
- Place citations beside the claims they support. One citation may cover a
  clearly bounded group of related sentences; do not repeat it mechanically
  after every sentence or attach unrelated references to increase citation count.
- Keep original results tied to their figures, tables, or project artifacts.
  Implementation descriptions need project evidence; goals, proposed methods,
  and labelled invented examples must not acquire spurious literature support.
  Check external premises within those sentences separately.
- If the local collection lacks direct support, narrow or remove the claim,
  identify it as a proposal or inference when that is what it is, or record the
  evidence gap. When necessary, consult a primary publication or official
  technical documentation and disclose that it came from outside the collection.
  Do not cite a paper solely because its subject sounds relevant.

## Final reading pass

- Can a newcomer say why this section exists after its opening?
- Does each necessary term have an explanation before its first substantive use?
- Can the reader follow an example without already understanding the theory?
- Does each paragraph add one manageable step rather than several compressed ones?
- Does the prose flow through connected reasoning, with varied sentence rhythm?
- Do callbacks develop earlier examples rather than reintroduce them?
- Can the reader connect each technical choice and result to the central problem?
- Do figures explain inputs, outputs, and relationships as well as display names?
- Does each result explain what changed, why it matters, and the evidence limit?
- Can background be shortened without removing context the reader needs or enjoys?

Readability scores may flag difficult passages, but they cannot replace this
comprehension check. Do not flatten necessary technical meaning to meet an
arbitrary sentence length or grade-level score.

Adapted from the maintainer's writing workflow and its general lessons from
Jan van Gemert's writing guidance and Simon Peyton Jones's *How to write a great
research paper*. See [sources.md](sources.md) for provenance and the distinction
between writing feedback and research evidence. Project-specific audience,
terminology, and feedback must come from the current project's own sources.
