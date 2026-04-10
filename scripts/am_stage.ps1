param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("analyze", "stage1", "stage2", "stage3")]
    [string]$Stage,

    [Parameter(Mandatory = $true)]
    [string]$LegacyPage,

    [string]$Config = "am-bridge.config.json",

    [string]$Review
)

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptRoot
$runnerPath = Join-Path $scriptRoot "ai_pro_stage_runner.py"

$configPath = if ([System.IO.Path]::IsPathRooted($Config)) {
    $Config
} else {
    Join-Path $repoRoot $Config
}

$pythonArgs = @(
    $runnerPath
    $Stage
    $LegacyPage
    "--config"
    $configPath
)

if ($Review) {
    $pythonArgs += @("--review", $Review)
}

& python @pythonArgs
exit $LASTEXITCODE
