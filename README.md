# Saracen Bridge Studio

A standalone production tool: open any section on its own (coverage, scheduling, incentives, BFI, sales, brands, finance,
greenlight, term sheets), or launch Aiden (storyboard) and FRAT (visual feedback). No ChatGPT, no cloud.

Run it from source (Python 3.13+):

    pip install -r requirements.txt
    python studio_launcher.py            # opens the window; --headless --port 8798 for server only

Build the Windows installer: on Linux with Wine, `bash packaging/build_windows_on_linux.sh`; on Windows,
`.\packaging\build_windows.ps1`.

Build the Mac app and disk image (on an Apple Silicon Mac): `bash packaging/build_mac.sh`. GitHub builds and
smoke-tests it on one of its Macs on every push to main, and runs the tests on Windows (`.github/workflows/build.yml`).


Run the tests (Python 3, pytest, openpyxl, lxml):

    python3 -m pytest -q

Rebuild from sources (needs LibreOffice for recalculation):

    python3 scripts/build_library.py <extracted-bundles-dir> .
    python3 scripts/load_reference.py . <recalculated-workbooks-dir>
    python3 scripts/load_controlled.py .

See docs/ARCHITECTURE.md and tools/registry.json.
