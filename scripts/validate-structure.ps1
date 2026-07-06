param(
    [switch]$Strict
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$failures = [System.Collections.Generic.List[string]]::new()
$warnings = [System.Collections.Generic.List[string]]::new()

function Add-Failure([string]$message) {
    $failures.Add($message) | Out-Null
}

function Add-Warning([string]$message) {
    $warnings.Add($message) | Out-Null
}

function Require-File([string]$path, [string]$label) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        Add-Failure "missing ${label}: ${path}"
    }
}

function Require-Dir([string]$path, [string]$label) {
    if (-not (Test-Path -LiteralPath $path -PathType Container)) {
        Add-Failure "missing ${label}: ${path}"
    }
}

$platformFiles = @(
    "_platform/profile_schema.md",
    "_platform/create_flow.md",
    "_platform/lorebook_schema.md",
    "_platform/copy_rules.md"
)

foreach ($rel in $platformFiles) {
    Require-File (Join-Path $repoRoot $rel) $rel
}

$templateDir = Join-Path $repoRoot "characters/_TEMPLATE"
Require-Dir $templateDir "character template"
foreach ($name in @("canon.md", "lorebook.md", "profile.twiv.md", "meta.yml", "images/INDEX.md", "media/INDEX.md")) {
    Require-File (Join-Path $templateDir $name) "template $name"
}

$charactersDir = Join-Path $repoRoot "characters"
$characterDirs = Get-ChildItem -LiteralPath $charactersDir -Directory |
    Where-Object { $_.Name -ne "_TEMPLATE" } |
    Sort-Object Name

foreach ($dir in $characterDirs) {
    $slug = $dir.Name
    $meta = Join-Path $dir.FullName "meta.yml"
    $canon = Join-Path $dir.FullName "canon.md"
    $lore = Join-Path $dir.FullName "lorebook.md"
    $profile = Join-Path $dir.FullName "profile.twiv.md"
    $imagesDir = Join-Path $dir.FullName "images"
    $imageIndex = Join-Path $imagesDir "INDEX.md"
    $mediaDir = Join-Path $dir.FullName "media"

    Require-File $meta "$slug/meta.yml"
    Require-File $canon "$slug/canon.md"
    Require-File $lore "$slug/lorebook.md"
    Require-File $profile "$slug/profile.twiv.md"
    Require-Dir $imagesDir "$slug/images"
    Require-File $imageIndex "$slug/images/INDEX.md"

    # media/ (온보딩 영상) is video-first; warn (not fail) if absent
    if (-not (Test-Path -LiteralPath $mediaDir -PathType Container)) {
        Add-Warning "$slug has no media/ (온보딩 영상) folder"
    }

    if (Test-Path -LiteralPath $meta -PathType Leaf) {
        $metaText = Get-Content -Raw -Encoding UTF8 -LiteralPath $meta
        $slugPattern = "(?m)^slug:\s*$([regex]::Escape($slug))\s*$"
        if ($metaText -notmatch $slugPattern) {
            Add-Failure "$slug meta.yml slug mismatch"
        }

        $declaredImages = $null
        if ($metaText -match "(?m)^images:\s*(\d+)\s*$") {
            $declaredImages = [int]$Matches[1]
        } else {
            Add-Warning "$slug meta.yml has no images count"
        }

        $imageFiles = @()
        if (Test-Path -LiteralPath $imagesDir -PathType Container) {
            $imageFiles = @(Get-ChildItem -LiteralPath $imagesDir -File |
                Where-Object { $_.Extension.ToLowerInvariant() -in @(".png", ".jpg", ".jpeg", ".webp") })
        }

        if ($null -ne $declaredImages -and $declaredImages -ne $imageFiles.Count) {
            Add-Failure "$slug image count mismatch: meta=$declaredImages actual=$($imageFiles.Count)"
        }

        if (Test-Path -LiteralPath $imageIndex -PathType Leaf) {
            $indexText = Get-Content -Raw -Encoding UTF8 -LiteralPath $imageIndex
            foreach ($image in $imageFiles) {
                if ($indexText -notlike "*$($image.Name)*") {
                    Add-Failure "$slug images/INDEX.md missing image: $($image.Name)"
                }
            }
        }

        if ($metaText -match "(?m)^copy_risk:\s*true\s*$") {
            $riskText = ""
            if (Test-Path -LiteralPath $canon -PathType Leaf) {
                $riskText += Get-Content -Raw -Encoding UTF8 -LiteralPath $canon
            }
            if (Test-Path -LiteralPath $lore -PathType Leaf) {
                $riskText += "`n" + (Get-Content -Raw -Encoding UTF8 -LiteralPath $lore)
            }
            if ($riskText -notmatch "\uAE08\uC9C0\uC120|Guardrails|guardrail|forbidden") {
                Add-Failure "$slug copy_risk=true but no visible risk/guardrail section"
            }
        }
    }
}

if ($warnings.Count -gt 0) {
    Write-Host "WARNINGS"
    $warnings | ForEach-Object { Write-Host "- $_" }
}

if ($failures.Count -gt 0) {
    Write-Host "FAILED"
    $failures | ForEach-Object { Write-Host "- $_" }
    exit 1
}

Write-Host "OK: platform docs + template + $($characterDirs.Count) character folders validated."
if ($Strict) {
    Write-Host "Strict mode currently checks the same structural contract."
}
