"""Saracen Bridge Studio desktop launcher.

Starts the local engine server on 127.0.0.1 and shows the app. On Windows (0.3.4 on) that is an Edge app window
(`msedge --app=`: its own window, no tabs or address bar); on 13 Oct the embedded WebView2 window (pywebview, over
.NET) hung on Tim's PC without an error, so it is now opt-in with `--native`. If no window shows the page, the
default browser is tried, then a message box gives the address. `--headless` runs the server only (tests and CI);
`--browser` uses the default browser.

On Windows the native window is only tried when the WebView2 runtime is installed, and
pywebview is pinned to the Edge Chromium renderer: left to itself it falls back to the
legacy MSHTML (IE11) engine, which cannot run the UI and would show a blank window.

Never fail silently (13 Oct: on Tim's PC the engine started but the window never appeared and nothing said so):
- every start-up step is written to studio.log in the Studio data folder;
- if the window has not shown the page within WINDOW_LOAD_SECONDS, the Studio opens in the browser instead,
  writes where the window was stuck, and goes straight to the browser on later starts of the same version;
- any other start-up failure is shown in a message box, not just logged.
"""
from __future__ import annotations

import os
import sys
import time

if sys.platform == "win32":      # never wait on a stuck WMI service (see packaging/rth_no_wmi.py; frozen builds do this first)
    try:
        import platform as _platform
        _platform._wmi = None
    except Exception:  # noqa: BLE001
        pass


def _open_log():
    """The installed program always logs to studio.log in the Studio data folder (%APPDATA%\\SaracenStudio on
    Windows, ~/Library/Application Support/SaracenStudio on the Mac), written before anything else loads, so a
    start that stalls or is stopped early still leaves a trace (13 Oct: 0.3.3 left none on Tim's PC)."""
    if not getattr(sys, "frozen", False):
        return None, None
    try:
        if sys.platform == "darwin":
            folder = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "SaracenStudio")
        else:
            folder = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "SaracenStudio")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, "studio.log")
        f = open(path, "a", encoding="utf-8", buffering=1)
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}  Process {os.getpid()} started: {sys.executable} {' '.join(sys.argv[1:])}\n")
        f.flush()
        return f, path
    except OSError:
        return None, None


_LOG_FILE, LOG_PATH = _open_log()
# A windowed Windows build has no console: stdout/stderr are None, which breaks printing and logging.
if sys.stdout is None or sys.stderr is None:
    sys.stdout = sys.stderr = _LOG_FILE or open(os.devnull, "w", encoding="utf-8")

import argparse  # noqa: E402
import faulthandler  # noqa: E402
import socket  # noqa: E402
import threading  # noqa: E402
import traceback  # noqa: E402
import urllib.request  # noqa: E402
import webbrowser  # noqa: E402
from pathlib import Path  # noqa: E402

if not getattr(sys, "frozen", False):
    sys.path.insert(0, str(Path(__file__).resolve().parent / "engine"))

WINDOW_LOAD_SECONDS = 20          # a working window shows the page within a few seconds
STARTUP_DUMP_SECONDS = 90         # if start-up has not settled by then, write where every thread is waiting


def log(msg: str) -> None:
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {msg}"
    if _LOG_FILE is not None:
        try:
            _LOG_FILE.write(line + "\n")
            _LOG_FILE.flush()
        except (OSError, ValueError):
            pass
    if sys.stdout is not _LOG_FILE:
        try:
            print(line, flush=True)
        except (OSError, ValueError):
            pass


def tell_user(msg: str) -> None:
    """A message box (Windows) or alert (Mac), so a failure is never silent; the log gets the same text."""
    log(msg.replace("\n\n", " "))
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.user32.MessageBoxW(None, msg, "Saracen Bridge Studio", 0x10 | 0x40000)  # error icon, on top
        except Exception:  # noqa: BLE001
            pass
    elif sys.platform == "darwin":
        import subprocess
        try:                                     # the text goes in as an argument, never into the script itself
            subprocess.run(["osascript", "-e", "on run argv", "-e",
                            'display alert "Saracen Bridge Studio" message (item 1 of argv) as critical',
                            "-e", "end run", msg], timeout=600, capture_output=True)
        except (OSError, subprocess.SubprocessError):
            pass


DIRECT = urllib.request.build_opener(urllib.request.ProxyHandler({}))   # never send 127.0.0.1 through a system proxy


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def serve(port: int):
    import uvicorn
    from studio.server import app
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    for _ in range(300):
        try:
            DIRECT.open(f"http://127.0.0.1:{port}/api/health", timeout=1)
            return server
        except OSError:
            time.sleep(0.1)
    raise RuntimeError("The engine did not start within 30 seconds.")


