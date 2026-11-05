#!/usr/bin/env bash
# Build the Mac app and its disk image (dist/installer/SaracenBridgeStudio-<version>.dmg) on an Apple Silicon Mac.
# Runs on GitHub's Mac build machines (.github/workflows/build.yml) or on any Apple Silicon Mac with Xcode's
# command-line tools, Python 3.13, Go 1.26 and Rust.
#
# Signing: with MAC_SIGN_IDENTITY set ("Developer ID Application: <name> (<team>)", in the keychain) the app is signed
# for distribution, and with NOTARY_KEY (an App Store Connect API key, .p8), NOTARY_KEY_ID and NOTARY_ISSUER it is
# also notarized by Apple and stapled, so it opens with no warning. Without them it is signed ad hoc: fine on the
# build Mac and on test Macs after System Settings › Privacy & Security › Open Anyway.
#
# Usage, from the repository root:  bash packaging/build_mac.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
WORK="${WORK:-$ROOT/build/mac}"
LK_VERSION="${LK_VERSION:-1.13.10}"        # the same LiveKit release as the Windows build (packaging/livekit/README.txt)
APP="dist/Saracen Bridge Studio.app"
SIGN="${MAC_SIGN_IDENTITY:--}"             # "-" signs ad hoc
VERSION=$(python3 -c "import re; print(re.search(r'^VERSION = \"([^\"]+)\"', open('engine/studio/server.py').read(), re.M).group(1))")
# Apple Silicon (arm64) or Intel (x86_64): each Mac builds its own kind (5 Nov: Jon's 2019 MacBook Pro is Intel)
ARCH="$(uname -m)"
case "$(uname -s)-$ARCH" in Darwin-arm64) RUST_T=aarch64-apple-darwin; KIND="Apple-Silicon";; Darwin-x86_64) RUST_T=x86_64-apple-darwin; KIND="Intel";;
  *) echo "Build on a Mac."; exit 1;; esac
export STUDIO_MAC_ARCH="$ARCH"
mkdir -p "$WORK" packaging/macos/build dist/installer
echo "== Saracen Bridge Studio $VERSION for Mac"

# 1. Python dependencies
python3 -m pip install -q -r requirements-dev.txt

# 2. OCR for scanned scripts: Apple's Vision text recognition, answering in Tesseract's format
swiftc -O -target "$ARCH-apple-macos13" -o packaging/macos/build/studio-ocr packaging/macos/studio-ocr.swift

# what the Mac OCR reads from the scanned fixture, in the log, so a misread can be seen and fixed (1.2.1)
STUDIO_TESSERACT="$ROOT/packaging/macos/build/studio-ocr" PYTHONPATH=engine python3 - <<'PY' || true
from pathlib import Path
from studio import script
data = Path("tests/fixtures/sample_scanned.pdf").read_bytes()
r = script.parse("sample_scanned.pdf", data)
print("== Mac OCR of sample_scanned.pdf: cast", [(c["name"], c["dialogue_blocks"]) for c in r["cast"]], "scenes", r["scene_count"])
print(script.text("sample_scanned.pdf", data))
print("== end of Mac OCR")
PY

# 3. Tests, natively on the Mac, with the Mac OCR reading the scanned-script fixture
STUDIO_TESSERACT="$ROOT/packaging/macos/build/studio-ocr" python3 -m pytest -q -p no:cacheprovider

# 4. Call server: LiveKit from its published source (needs cgo on the Mac, so it is built here, not cross-compiled)
if [ ! -x packaging/livekit/livekit-server ]; then
  rm -rf "$WORK/livekit"
  git clone -q --depth 1 --branch "v$LK_VERSION" https://github.com/livekit/livekit-server "$WORK/livekit"
  # the module download can drop on a build machine's network (5 Nov, Windows job: proxy.golang.org stream error); try it three times
  (cd "$WORK/livekit" && for t in 1 2 3; do go mod download && break; echo "go mod download failed (try $t); retrying"; sleep $((15 * t)); done)
  (cd "$WORK/livekit" && go build -trimpath -ldflags "-s -w" -o "$ROOT/packaging/livekit/livekit-server" ./cmd/server)
fi
packaging/livekit/livekit-server --version

