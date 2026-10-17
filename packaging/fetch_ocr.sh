#!/usr/bin/env bash
# Builds packaging/ocr: Tesseract for scanned scripts (1.0.6, register S-67), from Universitaet Mannheim's signed
# Windows installer. The source zip leaves it out (126 MB); studio.spec bundles it when it is there.
# usage: packaging/fetch_ocr.sh [tesseract-ocr-w64-setup-v5.3.0.20221214.exe]   (downloaded if not given)
# Needs: wine (with a display, e.g. xvfb-run), osslsigncode, x86_64-w64-mingw32-strip (binutils-mingw-w64).
# Output matches the 1.0.6 build's copy except for the PE header date and checksum of the 25 support DLLs.
set -euo pipefail
URL=https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.3.0.20221214.exe
SHA=175a326853f87474132c284072a821dd819c63b707b01879b309f80bd6c0ab1e
OUT="$(cd "$(dirname "$0")" && pwd)/ocr"
WORK=$(mktemp -d); trap 'rm -rf "$WORK"' EXIT
SETUP=${1:-$WORK/setup.exe}
signed() { local v; v=$(osslsigncode verify -in "$1" 2>&1 || true); [[ $v == *Mannheim* && $v == *"Signature verification: ok"* ]]; }
[ -f "$SETUP" ] || curl -fsSL -o "$SETUP" "$URL"
echo "$SHA  $SETUP" | sha256sum -c --quiet - || { echo "installer SHA-256 mismatch"; exit 1; }
signed "$SETUP" || { echo "installer signature check failed"; exit 1; }
export WINEPREFIX=$WORK/prefix WINEDEBUG=-all WINEDLLOVERRIDES="mscoree,mshtml="
wine "$SETUP" /S < /dev/null > /dev/null 2>&1 || true            # silent; it installs to Program Files whatever /D says
wineserver -w
T="$WINEPREFIX/drive_c/Program Files/Tesseract-OCR"
[ -f "$T/tesseract.exe" ] || { echo "the Tesseract installer did not run"; exit 1; }
SIGNED="tesseract.exe libtesseract-5.dll"                  # kept exactly as signed
DLLS="iconv.dll libarchive-13.dll libbz2-1.dll libcurl-4.dll libgcc_s_seh-1.dll libgif-7.dll libidn2-0.dll libintl-8.dll
libjbig-2.dll libjpeg-8.dll liblept-5.dll liblz4-1.dll liblzma-5.dll liblzo2-2.dll libnghttp2-14.dll libopenjp2.dll
libpng16-16.dll libstdc++-6.dll libtiff-5.dll libunistring-2.dll libwebp-7.dll libwinpthread-1.dll libxml2-2.dll
libzstd-1.dll zlib1.dll"                                   # what tesseract.exe loads; debug symbols stripped
rm -rf "$OUT"; mkdir -p "$OUT/tessdata"
for f in $SIGNED; do cp "$T/$f" "$OUT/"; signed "$OUT/$f" || { echo "$f signature check failed"; exit 1; }; done
for f in $DLLS; do x86_64-w64-mingw32-strip --strip-debug -o "$OUT/$f" "$T/$f"; done
cp "$T/tessdata/eng.traineddata" "$OUT/tessdata/"; cp -r "$T/tessdata/configs" "$OUT/tessdata/"
cp "$T/doc/LICENSE" "$OUT/LICENSE-tesseract.txt"
cat > "$OUT/README-OCR.txt" <<TXT
Tesseract OCR 5.3.0 (20221214), Windows build by Universitaet Mannheim, signed installer tesseract-ocr-w64-setup-v5.3.0.20221214.exe
SHA-256 $SHA, from https://digi.bib.uni-mannheim.de/tesseract/
Apache License 2.0 (LICENSE-tesseract.txt). tesseract.exe and libtesseract-5.dll as signed; support DLLs with debug symbols stripped.
English model: tessdata/eng.traineddata from the same installer.
TXT
wineserver -k 2>/dev/null || true
du -sh "$OUT"