WEBVIEW2_KEYS = [  # Microsoft: runtime present when pv exists and is not 0.0.0.0 under any of these
    ("HKEY_LOCAL_MACHINE", r"SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"),
    ("HKEY_LOCAL_MACHINE", r"SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"),
    ("HKEY_CURRENT_USER", r"Software\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"),
]


def webview2_installed() -> bool:
    if sys.platform != "win32":
        return True
    import winreg
    for hive, key in WEBVIEW2_KEYS:
        try:
            with winreg.OpenKey(getattr(winreg, hive), key) as k:
                pv, _ = winreg.QueryValueEx(k, "pv")
                if pv and pv != "0.0.0.0":
                    log(f"WebView2 runtime {pv} found")
                    return True
        except OSError:
            continue
    return False


# ---- remembering a window that does not work on this PC (per version, so a fixed release tries again)

def _marker() -> Path:
    from studio import store
    return store.home() / "window-failed.txt"


def _version() -> str:
    from studio.server import VERSION
    return VERSION


def window_failed_before() -> bool:
    try:
        return _marker().read_text(encoding="utf-8").strip() == _version()
    except OSError:
        return False


def remember_window_failed() -> None:
    try:
        _marker().write_text(_version(), encoding="utf-8")
    except OSError:
        pass


def forget_window_failed() -> None:
    try:
        _marker().unlink()
    except OSError:
        pass


def native_window(url: str, load_seconds: float = WINDOW_LOAD_SECONDS, on_stuck=None) -> bool:
    """Open the native window and block until it closes.

    False when the window could not be used, so the caller opens the browser. If the window has not shown the
    page within load_seconds, on_stuck() runs on a watchdog thread (the window call itself may never return)."""
    if not webview2_installed():
        log("WebView2 runtime not found: opening in the browser")
        return False
    loaded, finished = threading.Event(), threading.Event()
    try:
        log("Loading the window component")
        import webview  # pywebview
        window = webview.create_window("Saracen Bridge Studio", url, width=1440, height=900, min_size=(1024, 700))
        window.events.loaded += lambda: loaded.set()

        def watchdog():
            if loaded.wait(load_seconds):
                log("Window open")
                forget_window_failed()
                faulthandler.cancel_dump_traceback_later()
                return
            if finished.is_set():                # the window call already failed and the browser took over
                return
            log(f"The window did not show the page within {load_seconds:g} s. Where it is waiting:")
            try:
                faulthandler.dump_traceback(file=_LOG_FILE or sys.stderr, all_threads=True)
            except (AttributeError, ValueError, OSError):      # stderr without a file handle (tests)
                pass
            remember_window_failed()
            if on_stuck:
                on_stuck()

        threading.Thread(target=watchdog, name="window-watchdog", daemon=True).start()
        log("Opening the window")
        webview.start(gui="edgechromium" if sys.platform == "win32" else None)
    except Exception as e:  # noqa: BLE001 - any failure means: use the browser instead
        finished.set()
        log(f"Native window unavailable ({e.__class__.__name__}: {e}): opening in the browser")
        remember_window_failed()
        return False
    finished.set()
    if not loaded.is_set():
        log("The window closed before it showed the page: opening in the browser")
        remember_window_failed()
        return False
    return True


_BROWSER_ONCE = threading.Lock()
_browser_opened = False
IDLE_SECONDS = 150                # no check-in from the page for this long: the window was closed
PAGE_CONNECT_SECONDS = 25         # time for a window or browser tab to show the page and check in


