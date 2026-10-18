//! Saracen Bridge Studio's window (0.4). The Python launcher starts the local engine, then runs this with
//! `--url http://127.0.0.1:<port>/`. Closing the window ends this process; the launcher then stops the engine.
//! Native title bar (keeps Windows 11 Snap Layouts), coloured to the house style through DWM. On the Mac it runs as
//! a small app inside the Studio's bundle (Contents/Helpers), with the dark title bar and Tauri's standard menus.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{WebviewUrl, WebviewWindowBuilder};

fn arg(name: &str) -> Option<String> {
    let mut it = std::env::args().skip(1);
    while let Some(a) = it.next() {
        if a == name {
            return it.next();
        }
        if let Some(v) = a.strip_prefix(&format!("{name}=")) {
            return Some(v.to_string());
        }
    }
    None
}

fn is_studio(u: &url::Url) -> bool {
    matches!(u.scheme(), "http") && matches!(u.host_str(), Some("127.0.0.1") | Some("localhost"))
}

fn open_outside(u: &url::Url) {
    if !matches!(u.scheme(), "http" | "https" | "mailto") {
        return;
    }
    #[cfg(windows)]
    {
        use std::os::windows::process::CommandExt;
        let _ = std::process::Command::new("rundll32")
            .args(["url.dll,FileProtocolHandler", u.as_str()])
            .creation_flags(0x0800_0000) // CREATE_NO_WINDOW
            .spawn();
    }
    #[cfg(target_os = "macos")]
    {
        let _ = std::process::Command::new("open").arg(u.as_str()).spawn();
    }
    #[cfg(all(not(windows), not(target_os = "macos")))]
    {
        let _ = std::process::Command::new("xdg-open").arg(u.as_str()).spawn();
    }
}

#[cfg(windows)]
fn house_title_bar(hwnd: isize) {
    #[link(name = "dwmapi")]
    extern "system" {
        fn DwmSetWindowAttribute(hwnd: isize, attr: u32, value: *const core::ffi::c_void, size: u32) -> i32;
    }
    // COLORREF is 0x00BBGGRR. Caption #0b0812 (ink), title text #f2c04d (gold), border #2d203e. Windows 11 only;
    // Windows 10 ignores these and keeps the dark title bar from the theme.
    let set = |attr: u32, v: u32| unsafe { DwmSetWindowAttribute(hwnd, attr, &v as *const u32 as *const _, 4) };
    let dark: u32 = 1;
    unsafe { DwmSetWindowAttribute(hwnd, 20, &dark as *const u32 as *const _, 4) }; // DWMWA_USE_IMMERSIVE_DARK_MODE
    set(35, 0x0012_080b); // DWMWA_CAPTION_COLOR
    set(36, 0x004d_c0f2); // DWMWA_TEXT_COLOR
    set(34, 0x003e_202d); // DWMWA_BORDER_COLOR
}

fn main() {
    let url: url::Url = arg("--url")
        .and_then(|u| u.parse().ok())
        .filter(is_studio)
        .unwrap_or_else(|| "http://127.0.0.1:8798/".parse().unwrap());
    let maximized = arg("--maximized").is_some();

    tauri::Builder::default()
        .setup(move |app| {
            let w = WebviewWindowBuilder::new(app, "main", WebviewUrl::External(url.clone()))
                .title("Saracen Bridge Studio")
                .inner_size(1440.0, 900.0)
                .min_inner_size(1024.0, 660.0)
                .center()
                .maximized(maximized)
                .theme(Some(tauri::Theme::Dark))
                .background_color(tauri::webview::Color(7, 5, 11, 255))
                .disable_drag_drop_handler() // the page takes dropped scripts itself
                .on_navigation(|u| {
                    if is_studio(u) {
                        true
                    } else {
                        open_outside(u);
                        false
                    }
                })
                .build()?;
            #[cfg(windows)]
            if let Ok(h) = w.hwnd() {
                house_title_bar(h.0 as isize);
            }
            // The Mac launcher runs in the background and starts this window app directly, so the window asks to
            // come to the front itself (otherwise it can open behind whatever the user was using).
            #[cfg(target_os = "macos")]
            {
                app.set_activation_policy(tauri::ActivationPolicy::Regular);
                let _ = w.set_focus();
            }
            let _ = w;
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("Saracen Bridge Studio window failed");
}
