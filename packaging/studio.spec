# PyInstaller spec: builds the Saracen Bridge Studio app folder (dist/SaracenBridgeStudio) on Windows, and the
# Mac app (dist/Saracen Bridge Studio.app, Apple Silicon) on a Mac (packaging/build_mac.sh).
# Run from the repository root:  pyinstaller packaging/studio.spec --noconfirm
import os
import re
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

ROOT = Path(SPECPATH).parent
MAC = sys.platform == "darwin"
VERSION = re.search(r'^VERSION = "([^"]+)"', (ROOT / "engine" / "studio" / "server.py").read_text(), re.M).group(1)
datas = [
    (str(ROOT / "data" / "studio_reference.db"), "data"),
    (str(ROOT / "data" / "knowledge.db"), "data"),            # Ask Jonny's index of Jon's documents (scripts/build_knowledge.py)
    (str(ROOT / "ui"), "ui"),
    (str(ROOT / "projects"), "projects"),
    (str(ROOT / "sources" / "shared"), "sources/shared"),
    (str(ROOT / "sources" / "t10_agreement_builder"), "sources/t10_agreement_builder"),
    (str(ROOT / "sources" / "t02_script_coverage"), "sources/t02_script_coverage"),     # Jon's coverage spec, read at run time
    (str(ROOT / "sources" / "t01_look_book"), "sources/t01_look_book"),                 # Jon's look book spec, read at run time
    (str(ROOT / "sources" / "t04_sales_agent" / "skills" / "instructions" / "references" / "Saracen_Bridge_Sales_Valuation_Engine_v4_1_Integrated_Imports.xlsx"),
     "sources/t04_sales_agent/skills/instructions/references"),                       # Jon's Sales Valuation Engine, evaluated at run time
    (str(ROOT / "tools"), "tools"),
]
# Jon's instructions the 1.0.7 AI features read at run time (the first 1.0.7 build missed them: term sheets failed)
for t in ("t05_brand_integration", "t07_bfi_certification", "fpm_finance_plan_modeller"):
    datas.append((str(ROOT / "sources" / t / "skills" / "instructions" / "SKILL.md"), f"sources/{t}/skills/instructions"))
# The Room (1.0.8): the safety-word list the crypto library reads at run time; ui/vendor (LiveKit, MIT/Apache) rides in ui.
# 1.1.0: whoever starts a production hosts it, so the Studio carries the hub (and its phone app) and LiveKit.
datas.append((str(ROOT / "engine" / "room_crypto" / "words.txt"), "room_crypto"))
datas.append((str(ROOT / "engine" / "room_hub" / "static"), "room_hub/static"))
LK = ROOT / "packaging" / "livekit"
mac_binaries = []        # Mac executables go in as binaries, so the build signs them with the app (notarization)
if MAC and (LK / "livekit-server").exists():
    mac_binaries.append((str(LK / "livekit-server"), "livekit"))
    datas += [(str(LK / "LICENSE-livekit.txt"), "livekit"), (str(LK / "NOTICE-livekit.txt"), "livekit")]
elif not MAC and (LK / "livekit-server.exe").exists():
    datas.append((str(LK), "livekit"))
datas.append((str(ROOT / "engine" / "room_crypto" / "LICENSE-wordlist.txt"), "room_crypto"))
datas += collect_data_files("docx", include_py_files=True)   # python-docx's own part templates (headers, footers): needed to render reports
datas += collect_data_files("pypdfium2_raw") + collect_data_files("pypdfium2")      # PDFium renders look book pages
# Optional built-in AI engine: packaging/llm/llama-server.exe (+ its DLLs) and packaging/llm/models/<model>.gguf.
# Present only when the build bundles a model (see packaging/llm/README.txt).
if (ROOT / "packaging" / "llm").exists() and any((ROOT / "packaging" / "llm" / "models").glob("*.gguf")):
    datas.append((str(ROOT / "packaging" / "llm"), "llm"))
# OCR for scanned scripts (1.0.6): Tesseract 5.3.0, Universitaet Mannheim's signed Windows build (packaging/ocr, see README-OCR.txt)
if not MAC and (ROOT / "packaging" / "ocr" / "tesseract.exe").exists():
    datas.append((str(ROOT / "packaging" / "ocr"), "ocr"))
# Mac OCR (1.2): Apple's Vision text recognition, compiled from packaging/macos/studio-ocr.swift by build_mac.sh
if MAC and (ROOT / "packaging" / "macos" / "build" / "studio-ocr").exists():
    mac_binaries.append((str(ROOT / "packaging" / "macos" / "build" / "studio-ocr"), "ocr"))
