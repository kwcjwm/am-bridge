---
name: am-page-modernization
description: AI-first PL workflow for page-based AM modernization. Use when the PM gives a legacy page such as `aaa.xml` and wants the internal AI to analyze the page, write the Korean main report, create the shell/mockup, and use optional deterministic support only when exhaustive detail is needed.
---

# AM Page Modernization

Use this skill when acting as the working PL for AM tasks.
The human user is the PM.
You are the main analyst, report writer, and shell/mockup author.

## Core Rule

- start from screenshots, running-screen captures, XML, and source
- require the matching main page image using `<page>.xml` -> `<page>.jpg` as the default rule
- if the matching main image is missing, ask the PM/operator to provide it before treating the shell as reviewable
- if `prompts/amprompt.md` exists, use it first for report headings and detail rules
- if `prompts/amprompt.md` is missing or incomplete, fall back to `REPORT-CONTRACT.md`
- write the Korean main report yourself
- build the shell/mockup yourself
- use deterministic support only when it materially improves completeness or repeatability
- do not let deterministic support become the main workflow

## Default Working Flow

1. inspect visual evidence first when it exists
   - use the matching `<page>.jpg` file as the default primary visual source
2. inspect XML and source directly
3. decide the report heading/detail rule source
   - `prompts/amprompt.md` first
   - fallback: `REPORT-CONTRACT.md`
4. write the canonical Korean main report
5. create or refine the shell/mockup
6. if long-tail detail may be missing, use optional completeness support

## Optional Completeness Support

Deterministic support is allowed only for things like:

- full dataset lists
- full component lists
- full transaction lists
- backend candidate appendices
- machine-generated CSV references

Deterministic support is not the source of truth for:

- visual layout
- shell/mockup structure
- dominant business interpretation
- final report narrative

If deterministic support is used, link its output from the matching numbered report section such as:

- `4-4. 상세 목록: [datasets.csv](...)`
- `9-4. 상세 목록: [transactions.csv](...)`

## Report Rules

- Korean main report is canonical
- `prompts/amprompt.md` has priority for headings and detail level
- if `prompts/amprompt.md` is missing or incomplete, use `REPORT-CONTRACT.md`
- the main report must be readable standalone
- use numbered sections
- include short explanation + inline table in each major section
- use ASCII diagrams when helpful
- link exhaustive CSV or appendix files from the section that owns them
- do not turn the report into a link-only index

## Shell Rules

- prefer screenshots and direct visual evidence over rule-based layout guesses
- keep shell/layout decisions separate from behavior/API/SQL decisions
- placeholder actions are allowed
- do not present placeholders as completed functionality

## Reference Loading

Read these when needed:

- `prompts/amprompt.md`
- `REPORT-CONTRACT.md`
- `OPTIONAL-COMPLETENESS-SUPPORT.md`
- `references/review-contract.md`
- `references/visual-shell-contract.md`
