```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REVISE: the paper has a strong scientific spine, but inconsistent completion tense, insider vocabulary, duplicated background, and the absence of a discussion section keep it from reading as one advisor-facing paper.",
  "workspace": {
    "base_requested": "impl/paper-mvp-complete",
    "base_mode": "exact",
    "head_start": "5e472e8f9c1e59d50ac55f820a61e5e6dd99ee9e",
    "head_end": "5e472e8f9c1e59d50ac55f820a61e5e6dd99ee9e",
    "upstream_end": "5e472e8f9c1e59d50ac55f820a61e5e6dd99ee9e",
    "branch": "impl/paper-mvp-complete"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "REVISE",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "file": "docs/paper/draft-v1.md",
        "line": "5, 22-24, 147-156, 180, 244",
        "title": "The paper alternates between completed-result and pre-results voices",
        "fix": "Put a results-pending note outside the abstract, use future or planned tense for uncollected characterization and demonstration work, and restore completed-result and open-artifact claims only when the values and release locators exist."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "file": "docs/paper/draft-v1.md",
        "line": 5,
        "title": "The abstract has the right order but hides the central physical result under jargon",
        "fix": "Rewrite as problem, plain-language method, physical finding, scope, and demonstration: define the floor as the smallest trustworthy difference, explain approximately 30 ms times 33 W as about 1 J that repetitions cannot remove, and move the draft placeholder outside the abstract."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "file": "docs/paper/draft-v1.md",
        "line": "17-24, 68-86, 109-111, 123-143, 168-180, 230-244",
        "title": "Repository and protocol shorthand repeatedly replaces reader-facing explanation",
        "fix": "Remove contribution IDs C-i through C-vi and internal terms such as LABELLED path, floor_source, mint, run root, exact basis, occurrence, and claim-licensing; define measurement session/window, run/member, bundle, and cell before first use, then use those terms consistently."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "file": "docs/paper/draft-v1.md",
        "line": "26-40, 200-220",
        "title": "Background and related work repeat the same literature and argumentative work",
        "fix": "Make Section 2 conceptual background about energy integration, software counters, and phase-boundary error; reserve paper-by-paper comparisons and the novelty claim for Section 8, or merge the sections and spend the saved space on results and interpretation."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "file": "docs/paper/draft-v1.md",
        "line": "198, 228-248",
        "title": "Limitations plus the conclusion do not substitute for a discussion section",
        "fix": "Add a concise Discussion after the results that interprets why attribution rather than scatter dominates, why refusal is scientifically useful, how prompt length changes the question being estimated, and what parts of the method may transfer. Keep Section 9 for threats and scope limits."
      },
      {
        "id": "F6",
        "severity": "should_fix",
        "file": "docs/paper/draft-v1.md",
        "line": "170-176",
        "title": "The sizing subsection is valuable but is in the wrong form and partly in the wrong section",
        "fix": "Move the general prospective-sizing rule to Section 5 pre-registration. In Section 7 retain only the application and state the one design actually frozen, with its prompt length and target margin; do not leave two live alternatives under a Pre-registered design heading."
      },
      {
        "id": "F7",
        "severity": "should_fix",
        "file": "docs/paper/draft-v1.md",
        "line": "182-196",
        "title": "The result tables are close, but the contrast table does not expose the decisive quantity",
        "fix": "Keep the phase-by-model table, define the interval type and sample unit, and put the common stack identity in its caption rather than claiming every row carries it. In the contrast table show estimate, claim-side bound or interval endpoint, floor, effective threshold, signed clearance margin, and verdict; a ratio alone can hide which endpoint controls the decision."
      },
      {
        "id": "F8",
        "severity": "should_fix",
        "file": "docs/paper/draft-v1.md",
        "line": "68-80, 115-119",
        "title": "The equations introduce notation without fully defining it in words",
        "fix": "Define the A/B/B/A block difference and its sign before introducing delta, identify the Student-t critical value and every subscript, and state that F_cell and B_claim are energy magnitudes in joules before presenting their sum."
      },
      {
        "id": "F9",
        "severity": "should_fix",
        "file": "docs/paper/draft-v1.md",
        "line": "1, 230",
        "title": "The title and one limitation sentence imply broader hardware scope than the evidence supports",
        "fix": "Prefer a title such as JouleWise: Attribution-Limited Detection Floors for Phase-Resolved LLM Energy on Apple Silicon, and change what this instrument class can support to what this implementation on this stack can support."
      },
      {
        "id": "F10",
        "severity": "should_fix",
        "file": "docs/paper/draft-v1.md",
        "line": "30-38, 204-224, 248",
        "title": "Citation keys have no references section",
        "fix": "Add complete bibliographic entries and replace internal citation keys with the required citation style before advisor circulation; the present Markdown file ends without enough information to identify or check its sources."
      },
      {
        "id": "F11",
        "severity": "nit",
        "file": "docs/paper/draft-v1.md",
        "line": "22-24, 109, 182, 208, 248",
        "title": "Copyediting and planning-note batch",
        "fix": "Change drift/settle to drift and settling; remove the optional quantization-ladder planning bracket unless it is frozen; standardize labeled versus labelled; change Per stack to On the studied stack; repair the missing subject in the unlike boundaries sentence; and split the 208-word conclusion paragraph."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD; git rev-parse @{upstream}; wc -l docs/paper/draft-v1.md; awk 'BEGIN{pending=0; refs=0; sections=0} /^## /{sections++} {pending += gsub(/\\[[^]]*PENDING[^]]*\\]/,\"&\"); if($0 ~ /^## References/) refs++} END{print \"SECTIONS\",sections; print \"PENDING_MARKERS\",pending; print \"REFERENCE_SECTIONS\",refs}' docs/paper/draft-v1.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "5e472e8f9c1e59d50ac55f820a61e5e6dd99ee9e",
          "     248 docs/paper/draft-v1.md",
          "SECTIONS 12",
          "PENDING_MARKERS 34",
          "REFERENCE_SECTIONS 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "248 docs/paper/draft-v1.md\\nSECTIONS 12\\nPENDING_MARKERS 34\\nREFERENCE_SECTIONS 0"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The literature claims and citation accuracy were not independently source-verified under this plain-language and coherence lens.",
      "needs": "Run a bibliography and novelty-claim audit before submission."
    },
    {
      "id": "G2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Final result-to-method balance and page-level conference proportion cannot be judged until the pending values, figures, references, and typeset format exist.",
      "needs": "Repeat the coherence pass on the populated, rendered manuscript."
    }
  ]
}
```

