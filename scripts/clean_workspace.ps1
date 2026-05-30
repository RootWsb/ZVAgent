param(
    [switch]$DryRun,
    [switch]$Apply,
    [switch]$IncludeRuntime,
    [switch]$IncludeTrainingArtifacts
)

$ErrorActionPreference = "Stop"

if (-not $DryRun -and -not $Apply) {
    $DryRun = $true
}

if ($DryRun -and $Apply) {
    throw "Use either -DryRun or -Apply, not both."
}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Test-InRepo {
    param([string]$Path)

    $resolved = (Resolve-Path -LiteralPath $Path -ErrorAction SilentlyContinue)
    if (-not $resolved) {
        return $false
    }

    $full = $resolved.Path.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    $root = $RepoRoot.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
    return ($full -eq $root) -or $full.StartsWith($root + [IO.Path]::DirectorySeparatorChar) -or $full.StartsWith($root + [IO.Path]::AltDirectorySeparatorChar)
}

function Add-Existing {
    param(
        [System.Collections.Generic.List[object]]$Targets,
        [string]$LiteralPath,
        [string]$Reason
    )

    $path = Join-Path $RepoRoot $LiteralPath
    if (Test-Path -LiteralPath $path) {
        $Targets.Add([pscustomobject]@{
            Path = $path
            Reason = $Reason
        }) | Out-Null
    }
}

$targets = [System.Collections.Generic.List[object]]::new()

Get-ChildItem -LiteralPath $RepoRoot -Recurse -Force -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
    ForEach-Object {
        $targets.Add([pscustomobject]@{ Path = $_.FullName; Reason = "Python bytecode cache" }) | Out-Null
    }

Get-ChildItem -LiteralPath $RepoRoot -Recurse -Force -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -in @(".pyc", ".pyo", ".pyd") } |
    ForEach-Object {
        $targets.Add([pscustomobject]@{ Path = $_.FullName; Reason = "Python bytecode file" }) | Out-Null
    }

Get-ChildItem -LiteralPath $RepoRoot -Force -Directory -Filter "*.egg-info" |
    ForEach-Object {
        $targets.Add([pscustomobject]@{ Path = $_.FullName; Reason = "Editable/build metadata" }) | Out-Null
    }

Add-Existing $targets ".pytest_cache" "Pytest cache"

if ($IncludeRuntime) {
    Add-Existing $targets "run.log" "Runtime log"
    Add-Existing $targets "debug.log" "Runtime log"
    Add-Existing $targets "user_datas.pkl" "Local runtime data"
    Add-Existing $targets "workspace" "Local runtime workspace"
    Add-Existing $targets "data" "Local runtime data"
    Add-Existing $targets "~" "Accidental project-local home directory"
}

if ($IncludeTrainingArtifacts) {
    Get-ChildItem -LiteralPath (Join-Path $RepoRoot "training") -Recurse -Force -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -in @("checkpoints", "comparison_report", "plots") } |
        ForEach-Object {
            $targets.Add([pscustomobject]@{ Path = $_.FullName; Reason = "Generated training artifact directory" }) | Out-Null
        }

    Get-ChildItem -LiteralPath (Join-Path $RepoRoot "training") -Recurse -Force -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like "*.errors.log" -or $_.Name -like "*_plot.png" } |
        ForEach-Object {
            $targets.Add([pscustomobject]@{ Path = $_.FullName; Reason = "Generated training artifact file" }) | Out-Null
        }
}

$targets = $targets |
    Sort-Object Path -Unique |
    Where-Object {
        if (-not (Test-InRepo $_.Path)) {
            Write-Warning "Skipping outside repo: $($_.Path)"
            return $false
        }
        return $true
    }

$directoryTargets = @(
    $targets |
        Where-Object { Test-Path -LiteralPath $_.Path -PathType Container } |
        ForEach-Object {
            $_.Path.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
        }
)

$targets = $targets |
    Where-Object {
        $path = $_.Path.TrimEnd([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar)
        foreach ($directory in $directoryTargets) {
            if ($path -ne $directory -and ($path.StartsWith($directory + [IO.Path]::DirectorySeparatorChar) -or $path.StartsWith($directory + [IO.Path]::AltDirectorySeparatorChar))) {
                return $false
            }
        }
        return $true
    }

if (-not $targets) {
    Write-Host "Nothing to clean."
    exit 0
}

if ($DryRun) {
    Write-Host "Dry run. These paths would be removed:"
    $targets | Select-Object Path, Reason | Format-Table -AutoSize
    Write-Host ""
    Write-Host "Run with -Apply to remove them."
    exit 0
}

Write-Host "Removing $($targets.Count) path(s)..."
foreach ($target in $targets) {
    Remove-Item -LiteralPath $target.Path -Recurse -Force
    Write-Host "Removed: $($target.Path)"
}
