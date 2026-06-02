#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Switch the local Git identity for this repository based on sub-project role.

.DESCRIPTION
    NatilleraApp uses GitFlow with three contributors, each identified by their
    email address, working on a different sub-project:

        backend  → Luis Gregorio Toro Amador - Luthors  <luis.g.toro@gmail.com>
        frontend → Luis Toro                            <luthors@hotmail.com>
        mobile   → LUIS GREGORIO TORO AMADOR            <ltoro@qvision.us>

    This script sets git config --local for the current repository.
    It does NOT touch the global ~/.gitconfig.

.PARAMETER Role
    One of: backend | frontend | mobile
    Omit to display the current identity.

.EXAMPLE
    .\scripts\switch-git-user.ps1 backend
    .\scripts\switch-git-user.ps1 frontend
    .\scripts\switch-git-user.ps1 mobile
    .\scripts\switch-git-user.ps1          # shows current identity

.NOTES
    Run from the repository root.
    After switching, verify with: git config --local user.name
#>

param(
    [Parameter(Position = 0)]
    [ValidateSet("backend", "frontend", "mobile", "")]
    [string]$Role = ""
)

# ── Identities ────────────────────────────────────────────────────────────────

$identities = @{
    "backend"  = @{
        Name   = "Luis Gregorio Toro Amador - Luthors"
        Email  = "luis.g.toro@gmail.com"
        Branch = "feature/backend/*"
        Scope  = "backend/"
    }
    "frontend" = @{
        Name   = "Luis Toro"
        Email  = "luthors@hotmail.com"
        Branch = "feature/frontend/*"
        Scope  = "frontend/"
    }
    "mobile"   = @{
        Name   = "LUIS GREGORIO  TORO AMADOR"
        Email  = "ltoro@qvision.us"
        Branch = "feature/mobile/*"
        Scope  = "mobile/"
    }
}

# ── Helper ────────────────────────────────────────────────────────────────────

function Show-Current {
    $name  = git config --local user.name  2>$null
    $email = git config --local user.email 2>$null
    $branch = git branch --show-current    2>$null
    Write-Host ""
    Write-Host "  Current local identity:" -ForegroundColor Cyan
    Write-Host "    Name   : $name"
    Write-Host "    Email  : $email"
    Write-Host "    Branch : $branch"
    Write-Host ""
}

function Show-All {
    Write-Host ""
    Write-Host "  Available identities:" -ForegroundColor Yellow
    foreach ($key in $identities.Keys | Sort-Object) {
        $id = $identities[$key]
        Write-Host "    $($key.PadRight(10)) $($id.Name) <$($id.Email)>  →  $($id.Branch)"
    }
    Write-Host ""
    Write-Host "  Usage: .\scripts\switch-git-user.ps1 <backend|frontend|mobile>"
    Write-Host ""
}

# ── No argument: show current + options ──────────────────────────────────────

if ($Role -eq "") {
    Show-Current
    Show-All
    exit 0
}

# ── Validate we're in a git repo ─────────────────────────────────────────────

$gitRoot = git rev-parse --show-toplevel 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Not inside a git repository." -ForegroundColor Red
    exit 1
}

# ── Apply identity ────────────────────────────────────────────────────────────

$id = $identities[$Role]
git config --local user.name  $id.Name
git config --local user.email $id.Email

Write-Host ""
Write-Host "  Switched to '$Role' identity:" -ForegroundColor Green
Write-Host "    Name  : $($id.Name)"
Write-Host "    Email : $($id.Email)"
Write-Host ""
Write-Host "  Recommended branch pattern: $($id.Branch)" -ForegroundColor DarkGray
Write-Host "  Example: git checkout feature/$Role/your-feature-name" -ForegroundColor DarkGray
Write-Host ""
