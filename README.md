# Saracen Bridge Studio

A standalone production tool: open any section on its own (coverage, scheduling, incentives, BFI, sales, brands, finance,
greenlight, term sheets), or launch Aiden (storyboard) and FRAT (visual feedback). No ChatGPT, no cloud.

Run it from source (Python 3.13+):

    pip install -r requirements.txt
    python studio_launcher.py            # opens the window; --headless --port 8798 for server only

Build the Windows installer (on Windows): `.\packaging\build_windows.ps1`


Run the tests (Python 3, pytest, openpyxl, lxml):

    python3 -m pytest -q

Rebuild from sources (needs LibreOffice for recalculation):

    python3 scripts/build_library.py <extracted-bundles-dir> .
    python3 scripts/load_reference.py . <recalculated-workbooks-dir>
    python3 scripts/load_controlled.py .

See docs/ARCHITECTURE.md and tools/registry.json.
