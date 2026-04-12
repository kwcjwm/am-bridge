# AI Pro Operator Prompts

## 1. End-To-End AM For One Page

```text
Use this workspace for AM on one page.
Target page: C:\path\to\aaa.xml

I am the PM and you are the PL.
You are the main analyst and report writer.

Do this in order:
1. Look for the matching main page image using `<page>.xml` -> `<page>.jpg`.
2. If the target page is `FF02_DtCode.xml`, require `FF02_DtCode.jpg` as the default main image.
3. If the main image is missing, ask me to provide it before treating the shell as reviewable.
4. Read screenshots or running-screen captures first if they exist.
5. Read the page XML and related source directly.
6. If `prompts/amprompt.md` exists, use it first for report headings and detail rules.
7. Write the canonical Korean main report following REPORT-CONTRACT.md.
8. Create the shell/mockup from visual/source evidence.
9. If exhaustive long-tail detail is still missing, use OPTIONAL-COMPLETENESS-SUPPORT.md to add reference material only.
10. Link every appendix or CSV from the matching numbered report section such as `4-4. 상세 목록`.
11. Keep shell/layout decisions separate from behavior/API/SQL decisions.

At the end, show:
- the Korean main report path
- any appendix/reference paths
- the shell/mockup path
- the next implementation step
```

## 2. Shell First Only

```text
The PM wants shell/layout agreement first.

Use screenshots, running-screen captures, XML, and source as evidence.
Recover the page shell as closely as practical.
Do not pretend behavior is already locked.
Use placeholder actions when needed.

Output:
- shell/mockup path
- visual rationale summary
- what still needs behavior/contract analysis
```

## 3. Completeness Pass Only

```text
The main Korean report already exists and is directionally correct.

Your task is only to reduce omission risk.
Use OPTIONAL-COMPLETENESS-SUPPORT.md if needed.
Add appendices or reference tables for long-tail items, but do not rewrite the main report around the tool output.

Output:
- updated report path
- appendix/reference paths
- what was added for completeness
```

## 4. Additional Derived Summary

```text
Use the reviewed Korean main report as the source of truth.
Produce an additional derived summary only when explicitly needed.

Rules:
- keep technical IDs in backticks
- keep links to detailed appendices by default
- do not overwrite the main Korean report
```
