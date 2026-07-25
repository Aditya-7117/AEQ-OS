# Installs AEQ-OS into $HOME\.ai_os on Windows.
# Junctions require no elevated privilege on modern Windows/NTFS, unlike
# symlinks, so this uses a directory junction instead of New-Item -ItemType SymbolicLink.
# Existing ~\.ai_os content is backed up, never deleted.

$ErrorActionPreference = "Stop"

$RepoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Target = Join-Path $HOME ".ai_os"

foreach ($f in @("BOOT.md", "ROUTER_MAP.json", "CORE", "DOMAINS")) {
    if (-not (Test-Path (Join-Path $RepoDir $f))) {
        Write-Error "$RepoDir\$f not found - run this script from a checkout of the AEQ-OS repo"
        exit 1
    }
}

$existing = Get-Item -Force -Path $Target -ErrorAction SilentlyContinue
if ($existing) {
    if ($existing.Attributes -match "ReparsePoint") {
        # A junction/symlink is just a pointer with no data of its own --
        # always safe to remove and recreate, regardless of where it
        # currently points. Using .Delete() directly (not Remove-Item)
        # because .NET guarantees a non-recursive delete on a reparse point
        # does not traverse it; Remove-Item -Force's cross-platform behavior
        # on a directory-symlink is inconsistent and can require -Recurse,
        # which would be dangerous here (it would delete through the link).
        Write-Host "existing junction found at $Target -- repointing to this checkout."
        $existing.Delete()
    } else {
        $backup = Join-Path $HOME (".ai_os.backup-" + (Get-Date -Format "yyyyMMddHHmmss"))
        Write-Host "$Target already exists as a real directory - backing it up to $backup"
        Move-Item $Target $backup
    }
}

try {
    New-Item -ItemType Junction -Path $Target -Target $RepoDir -ErrorAction Stop | Out-Null
} catch {
    Write-Error "Could not create the junction at $Target. If this is a permissions issue, try running PowerShell as Administrator. Underlying error: $_"
    exit 1
}
Write-Host "installed: $Target -> $RepoDir"

Write-Host ""
Write-Host "Next step - wire this into your agent tools (one-time, per tool):"
Write-Host "  Claude Code:  append templates\CLAUDE.md-snippet.md's line to `$env:USERPROFILE\.claude\CLAUDE.md"
Write-Host "  Antigravity:  copy templates\AGENTS.md to `$env:USERPROFILE\.gemini\AGENTS.md"
Write-Host "  Cursor:       paste templates\cursor-user-rules.txt into Settings -> Rules -> User Rules"
Write-Host "  Windsurf:     see templates\windsurf-rules.md"
Write-Host "  Copilot:      see templates\copilot-instructions.md"
Write-Host "  Cline/Roo:    see templates\clinerules.md"
Write-Host "  Aider:        see templates\aider-conventions.md"
Write-Host "  Any tool that reads a project-root AGENTS.md natively needs no extra step -"
Write-Host "  copy templates\AGENTS.md into a specific project's root to cover teammates"
Write-Host "  who never ran this installer."
Write-Host ""
Write-Host "Verify: Select-String -Path `$env:USERPROFILE\.ai_os\*\*.md -Pattern 'QT-STOP-3'"
