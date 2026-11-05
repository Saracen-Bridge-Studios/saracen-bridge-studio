# Builds packaging\ocr on Windows: Tesseract for scanned scripts (1.0.6, register S-67), from Universitaet
# Mannheim's signed installer. The Windows twin of fetch_ocr.sh (which does the same under Wine on Linux).
# Usage, from the repository root in PowerShell:  .\packaging\fetch_ocr.ps1 [path\to\tesseract-ocr-w64-setup-v5.3.0.20221214.exe]
# Checks the installer's SHA-256 and its Authenticode signature, runs it silently into a throwaway folder, keeps
# tesseract.exe and libtesseract-5.dll exactly as signed, and copies the 25 support DLLs it loads (debug symbols
# stripped when MinGW's strip is on the PATH, as on GitHub's Windows runners; otherwise as shipped).
param([string]$Setup = "")
$ErrorActionPreference = "Stop"
$Url = "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.3.0.20221214.exe"
$Sha = "175a326853f87474132c284072a821dd819c63b707b01879b309f80bd6c0ab1e"
$Out = Join-Path $PSScriptRoot "ocr"
$Work = Join-Path $env:TEMP ("tess_" + [guid]::NewGuid().ToString("n"))
New-Item -ItemType Directory -Path $Work | Out-Null
try {
  if (-not $Setup) { $Setup = Join-Path $Work "setup.exe"; Invoke-WebRequest $Url -OutFile $Setup }
  if ((Get-FileHash $Setup -Algorithm SHA256).Hash.ToLower() -ne $Sha) { throw "installer SHA-256 mismatch" }
  $sig = Get-AuthenticodeSignature $Setup
  if ($sig.Status -ne "Valid" -or $sig.SignerCertificate.Subject -notmatch "Mannheim") { throw "installer signature check failed" }
  $Dir = Join-Path $Work "Tesseract-OCR"
  $p = Start-Process $Setup -ArgumentList "/S", "/D=$Dir" -Wait -PassThru
  # The installer may ignore /D and go to Program Files (it does under Wine); look there too.
  if (-not (Test-Path (Join-Path $Dir "tesseract.exe"))) { $Dir = Join-Path $env:ProgramFiles "Tesseract-OCR" }
  if (-not (Test-Path (Join-Path $Dir "tesseract.exe"))) { throw "the Tesseract installer did not run (exit $($p.ExitCode))" }
  $Signed = "tesseract.exe", "libtesseract-5.dll"
  $Dlls = "iconv.dll libarchive-13.dll libbz2-1.dll libcurl-4.dll libgcc_s_seh-1.dll libgif-7.dll libidn2-0.dll libintl-8.dll libjbig-2.dll libjpeg-8.dll liblept-5.dll liblz4-1.dll liblzma-5.dll liblzo2-2.dll libnghttp2-14.dll libopenjp2.dll libpng16-16.dll libstdc++-6.dll libtiff-5.dll libunistring-2.dll libwebp-7.dll libwinpthread-1.dll libxml2-2.dll libzstd-1.dll zlib1.dll".Split(" ")
  if (Test-Path $Out) { Remove-Item $Out -Recurse -Force }
  New-Item -ItemType Directory -Path (Join-Path $Out "tessdata") | Out-Null
  foreach ($f in $Signed) {
    Copy-Item (Join-Path $Dir $f) $Out
    $s = Get-AuthenticodeSignature (Join-Path $Out $f)
    if ($s.Status -ne "Valid" -or $s.SignerCertificate.Subject -notmatch "Mannheim") { throw "$f signature check failed" }
  }
  $strip = Get-Command strip -ErrorAction SilentlyContinue
  foreach ($f in $Dlls) {
    if ($strip) { & $strip.Source --strip-debug -o (Join-Path $Out $f) (Join-Path $Dir $f); if ($LASTEXITCODE -ne 0) { throw "strip $f failed" } }
    else { Copy-Item (Join-Path $Dir $f) $Out }
  }
  Copy-Item (Join-Path $Dir "tessdata\eng.traineddata") (Join-Path $Out "tessdata")
  Copy-Item (Join-Path $Dir "tessdata\configs") (Join-Path $Out "tessdata\configs") -Recurse
  Copy-Item (Join-Path $Dir "doc\LICENSE") (Join-Path $Out "LICENSE-tesseract.txt")
  @"
Tesseract OCR 5.3.0 (20221214), Windows build by Universitaet Mannheim, signed installer tesseract-ocr-w64-setup-v5.3.0.20221214.exe
SHA-256 $Sha, from https://digi.bib.uni-mannheim.de/tesseract/
Apache License 2.0 (LICENSE-tesseract.txt). tesseract.exe and libtesseract-5.dll as signed; support DLLs with debug symbols stripped.
English model: tessdata/eng.traineddata from the same installer.
"@ | Set-Content -Path (Join-Path $Out "README-OCR.txt") -Encoding utf8
  $mb = [math]::Round(((Get-ChildItem $Out -Recurse -File | Measure-Object Length -Sum).Sum / 1MB), 1)
  Write-Host "packaging\ocr: $mb MB" -ForegroundColor Cyan
} finally { Remove-Item $Work -Recurse -Force -ErrorAction SilentlyContinue }
