# Instala la skill visual-artifacts y su regla siempre activa en Antigravity (Windows).
#
#   .\install.ps1                       instalación global (%USERPROFILE%\.gemini\config)
#   .\install.ps1 -Workspace <dir>      solo para un proyecto (<dir>\.agents)
#   .\install.ps1 -Uninstall [-Workspace <dir>]
param(
    [string]$Workspace,
    [switch]$Uninstall
)
$ErrorActionPreference = 'Stop'

if ($Workspace) {
    if (-not (Test-Path -PathType Container $Workspace)) { throw "No existe el directorio: $Workspace" }
    $Root = Join-Path (Resolve-Path $Workspace) '.agents'
} elseif ($env:ANTIGRAVITY_CONFIG_DIR) {
    $Root = $env:ANTIGRAVITY_CONFIG_DIR
} else {
    $Root = Join-Path $HOME '.gemini\config'
}

$SkillDir = Join-Path $Root 'skills\visual-artifacts'
$RuleDir = Join-Path $Root 'rules'
$RuleFile = Join-Path $RuleDir 'visual-artifacts.md'

if ($Uninstall) {
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $SkillDir, $RuleFile
    Write-Host "Desinstalado de $Root"
    exit 0
}

New-Item -ItemType Directory -Force -Path $SkillDir, $RuleDir | Out-Null
Copy-Item -Recurse -Force (Join-Path $PSScriptRoot 'skills\visual-artifacts\*') $SkillDir

# La regla apunta a la skill con ruta absoluta: Antigravity a veces no descubre las skills globales solo.
$template = Get-Content -Raw -Encoding UTF8 (Join-Path $PSScriptRoot 'rules\visual-artifacts.md')
$rule = $template.Replace('{{SKILL_MD}}', (Join-Path $SkillDir 'SKILL.md'))
[IO.File]::WriteAllText($RuleFile, $rule, (New-Object Text.UTF8Encoding $false))

Write-Host "Skill instalada en: $SkillDir"
Write-Host "Regla instalada en: $RuleFile"
Write-Host 'Abre una conversación NUEVA en Antigravity y pide, por ejemplo: "haz un artifact comparando estas 3 opciones".'
