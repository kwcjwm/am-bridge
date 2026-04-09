# Internal AI Pro Operator Script

Use this script when the project has been moved into the company environment and you want the shortest safe path to:

1. build the internal workspace
2. bootstrap AI Pro
3. run one sample AM page

## Phase 0: Build The Internal Workspace

If you cloned the full repository into the internal environment, do not open the repo root in AI Pro.
From a shell, run:

```powershell
cd C:\path\to\am-bridge
python scripts/export_ai_pro_bundle.py
```

This creates:

```text
C:\path\to\am-bridge\artifacts\internal-ai-workspace
```

## Phase 1: Open The Correct Workspace

Open this folder in AI Pro:

```text
C:\path\to\am-bridge\artifacts\internal-ai-workspace
```

Do not open:

- the repository root
- `artifacts/ai-pro-bundle`

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

## Phase 3: Bootstrap Harness, Skill, And Tools

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

Execution policy:
1. Run stage1.
2. Review the package, detailed analysis report, and review.json.
3. Correct primaryDatasetId, mainGridComponentId, primaryTransactionIds, dataset usage, and backend traces if needed.
4. Run stage2.
5. Inspect the PM checklist and make sure it matches the page's real business functions.
6. Run stage3.
7. Report locked decisions, remaining risks, and next implementation step.
```

Expected sample signals:

- `primaryDatasetId = ds_scorechk`
- `mainGridComponentId = Grid0`
- backend trace includes `sampleDAO.ScoreChk`

## Phase 5: Switch To The Real Project

Only after the sample run works, update:

```text
am-bridge.config.json
```

Provide real:

- `sourceRoots`
- `backendRoots`

After that, repeat the readiness check if the environment or tool registration changed.
