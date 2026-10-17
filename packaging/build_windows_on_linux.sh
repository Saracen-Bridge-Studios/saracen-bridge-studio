#!/usr/bin/env bash
# Build the Windows installer (SaracenBridgeStudio-Setup-<version>.exe) on Linux, without a Windows machine.
# Windows Python, PyInstaller and Inno Setup run under Wine; the result is a normal Windows installer.
# Each step below was run by hand on 12 Oct 2026 (Ubuntu 24.04) to build SaracenBridgeStudio-Setup-0.3.5.exe:
# 71/71 tests under Windows Python; the installed program passed packaging/smoke.py (16 checks); install and
# uninstall were clean. This script collects those steps; it has not yet been run start to finish as one script.
# Usage, from the repository root:  bash packaging/build_windows_on_linux.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${WORK:-$HOME/.cache/saracen-winbuild}"
PYVER="${PYVER:-3.13.16}"          # Windows Python from Microsoft's NuGet package (a plain zip, no installer)
INNO="${INNO:-6.7.3}"
export WINEPREFIX="$WORK/prefix" WINEDEBUG=-all WINEARCH=win64 WINEDLLOVERRIDES="mscoree,mshtml=" \
       XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/tmp/xdg-$(id -u)}"
mkdir -p "$WORK" "$XDG_RUNTIME_DIR" && chmod 700 "$XDG_RUNTIME_DIR"
# Wine needs a pipe, not a file, for console output, or Python fails with "Invalid handle".
w() { wine "$@" < /dev/null 2>&1 | cat; }

# 1. Wine 11 from WineHQ (Ubuntu's Wine 9 cannot launch the Inno Setup installer), Xvfb, signature tools
if ! wine --version 2>/dev/null | grep -qE "wine-1[1-9]"; then
  sudo dpkg --add-architecture i386
  sudo mkdir -pm755 /etc/apt/keyrings
  curl -fsSL https://dl.winehq.org/wine-builds/winehq.key | sudo gpg --dearmor -o /etc/apt/keyrings/winehq-archive.key --yes
  sudo curl -fsSL -o /etc/apt/sources.list.d/winehq-noble.sources \
    https://dl.winehq.org/wine-builds/ubuntu/dists/noble/winehq-noble.sources
  sudo apt-get update -qq && sudo apt-get install -y -qq --install-recommends winehq-stable xvfb xauth osslsigncode
fi