def find_edge() -> str | None:
    """Microsoft Edge, which every Windows 10/11 PC has."""
    if sys.platform != "win32":
        return None
    import winreg
    for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
        try:
            with winreg.OpenKey(hive, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe") as k:
                path, _ = winreg.QueryValueEx(k, "")
                if path and Path(path).exists():
                    return path
        except OSError:
            continue
    for base in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles"), os.environ.get("LOCALAPPDATA")):
        if base and (Path(base) / "Microsoft" / "Edge" / "Application" / "msedge.exe").exists():
            return str(Path(base) / "Microsoft" / "Edge" / "Application" / "msedge.exe")
    return None


def open_app_window(url: str) -> bool:
    """The Studio in its own Edge app window: no tabs or address bar, and no .NET or WebView2 wrapper to hang."""
    edge = find_edge()
    if not edge:
        log("Microsoft Edge not found")
        return False
    import subprocess
    try:
        subprocess.Popen([edge, f"--app={url}", "--window-size=1440,900"], close_fds=True)
    except OSError as e:
        log(f"Microsoft Edge could not be started ({e})")
        return False
    log(f"Opening an Edge app window ({edge})")
    return True


SHELL_NAME = "studio-window.exe" if sys.platform == "win32" else "studio-window"
# On the Mac the window is its own small app inside the Studio's (Contents/Helpers), so it carries the Dock icon,
# the menu bar and Cmd-Q, while the launcher stays in the background (LSUIElement; packaging/macos).
MAC_WINDOW_APP = "Saracen Bridge Studio.app"


def find_shell() -> str | None:
    """The Studio's own window (0.4, Tauri): beside the launcher when installed; STUDIO_SHELL for tests."""
    cands = [os.environ.get("STUDIO_SHELL", "")]
    if getattr(sys, "frozen", False):
        here = os.path.dirname(sys.executable)
        if sys.platform == "darwin":
            cands.append(os.path.join(here, "..", "Helpers", MAC_WINDOW_APP, "Contents", "MacOS", SHELL_NAME))
        cands.append(os.path.join(here, SHELL_NAME))
    return next((p for p in (os.path.normpath(c) for c in cands if c) if os.path.isfile(p)), None)


def shell_window_until_closed(url: str, connect_seconds: float = PAGE_CONNECT_SECONDS) -> bool:
    """The Studio in its own window. True when the window showed the page and has now been closed; False when it
    never showed the page (no WebView2, blocked, crashed), so the caller falls back to the Edge app window."""
    import subprocess
    shell = find_shell()
    if not shell:
        return False
    try:
        flags = 0x08000000 if sys.platform == "win32" else 0          # CREATE_NO_WINDOW
        proc = subprocess.Popen([shell, "--url", url], close_fds=True, creationflags=flags)
    except OSError as e:
        log(f"The Studio window could not be started ({e})")
        return False
    log(f"Opening the Studio window ({shell})")
    end = time.time() + connect_seconds
    from studio import server as srv
    while time.time() < end and srv.last_heartbeat() is None and proc.poll() is None:
        time.sleep(0.25)
    if srv.last_heartbeat() is None:
        log(f"The Studio window did not show the page (exit code {proc.poll()}): falling back")
        try:
            proc.kill()
        except OSError:
            pass
        return False
    log("Studio window open")
    try:
        faulthandler.cancel_dump_traceback_later()
    except Exception:  # noqa: BLE001
        pass
    proc.wait()
    log(f"The Studio window was closed (exit code {proc.returncode})")
    return True


def open_default_browser(url: str) -> bool:
    opened = False
    if sys.platform == "win32":
        try:                                     # ShellExecute hands URLs to COM-based handlers; initialise COM first
            import ctypes
            ctypes.windll.ole32.CoInitializeEx(None, 0x2 | 0x4)   # apartment-threaded, no OLE1 DDE
        except Exception:  # noqa: BLE001
            pass
    try:
        opened = webbrowser.open(url)
    except Exception as e:  # noqa: BLE001
        log(f"The browser could not be opened ({e.__class__.__name__}: {e})")
    if not opened and sys.platform == "win32":
        import subprocess
        try:
            subprocess.Popen(["explorer.exe", url], close_fds=True)
            opened = True
        except OSError as e:
            log(f"The default browser could not be opened ({e})")
    log("Default browser asked to open the Studio" if opened else "No browser opened")
    return opened


def wait_for_page(seconds: float) -> bool:
    """True once the page has loaded and checked in: proof a window or tab really shows the Studio."""
    from studio import server as srv
    end = time.time() + seconds
    while time.time() < end:
        if srv.last_heartbeat() is not None:
            return True
        time.sleep(0.5)
    return srv.last_heartbeat() is not None


def wait_until_idle(idle_seconds: int = IDLE_SECONDS, first_contact_seconds: int = 600) -> None:
    """A window or tab gives no close event, so the engine stops itself once the page stops checking in."""
    from studio import server as srv
    started = time.time()
    try:
        while True:
            time.sleep(5)
            last = srv.last_heartbeat()
            if last is None and time.time() - started > first_contact_seconds:
                log("The page never connected: stopping")
                return
            if last is not None and time.time() - last > idle_seconds:
                log("The Studio window has been closed: stopping")
                return
    except KeyboardInterrupt:
        pass


def _claim_browser() -> bool:
    global _browser_opened
    with _BROWSER_ONCE:                          # the window watchdog and the main thread can both get here
        if _browser_opened:
            return False
        _browser_opened = True
        return True


def _say_where(url: str) -> None:
    threading.Thread(target=tell_user, daemon=True, args=(
        f"Saracen Bridge Studio is running, but no window could be opened.\n\nOpen this address in your web browser:\n{url}",)).start()


def browser_until_idle(url: str, idle_seconds: int = IDLE_SECONDS, first_contact_seconds: int = 600) -> None:
    """Default browser, then wait. Used by --browser, on Linux, and after the Studio window fails."""
    if not _claim_browser():
        return
    log(f"Opening in the browser: {url}")
    try:
        faulthandler.cancel_dump_traceback_later()
    except Exception:  # noqa: BLE001
        pass
    if not open_default_browser(url):
        _say_where(url)
    wait_until_idle(idle_seconds, first_contact_seconds)


def app_window_until_idle(url: str, connect_seconds: float = PAGE_CONNECT_SECONDS) -> None:
    """Windows default (0.3.4): an Edge app window; if it never shows the page, the default browser; if that
    fails too, a message box with the address. Each step is logged, and none can hang the Studio."""
    if not _claim_browser():
        return
    try:
        faulthandler.cancel_dump_traceback_later()
    except Exception:  # noqa: BLE001
        pass
    if open_app_window(url) and wait_for_page(connect_seconds):
        log("Studio window open")
    else:
        log(f"No Edge window showed the Studio within {connect_seconds:g} s: trying the default browser")
        if open_default_browser(url) and wait_for_page(connect_seconds):
            log("Studio open in the browser")
        else:
            log("The browser did not show the Studio either")
            _say_where(url)
    wait_until_idle()


def shutdown(server) -> None:
    from studio import jobs, llm
    jobs.stop_worker(timeout=2)   # a job cut short here resumes next time the Studio opens
    llm.BUNDLED.stop()
    server.should_exit = True


def main() -> None:
    import signal
    if hasattr(signal, "SIGTERM"):              # a polite kill runs the normal shutdown (stops the AI engine)
        signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    ap = argparse.ArgumentParser(description="Saracen Bridge Studio")
    ap.add_argument("--headless", action="store_true", help="run the engine server only")
    ap.add_argument("--port", type=int, default=0)
    ap.add_argument("--browser", action="store_true", help="open in the default browser")
    ap.add_argument("--native", action="store_true", help="try the embedded WebView2 window (before 0.3.4, the default)")
    ap.add_argument("--no-shell", action="store_true",
                    help="skip the Studio window and use an Edge app window (Windows) or the browser (Mac)")
    args = ap.parse_args()
    log(f"Starting Saracen Bridge Studio (process {os.getpid()}, {' '.join(sys.argv[1:]) or 'no options'})")
    port = args.port or free_port()
    log("Loading the engine")
    server = serve(port)
    from studio import jobs
    jobs.ensure_worker()          # resume any coverage queue left from the last session
    url = f"http://127.0.0.1:{port}/"
    log(f"Saracen Bridge Studio {_version()} running at {url}")
    if args.headless:
        faulthandler.cancel_dump_traceback_later()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    else:
        def stuck():                             # the window never appeared: carry on in the browser, then exit
            browser_until_idle(url)
            shutdown(server)
            log("Stopped")
            os._exit(0)                          # the window call is still blocked on the main thread

        if args.browser:
            browser_until_idle(url)
        elif sys.platform == "win32" and not args.native:
            if args.no_shell or not shell_window_until_closed(url):
                app_window_until_idle(url)
        elif sys.platform == "darwin" and not args.native:
            if args.no_shell or not shell_window_until_closed(url):
                browser_until_idle(url)
        else:
            use_window = not window_failed_before()
            if not use_window:
                log("The window did not work last time on this PC: opening in the browser")
            if not (use_window and native_window(url, on_stuck=stuck)):
                browser_until_idle(url)
    shutdown(server)
    log("Stopped")


def _run() -> None:
    try:
        out = _LOG_FILE or sys.stderr
        faulthandler.enable(file=out, all_threads=True)             # native crashes leave a traceback in the log
        faulthandler.dump_traceback_later(STARTUP_DUMP_SECONDS, exit=False, file=out)
    except (AttributeError, ValueError, OSError):
        pass
    try:
        main()
    except SystemExit:
        raise
    except BaseException as e:  # noqa: BLE001
        log("Start-up failed:\n" + traceback.format_exc())
        where = f"\n\nDetails: {LOG_PATH}" if LOG_PATH else ""
        tell_user(f"Saracen Bridge Studio could not start.\n\n{e.__class__.__name__}: {e}{where}")
        sys.exit(1)


if __name__ == "__main__":
    _run()