## Findings

### F1 — Should-fix: inconsistent evidentiary tense

`docs/paper/draft-v1.md:5`, `:22-24`, `:147-156`, `:180`, `:244`

The manuscript says “we demonstrate,” claims “full instrument characterization,” describes what the open repository contains, and promises reader re-reduction while all characterization rows and demonstration values remain pending. That makes the new sections feel attached to a finished older paper rather than integrated into one honest draft.

The placeholders are acceptable internal drafting markers. The abstract placeholder is intrusive for advisor-facing circulation. Put a single “results pending” note above the abstract, then keep incomplete work in future tense until the artifacts exist.

### F2 — Should-fix: abstract needs a plainer physical result

`docs/paper/draft-v1.md:5`

The abstract has the correct large-scale order—problem, method, finding, demonstration, scope—but the method sentence asks a non-specialist to absorb “measurement window,” “bracketed pulse-train,” “detection floor,” “fail-closed,” “claim-side measurement bound,” “stack,” and “hash-bound evidence chain” at once.

The attribution-limited result is important, but its physical significance would land better as: a boundary uncertainty of roughly 30 ms during a roughly 33 W power change can move about 1 J into the wrong phase, and repeating the workload does not remove that systematic ambiguity. Define the detection floor immediately as the smallest difference the method can trust.

### F3 — Should-fix: project-internal language leaks throughout

`docs/paper/draft-v1.md:17-24`, `:68-86`, `:109-111`, `:123-143`, `:168-180`, `:230-244`

The main leaks are:

- `C-i` through `C-vi`
- “LABELLED path” and the literal `floor_source` field
- “mint,” “re-mint,” “active runs root,” “exact resulting basis,” “occurrence,” and “claim-licensing”
- “bundle” in the equations before a bundle is explained at line 137
- “custody chain” where “tamper-evident evidence record” would be clearer

“Member” is eventually defined well at line 56, and “cell” is defined at line 64. Apply that same discipline to the other recurring nouns. Keep schema fields and policy labels in an artifact appendix or implementation documentation.

### F4 — Should-fix: Sections 2 and 8 duplicate each other

`docs/paper/draft-v1.md:26-40`, `:200-220`