binaries = collect_dynamic_libs("pypdfium2_raw") + mac_binaries
hidden = collect_submodules("uvicorn") + collect_submodules("studio") + collect_submodules("pypdf") + ["multipart", "python_multipart"]
hidden += collect_submodules("room_crypto") + collect_submodules("nacl") + collect_submodules("websockets")   # the Room (1.0.8)
hidden += collect_submodules("room_hub") + collect_submodules("jwt") + ["cryptography.hazmat.primitives.ciphers.aead"]  # hosting (1.1.0)
hidden += collect_submodules("pypdfium2") + collect_submodules("pypdfium2_raw") + ["PIL.JpegImagePlugin", "PIL.PngImagePlugin", "PIL.WebPImagePlugin"]
# Jon's agreement-builder scripts ship as data and are imported at run time, so PyInstaller cannot see their imports.
hidden += collect_submodules("lxml") + ["argparse", "collections", "copy", "decimal", "hashlib", "json", "zipfile"]
if sys.platform == "win32":            # the Mac uses its own window app (Contents/Helpers) and the browser, not pywebview
    hidden += collect_submodules("webview")
if MAC:
    hidden += collect_submodules("keyring")            # the Mac Keychain seals saved keys (studio.keys)

# rth_no_wmi runs first: Python's platform module can hang forever on a PC with a stuck WMI service (see the hook).
# setuptools is a build tool the app never uses; bundled, its start-up hook ran platform.system() and hung there.
a = Analysis([str(ROOT / "studio_launcher.py")], pathex=[str(ROOT / "engine")], datas=datas,
             binaries=binaries, hiddenimports=hidden, excludes=["tkinter", "pytest", "setuptools", "pkg_resources", "_distutils_hack"],
             runtime_hooks=[str(ROOT / "packaging" / "rth_no_wmi.py")], noarchive=False)
pyz = PYZ(a.pure)
# PyInstaller 6 treats the OCR folder's exe and DLLs as binaries and its dependency scan also puts a second copy of
# each DLL at the top of _internal: 1.0.6's first build carried them twice (332 MB unpacked). tesseract.exe loads its
# own copies beside it in ocr\, so only those are kept.
_ocr = str(ROOT / "packaging" / "ocr").lower()
a.binaries = [b for b in a.binaries if not str(b[1]).lower().startswith(_ocr) or str(b[0]).replace("\\", "/").startswith("ocr/")]
# Mac signing: MAC_SIGN_IDENTITY (a Developer ID Application certificate in the keychain) when the build has one;
# otherwise PyInstaller signs ad hoc, which runs on the build Mac and on test Macs after "Open Anyway".
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="SaracenBridgeStudio", upx=False,  # UPX raises AV false positives
          console=sys.platform not in ("win32", "darwin"),
          target_arch="arm64" if MAC else None,
          codesign_identity=(os.environ.get("MAC_SIGN_IDENTITY") or None) if MAC else None,
          entitlements_file=str(ROOT / "packaging" / "macos" / "entitlements.plist") if MAC else None,
          icon=(str(ROOT / "packaging" / "macos" / "studio.icns") if MAC
                else str(ROOT / "packaging" / "studio.ico") if (ROOT / "packaging" / "studio.ico").exists() else None))
coll = COLLECT(exe, a.binaries, a.datas, upx=False, name="SaracenBridgeStudio")
if MAC:
    MIC = "Saracen Bridge Studio uses the microphone for huddles and meetings in the Room."
    LAN = "Saracen Bridge Studio connects to the productions your team hosts on their computers."
    app = BUNDLE(coll, name="Saracen Bridge Studio.app", bundle_identifier="com.saracenbridge.studio",
                 icon=str(ROOT / "packaging" / "macos" / "studio.icns"), version=VERSION,
                 info_plist={
                     "CFBundleName": "Saracen Bridge Studio", "CFBundleDisplayName": "Saracen Bridge Studio",
                     "CFBundleShortVersionString": VERSION, "CFBundleVersion": VERSION,
                     "LSMinimumSystemVersion": "13.0", "NSHighResolutionCapable": True,
                     "LSApplicationCategoryType": "public.app-category.productivity",
                     # The launcher runs in the background; the window app inside it (Contents/Helpers, added by
                     # build_mac.sh) carries the Dock icon, the menus and Cmd-Q.
                     "LSUIElement": True,
                     "NSMicrophoneUsageDescription": MIC, "NSLocalNetworkUsageDescription": LAN,
                     "NSHumanReadableCopyright": "Saracen Bridge",
                 })
