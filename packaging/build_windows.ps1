# Build the Windows installer on any Windows 10/11 PC.
# Prerequisites: Python 3.13 or newer (python.org with "Add to PATH", or uv) and Inno Setup 6 (jrsoftware.org).
# Run from the repository root in PowerShell:   .\packaging\build_windows.ps1
$ErrorActionPreference = "Stop"
function Check($what) { if ($LASTEXITCODE -ne 0) { throw "$what failed (exit $LASTEXITCODE)" } }
# OCR for scanned scripts (1.0.6) is bundled from packaging\ocr, which the source zip leaves out (126 MB).
# Make it with packaging/fetch_ocr.sh (Linux or WSL: Universitaet Mannheim's signed Tesseract installer, checked by SHA-256).
if (-not (Test-Path packaging\ocr\tesseract.exe)) { throw "packaging\ocr is missing: run packaging/fetch_ocr.sh first (see its header)" }
# Reuses an existing .venv (e.g. made with: uv venv --seed --python 3.13 .venv); otherwise creates one.
if (-not (Test-Path .venv\Scripts\python.exe)) { python -m venv .venv; Check "venv" }
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements-dev.txt; Check "pip install"
.\.venv\Scripts\python -m pytest -q; Check "Tests"
.\.venv\Scripts\python scripts\build_knowledge.py; Check "Knowledge index"
.\.venv\Scripts\pyinstaller packaging\studio.spec --noconfirm; Check "PyInstaller"
# Smoke-test the packaged app on port 8798 (8799 is reserved for Aiden on DADS_BEAST), with a throwaway data folder.
$env:STUDIO_HOME = Join-Path $env:TEMP "studio_smoke_$(Get-Random)"
$app = Start-Process dist\SaracenBridgeStudio\SaracenBridgeStudio.exe -ArgumentList "--headless","--port","8798" -PassThru
try { .\.venv\Scripts\python packaging\smoke.py http://127.0.0.1:8798; if ($LASTEXITCODE -ne 0) { throw "Smoke test failed" } }
finally { Stop-Process $app -ErrorAction SilentlyContinue; Remove-Item Env:\STUDIO_HOME }
# WebView2 bootstrapper for the installer (build time only; verified as Microsoft-signed).
$wv = "packaging\redist\MicrosoftEdgeWebview2Setup.exe"
if (-not (Test-Path $wv)) { Invoke-WebRequest "https://go.microsoft.com/fwlink/p/?LinkId=2124703" -OutFile $wv }
$sig = Get-AuthenticodeSignature $wv
if ($sig.Status -ne "Valid" -or $sig.SignerCertificate.Subject -notmatch "Microsoft Corporation") { throw "WebView2 bootstrapper signature check failed" }
# Split the installer only if a bundled model makes it too big for one file (Inno Setup limit 4.2 GB).
$size = (Get-ChildItem dist\SaracenBridgeStudio -Recurse -File | Measure-Object Length -Sum).Sum
if ($size -gt 4000000000) { $env:STUDIO_SPAN = "1"; Write-Host "Large build ($([math]::Round($size/1GB,1)) GB): Setup.exe + Setup-*.bin" }
$iscc = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
if (-not (Test-Path $iscc)) { $iscc = "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe" }
& $iscc packaging\installer.iss; Check "Inno Setup"
Write-Host "Installer written to dist\installer\" -ForegroundColor Cyan
