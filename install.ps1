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

$existing = Get-Item -Path $Target -ErrorAction SilentlyContinue
if ($existing) {
    if ($existing.LinkType -eq "Junction") {
        $currentTarget = $existing.Target
        if ($currentTarget -eq $RepoDir) {
            Write-Host "already installed from this checkout. Nothing to do."
            exit 0
        }
        Write-Host "repointing existing junction to this checkout."
        Remove-Item $Target -Force
    } else {
        $backup = Join-Path $HOME (".ai_os.backup-" + (Get-Date -Format "yyyyMMddHHmmss"))
        Write-Host "$Target already exists as a real directory - backing it up to $backup"
        Move-Item $Target $backup
    }
}

New-Item -ItemType Junction -Path $Target -Target $RepoDir | Out-Null
Write-Host "installed: $Target -> $RepoDir"

Write-Host ""
Write-Host "Next step - wire this into your agent tools (one-time, per tool):"
Write-Host "  Claude Code:  append templates\CLAUDE.md-snippet.md's line to `$env:USERPROFILE\.claude\CLAUDE.md"
Write-Host "  Antigravity:  copy templates\AGENTS.md to `$env:USERPROFILE\.gemini\AGENTS.md"
Write-Host "  Cursor:       paste templates\cursor-user-rules.txt into Settings -> Rules -> User Rules"
Write-Host ""
Write-Host "Verify: Select-String -Path `$env:USERPROFILE\.ai_os\*\*.md -Pattern 'QT-STOP-3'"
