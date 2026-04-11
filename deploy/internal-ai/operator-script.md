# Internal AI Pro Operator Script

Use this script when the project has been moved into the company environment and you want the shortest safe path to:

1. build the internal workspace
2. bootstrap AI Pro
3. run one sample AM page

This script assumes the realistic default:

- global `/harness` installation may be impossible
- custom tool registration may be impossible
- workspace file loading is still available
- direct command execution may still be usable

In other words:

- project harness activation is the real requirement
- direct execution is the normal runtime path
- global harness and tool registration are optional conveniences
- `UI Shell First` is allowed when the PM wants early layout signoff, but it does not replace the staged behavior lock flow

## Phase 0: Build Or Locate The Internal Workspace

If you are still in the full source repository, do not open the repo root in AI Pro.
From a shell, run:

```powershell
cd C:\path\to\am-bridge
python scripts/export_ai_pro_bundle.py
```

This creates:

```text
C:\path\to\am-bridge\exports\internal-ai-workspace
```

If you are already inside a copied exported bundle, skip this phase.
Do not try to run `scripts/export_ai_pro_bundle.py` from the exported bundle, because that script is only present in the source repository.

## Phase 1: Open The Correct Workspace

Open this folder in AI Pro:

```text
C:\path\to\am-bridge\exports\internal-ai-workspace
```

Do not open:

- the repository root
- anything under `artifacts/`

## Phase 2: First Message To Internal AI

Paste the full contents of:

```text
bootstrap-initial-prompt.md
```

Stop here if the readiness result is:

- `BLOCKED`
- or `PARTIAL` with missing runtime/tool evidence you cannot verify

If `prompts/amprompt.md` contains a real custom prompt, keep it in place.
Do not paste it first. It is supplemental and should be used only after the readiness check succeeds.

## Phase 3: Choose Runtime Mode

If the readiness report says:

- global command unavailable
- custom tool registration unavailable

then treat that as expected no-admin mode, skip the old admin-style bootstrap path, and use `no-admin-runtime-prompt.md`.

## Phase 3A: No-Admin Runtime Activation

Paste the full contents of:

```text
no-admin-runtime-prompt.md
```

Stop here if the internal AI reports all of these as unavailable:

- `scripts/am_stage.ps1`
- `python scripts/ai_pro_stage_runner.py ...`
- `am-bridge-analyze ...`

If one of them is available, continue with that execution path.

## Phase 3B: Admin-Style Bootstrap When Supported

Only use this phase if global command installation and custom tool registration are actually allowed.

Paste this exact prompt into the internal AI:

```text
Bootstrap this exported internal workspace for AI Pro + GLM-4.7 end to end.

Use these sources:
- integrations/ai-pro/bootstrap/glm-bootstrap-playbook.md
- integrations/ai-pro/bootstrap/bootstrap-manifest.json
- integrations/ai-pro/global/harness-global.md
- integrations/ai-pro/project/am-page-modernization.md
- integrations/ai-pro/tools/tool-contract.md
- scripts/ai_pro_stage_runner.py

Tasks:
1. Discover the local AI Pro config locations and formats.
2. Install the global harness.
3. Activate the project harness.
4. Register the am-bridge tools.
5. Validate the installed setup as far as possible using the bundled sample configuration first.

Do not claim success unless each step was actually completed or explicitly blocked.
If runtime registration cannot be verified, say so explicitly.
```

Stop here if the answer does not show evidence for:

- global harness status
- project harness status
- tool registration status
- config status
- validation result

If `prompts/amprompt.md` exists and contains a real project prompt, tell the internal AI to use it as an additional detail contract for report/config quality, not as a replacement for the harness.

## Phase 4: Run One Sample AM Page

The exported internal workspace includes the public sample inputs used by the default config.

Paste this exact prompt into the internal AI:

```text
Use the AM page modernization workflow for this workspace.
Target page: DefApp/Win32/form.xml

I am the PM and you are the PL.
Use am-bridge as the deterministic tool layer.
If prompts/amprompt.md exists, use it as supplemental guidance for report detail and Vue conversion config completeness, but do not override the staged workflow.
If registered tools are unavailable, use one of these direct execution paths:
1. `scripts/am_stage.ps1`
2. `python scripts/ai_pro_stage_runner.py ...`
3. `am-bridge-analyze ...`

Execution policy:
1. Classify whether this page needs `UI Shell First`.
2. If early layout signoff matters, create a UI shell blueprint with clearly marked placeholder actions.
3. Run stage1.
4. Review the package, detailed analysis report, and review.json.
5. Correct primaryDatasetId, mainGridComponentId, primaryTransactionIds, dataset usage, and backend traces if needed.
6. Run stage2.
7. Inspect the PM checklist and make sure it matches the page's real business functions.
8. Run stage3.
9. Report locked decisions, remaining risks, and next implementation step.
```

Expected sample signals:

- `primaryDatasetId = ds_scorechk`
- `mainGridComponentId = Grid0`
- backend trace includes `sampleDAO.ScoreChk`

## Phase 4A: Optional Korean Report Delivery

Use this only after the English report pack looks correct.

Ask the internal AI to read:

- `artifacts/reports/<page>/README.md`
- `artifacts/reports/<page>/translate-to-korean.md`
- the linked Stage 1 / Stage 2 overview docs
- the primary narrative reports under `artifacts/packages/` and `artifacts/plans/`

Rule:

- English reports remain canonical
- Korean output is a derived operator/PM delivery layer
- technical IDs, dataset IDs, transaction IDs, and file paths stay in backticks
- default to summary-only Korean delivery, not a full mirrored Korean report tree
- keep deep technical links pointed at the English canonical docs unless a Korean counterpart is explicitly required
- before writing Korean files, list the exact output files and make sure none overwrite the English originals

## Phase 5: Switch To The Real Project

Only after the sample run works, update:

```text
am-bridge.config.json
```

Provide real:

- `sourceRoots`
- `backendRoots`

After that, repeat the readiness check if the environment or tool registration changed.