Both sections walk through MLPerf, software-counter validation, LLM energy studies, and minimum-detectable-effect methods. This is the clearest whole-paper flow problem outside the placeholders.

Keep Section 2 as conceptual background: energy as integrated power, why software counters are appealing, and why phase boundaries create a distinct measurement problem. Let Section 8 perform the literature comparison and novelty argument. This also recovers space for results and discussion without making the paper longer.

### F5 — Should-fix: add a real Discussion section

`docs/paper/draft-v1.md:198`, `:228-248`

Section 9 lists limitations effectively, but limitations are not the place for the paper’s positive interpretation. The conclusion currently has to compress the scientific meaning, methodological contribution, transfer boundary, and future work into one dense paragraph.

Add a short Discussion after Section 7. It should explain:

- why attribution exceeding scatter changes experimental practice;
- why a refused comparison is informative rather than a failed experiment;
- why lengthening the prompt improves resolvability but changes the scientific question;
- which lessons may transfer to other software counters, without transferring the measured numerical floor.

That section would make the new ending match the explanatory voice of Sections 3–6.

### F6 — Should-fix: retain sizing, but relocate and resolve it

`docs/paper/draft-v1.md:170-176`

The sizing episode earns its place because it shows the floor changing the experiment before data collection. That is one of the paper’s strongest practical consequences.

Its general rule belongs in Section 5 under pre-registration. Section 7 should then state the one design actually frozen and the concrete rationale. Presenting two possible designs under “Pre-registered design” weakens the claim that design freedom was already closed. The forward reference to Section 8’s literature “lineage” also interrupts the methods-to-results flow.

### F7 — Should-fix: expose the actual decision in the result tables

`docs/paper/draft-v1.md:182-196`

The phase-by-model table is the right basic shape. Give it a caption naming the single stack and define the interval and `n`; do not claim that the narrow row format carries the entire identity list from Section 6.

The contrast table needs the quantity that makes the refusal auditable. Show the effect estimate, its claim-side bound or controlling interval endpoint, the applicable floor, the combined threshold, a signed clearance margin, and the verdict. “Effect-to-bar ratio” may be a useful companion, but it does not show whether the uncertainty interval itself cleared the bar.

### F8 — Should-fix: complete the notation definitions

`docs/paper/draft-v1.md:68-80`, `:115-119`

The prose defines several symbols, but it never states the sign convention or formula for the A/B/B/A block difference, and the Student-*t* critical value appears without explanation. Define each in words immediately before the equations. Likewise, state that \(F_{\mathrm{cell}}\) and \(B_{\mathrm{claim}}\) are energy magnitudes in joules. This is a small edit with a large metrology-readability payoff.

### F9 — Should-fix: narrow and sharpen the title

`docs/paper/draft-v1.md:1`, `:230`

The current title points in the right direction, but “consumer silicon” suggests a broader hardware study than one Apple-silicon unit and stack. The actual center is phase-boundary attribution, its detection floor, and principled refusal.

A closer title would be:

> JouleWise: Attribution-Limited Detection Floors for Phase-Resolved LLM Energy on Apple Silicon

Also replace “what this instrument class can support” at line 230 with “what this implementation on this stack can support.”

### F10 — Should-fix: add the bibliography

`docs/paper/draft-v1.md:30-38`, `:204-224`, `:248`

The document contains many internal citation keys but no References section. Even for a draft, an advisor cannot efficiently check the novelty argument or identify several works from the keys alone. Add complete bibliographic entries and the intended citation format before professor-facing circulation.

### F11 — Nit batch

- `docs/paper/draft-v1.md:22`: use “drift and settling,” not “drift/settle.”
- `docs/paper/draft-v1.md:23` and `:198`: remove the optional quantization-ladder planning language unless that experiment is frozen.
- `docs/paper/draft-v1.md:109`: standardize on “labeled” to match the paper’s otherwise American spelling.
- `docs/paper/draft-v1.md:182`: change “Per stack” to “On the studied stack.”
- `docs/paper/draft-v1.md:208`: repair “Such studies answer valuable systems questions, but unlike boundaries and software stacks…”; the comparison is grammatically incomplete.
- `docs/paper/draft-v1.md:248`: split the 208-word conclusion into a result/contribution paragraph and a scope/future-work paragraph.

## Residual risk

This review did not independently verify the cited literature, novelty claims, or attribution of particular methods to particular papers. Final section proportion also needs another pass after the result tables, figures, bibliography, and conference formatting are populated.