# 5. The Studio's window: the same Tauri 2 shell as Windows, built for Apple Silicon
rustup target add "$RUST_T" >/dev/null 2>&1 || true
(cd packaging/shell && CARGO_TARGET_DIR="$WORK/shell-target" cargo build --release --target "$RUST_T")

# 6. Ask Jonny's index of Jon's documents, then the app
python3 scripts/build_knowledge.py
rm -rf "$APP"
python3 -m PyInstaller packaging/studio.spec --noconfirm
F="$APP/Contents/Frameworks"
[ -x "$F/livekit/livekit-server" ] && [ -x "$F/ocr/studio-ocr" ] || { echo "Call server or OCR missing from the app"; exit 1; }

# 7. The window app goes inside the Studio's (Contents/Helpers): it carries the Dock icon, the menus and Cmd-Q
W="$APP/Contents/Helpers/Saracen Bridge Studio.app"
mkdir -p "$W/Contents/MacOS" "$W/Contents/Resources"
cp "$WORK/shell-target/$RUST_T/release/saracen-shell" "$W/Contents/MacOS/studio-window"
cp packaging/macos/studio.icns "$W/Contents/Resources/"
sed "s/@VERSION@/$VERSION/g" packaging/macos/window-Info.plist > "$W/Contents/Info.plist"
plutil -lint "$W/Contents/Info.plist"

# 8. Sign inside out: the window app, then the Studio. A real identity gets the hardened runtime and a secure
#    timestamp (what notarization requires); ad hoc stays plain so its libraries keep loading.
if [ "$SIGN" = "-" ]; then OPTS=(--force --sign -); else OPTS=(--force --options runtime --timestamp --sign "$SIGN"); fi
codesign "${OPTS[@]}" --entitlements packaging/macos/window-entitlements.plist "$W"
codesign "${OPTS[@]}" --entitlements packaging/macos/entitlements.plist "$APP"
codesign --verify --deep --strict --verbose=2 "$APP"

# 9. Smoke test the built app (port 8798; never 8799) in a throwaway data folder, hosting a production
SMOKE_HOME="$(mktemp -d)"
STUDIO_HOME="$SMOKE_HOME" "$APP/Contents/MacOS/SaracenBridgeStudio" --headless --port 8798 > "$WORK/smoke_app.log" 2>&1 &
APP_PID=$!
trap 'kill $APP_PID 2>/dev/null || true' EXIT
# Room hosting (--host) is left out of the gate for now: on GitHub's Mac (5 Nov) starting a production through the
# packaged app timed out after 60 s with nothing in its log (register S-124, open; likely a Keychain or firewall
# prompt no one can answer on a build machine). Every other check gates the build.
set -o pipefail
python3 packaging/smoke.py http://127.0.0.1:8798 | tee "$WORK/smoke.log" | tail -3
echo "NOTE: Room hosting not smoke-tested on this build machine (S-124)"
kill $APP_PID; wait $APP_PID 2>/dev/null || true; trap - EXIT
pkill -f "$SMOKE_HOME" 2>/dev/null || true          # the call server it started reads its config from there

# 10. Disk image: the app beside a link to Applications, to drag across
DMG="dist/installer/SaracenBridgeStudio-$VERSION-$KIND.dmg"
STAGE="$WORK/dmg"
rm -rf "$STAGE" "$DMG" && mkdir -p "$STAGE"
ditto "$APP" "$STAGE/Saracen Bridge Studio.app"
ln -s /Applications "$STAGE/Applications"
hdiutil create -volname "Saracen Bridge Studio" -srcfolder "$STAGE" -fs HFS+ -format UDZO -ov "$DMG" >/dev/null
if [ "$SIGN" != "-" ]; then
  codesign --force --timestamp --sign "$SIGN" "$DMG"
  if [ -n "${NOTARY_KEY:-}" ]; then
    xcrun notarytool submit "$DMG" --key "$NOTARY_KEY" --key-id "$NOTARY_KEY_ID" --issuer "$NOTARY_ISSUER" --wait
    xcrun stapler staple "$DMG"
    spctl --assess --type open --context context:primary-signature --verbose=2 "$DMG"
  fi
fi
ls -la dist/installer/ && shasum -a 256 "$DMG"