# 2. Wine prefix with Windows Python
if [ ! -f "$WINEPREFIX/drive_c/Python313/python.exe" ]; then
  xvfb-run -a wineboot -i < /dev/null 2>&1 | cat
  curl -fsSL -o "$WORK/python.nupkg" "https://api.nuget.org/v3-flatcontainer/python/$PYVER/python.$PYVER.nupkg"
  mkdir -p "$WINEPREFIX/drive_c/Python313" && (cd "$WINEPREFIX/drive_c/Python313" && unzip -q "$WORK/python.nupkg" 'tools/*' && mv tools/* . && rmdir tools)
  # Build environment only: older Wine lacks KERNEL32.CopyFile2, which Python 3.13's shutil uses; fall back safely.
  printf 'try:\n    import _winapi\n    if hasattr(_winapi, "CopyFile2"):\n        del _winapi.CopyFile2\nexcept Exception:\n    pass\n' \
    > "$WINEPREFIX/drive_c/Python313/Lib/sitecustomize.py"
  w 'C:\Python313\python.exe' -m ensurepip
fi
PY='C:\Python313\python.exe'
WIN_ROOT="Z:$(echo "$ROOT" | tr / '\\')"
WIN_WORK="Z:$(echo "$WORK" | tr / '\\')"

# 3. Dependencies. proxy_tools (pulled in by pywebview) ships only an old source package that will not build
#    under Wine, so a pure-Python wheel is assembled from it here.
if [ ! -f "$WORK/wheels/proxy_tools-0.1.0-py3-none-any.whl" ]; then
  mkdir -p "$WORK/wheels" "$WORK/pt" && pip download -q --no-deps --no-binary :all: proxy_tools==0.1.0 -d "$WORK/pt"
  tar xzf "$WORK/pt/proxy_tools-0.1.0.tar.gz" -C "$WORK/pt"
  python3 - "$WORK" <<'EOF'
import base64, hashlib, sys, zipfile, pathlib
work = pathlib.Path(sys.argv[1])
files = {"proxy_tools/__init__.py": (work / "pt/proxy_tools-0.1.0/proxy_tools/__init__.py").read_bytes(),
         "proxy_tools-0.1.0.dist-info/METADATA": b"Metadata-Version: 2.1\nName: proxy_tools\nVersion: 0.1.0\nLicense: MIT\n",
         "proxy_tools-0.1.0.dist-info/WHEEL": b"Wheel-Version: 1.0\nGenerator: manual\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
         "proxy_tools-0.1.0.dist-info/top_level.txt": b"proxy_tools\n"}
h = lambda b: "sha256=" + base64.urlsafe_b64encode(hashlib.sha256(b).digest()).rstrip(b"=").decode()
rec = "".join(f"{n},{h(b)},{len(b)}\n" for n, b in files.items()) + "proxy_tools-0.1.0.dist-info/RECORD,,\n"
with zipfile.ZipFile(work / "wheels/proxy_tools-0.1.0-py3-none-any.whl", "w", zipfile.ZIP_DEFLATED) as z:
    for n, b in files.items(): z.writestr(n, b)
    z.writestr("proxy_tools-0.1.0.dist-info/RECORD", rec)
EOF
fi
CA="${SSL_CERT_FILE:-}"; [ -n "$CA" ] && export PIP_CERT="Z:$(echo "$CA" | tr / '\\')"
w "$PY" -m pip install -q --no-warn-script-location --find-links "$WIN_WORK\\wheels" -r "$WIN_ROOT\\requirements-dev.txt"

# 3b. OCR for scanned scripts (1.0.6): Tesseract from Universitaet Mannheim's signed installer, into packaging/ocr
cd "$ROOT"
command -v x86_64-w64-mingw32-strip >/dev/null || sudo apt-get install -y -qq binutils-mingw-w64-x86-64
[ -f packaging/ocr/tesseract.exe ] || xvfb-run -a bash packaging/fetch_ocr.sh

# 4. Tests under Windows Python, then freeze
w "$PY" -m pytest -q -p no:cacheprovider | tail -2
python3 scripts/build_knowledge.py          # Ask Jonny's index of Jon's documents -> data/knowledge.db
w "$PY" -m PyInstaller packaging/studio.spec --noconfirm | tail -1
I=dist/SaracenBridgeStudio/_internal            # OCR kept once, beside tesseract.exe (1.0.6's first build had it twice)
[ -f $I/ocr/tesseract.exe ] && [ -f $I/ocr/libtesseract-5.dll ] && [ ! -f $I/libtesseract-5.dll ] || { echo "OCR bundle layout wrong"; exit 1; }

# 4b. The Studio window (0.4): a Tauri 2 shell, cross-compiled with mingw-w64, placed beside the launcher.
#     The launcher opens it first and falls back to an Edge app window if it cannot show the page.
if ! command -v x86_64-w64-mingw32-gcc >/dev/null; then sudo apt-get install -y -qq gcc-mingw-w64-x86-64 g++-mingw-w64-x86-64; fi
rustup target add x86_64-pc-windows-gnu >/dev/null
(cd packaging/shell && CARGO_TARGET_DIR="$WORK/shell-target" cargo build --release --target x86_64-pc-windows-gnu)
cp "$WORK/shell-target/x86_64-pc-windows-gnu/release/saracen-shell.exe" dist/SaracenBridgeStudio/studio-window.exe
# WebView2Loader.dll comes with the webview2-com-sys crate; it is Microsoft's, signed by Microsoft. Checked before shipping.
osslsigncode verify -in "$WORK/shell-target/x86_64-pc-windows-gnu/release/WebView2Loader.dll" 2>&1 | grep -q "O=Microsoft Corporation" || { echo "WebView2Loader signature check failed"; exit 1; }
cp "$WORK/shell-target/x86_64-pc-windows-gnu/release/WebView2Loader.dll" dist/SaracenBridgeStudio/

# 5. Smoke-test the Windows exe (port 8798; never 8799), throwaway data folder
STUDIO_HOME='C:\studio_smoke' wine dist/SaracenBridgeStudio/SaracenBridgeStudio.exe --headless --port 8798 < /dev/null 2>&1 | cat > "$WORK/smoke_app.log" &
python3 packaging/smoke.py http://127.0.0.1:8798 | tail -1
wineserver -k || true

# 6. Inno Setup and the Microsoft-signed WebView2 bootstrapper, then the installer
if [ ! -f "$WINEPREFIX/drive_c/InnoSetup/ISCC.exe" ]; then
  curl -fsSL -o "$WORK/innosetup.exe" "https://github.com/jrsoftware/issrc/releases/download/is-${INNO//./_}/innosetup-$INNO.exe"
  osslsigncode verify -in "$WORK/innosetup.exe" 2>&1 | grep -q "CN=Pyrsys B.V." || { echo "Inno Setup signature check failed"; exit 1; }
  xvfb-run -a wine "$WORK/innosetup.exe" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /CURRENTUSER '/DIR=C:\InnoSetup' < /dev/null 2>&1 | cat
fi
WV=packaging/redist/MicrosoftEdgeWebview2Setup.exe
[ -f "$WV" ] || curl -fsSL -o "$WV" "https://go.microsoft.com/fwlink/p/?LinkId=2124703"
osslsigncode verify -in "$WV" 2>&1 | grep -q "O=Microsoft Corporation" || { echo "WebView2 bootstrapper signature check failed"; exit 1; }
SIZE=$(du -sb dist/SaracenBridgeStudio | cut -f1)
[ "$SIZE" -gt 4000000000 ] && export STUDIO_SPAN=1
w 'C:\InnoSetup\ISCC.exe' 'packaging\installer.iss' | tail -3
ls -la dist/installer/ && sha256sum dist/installer/*.exe
