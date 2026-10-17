# PyInstaller runtime hook: runs before anything else in the frozen app, including PyInstaller's own hooks.
#
# Python's platform module asks Windows Management Instrumentation (WMI) for the OS version and CPU. On a PC whose
# WMI service is stuck, that call never returns, and every caller hangs with it. 13 Oct 2026, Tim's PC (where the
# Windows Security app also opened blank): 0.3.3 hung at start-up inside setuptools' import-time platform.system(),
# and 0.3.2's window hung in pywebview's platform.machine(). With _wmi unset, platform falls back to
# sys.getwindowsversion() and the PROCESSOR_* environment variables, which never block.
import sys

if sys.platform == "win32":
    try:
        import platform
        platform._wmi = None
    except Exception:  # noqa: BLE001
        pass
