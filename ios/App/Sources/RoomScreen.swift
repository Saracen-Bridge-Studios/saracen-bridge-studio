import SwiftUI
import WebKit
import SafariServices
import RoomCore

/// One Studio's Room: its relay started, the host checked, then the Room page (or a plain "can't reach" screen).
struct RoomScreen: View {
    @EnvironmentObject var model: AppModel
    let host: RoomHost
    let joinToken: String?
    var part: String? = nil
    @State private var state: Phase = .connecting

    enum Phase: Equatable { case connecting, ready, unreachable(String) }

    var body: some View {
        ZStack {
            Theme.ink.ignoresSafeArea()
            switch state {
            case .connecting:
                ProgressView("Connecting to \(host.name)…").tint(Theme.gold).foregroundStyle(Theme.muted)
            case .ready:
                RoomWebView(host: host, page: host.pageURL(join: joinToken, fragment: part),
                            onDeleted: { Task { @MainActor in model.accountDeleted(host) } })
                    .ignoresSafeArea(edges: .bottom)
            case .unreachable(let why):
                Unreachable(host: host, why: why) { Task { await connect() } }
            }
        }
        .navigationTitle(host.name)
        .navigationBarTitleDisplayMode(.inline)
        .toolbarBackground(Theme.ink, for: .navigationBar)
        .task { await connect() }
    }

    func connect() async {
        state = .connecting
        do {
            let relay = try await model.relay(for: host)
            state = await relay.reachable() ? .ready : .unreachable("")
        } catch {
            state = .unreachable(error.localizedDescription)
        }
    }
}

struct Unreachable: View {
    let host: RoomHost
    let why: String
    let retry: () -> Void

    var body: some View {
        VStack(spacing: 18) {
            Image(systemName: "wifi.exclamationmark").font(.system(size: 44)).foregroundStyle(Theme.gold)
            Text("Can't reach \(host.name)").font(.title3.weight(.semibold)).foregroundStyle(.white)
            VStack(alignment: .leading, spacing: 10) {
                Label("The Studio that hosts this production has to be open.", systemImage: "desktopcomputer")
                Label("This phone has to be on the same network (the office Wi-Fi), or on the production's private network.", systemImage: "wifi")
                Label("If iOS asked about finding devices on your network, allow it: Settings › Saracen Bridge › Local Network.", systemImage: "hand.raised")
            }
            .font(.callout).foregroundStyle(Theme.muted).padding(.horizontal, 26)
            if !why.isEmpty { Text(why).font(.caption).foregroundStyle(Theme.muted) }
            Button(action: retry) { Text("Try again").font(.headline).padding(.horizontal, 34).padding(.vertical, 14) }
                .buttonStyle(GoldButton())
                .accessibilityIdentifier("retry")
        }
    }
}

/// The Room page in WebKit, from the relay's loopback address: a secure context, so the microphone and the calls'
/// encryption work. The page's device key is kept in the Keychain through the `saracen` bridge.
struct RoomWebView: UIViewRepresentable {
    let host: RoomHost
    let page: URL
    var onDeleted: () -> Void = {}

    func makeCoordinator() -> Coordinator { Coordinator(host: host, onDeleted: onDeleted) }

    func makeUIView(context: Context) -> WKWebView {
        let cfg = WKWebViewConfiguration()
        cfg.websiteDataStore = .default()
        cfg.allowsInlineMediaPlayback = true
        cfg.mediaTypesRequiringUserActionForPlayback = []
        cfg.limitsNavigationsToAppBoundDomains = false
        let ucc = WKUserContentController()
        ucc.addScriptMessageHandler(context.coordinator, contentWorld: .page, name: "saracen")
        // tells the Room page it's inside the app (no "add to home screen", no web notifications)
        let info: [String: String] = ["platform": "ios",
                                      "version": Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "",
                                      "support": Company.supportEmail]       // the Room's terms and Contact show it
        let json = (try? JSONSerialization.data(withJSONObject: info)).flatMap { String(data: $0, encoding: .utf8) } ?? "{}"
        ucc.addUserScript(WKUserScript(source: "window.SaracenApp = \(json);", injectionTime: .atDocumentStart, forMainFrameOnly: true))
        cfg.userContentController = ucc
        let web = WKWebView(frame: .zero, configuration: cfg)
        web.isOpaque = false
        web.backgroundColor = UIColor(Theme.ink)
        web.scrollView.backgroundColor = UIColor(Theme.ink)
        web.scrollView.contentInsetAdjustmentBehavior = .never
        web.allowsBackForwardNavigationGestures = false
        web.uiDelegate = context.coordinator
        web.navigationDelegate = context.coordinator
        #if DEBUG
        web.isInspectable = true
        #endif
        context.coordinator.web = web
        web.load(URLRequest(url: page))
        return web
    }

    func updateUIView(_ web: WKWebView, context: Context) {}

    final class Coordinator: NSObject, WKUIDelegate, WKNavigationDelegate, WKScriptMessageHandlerWithReply, WKDownloadDelegate {
        let host: RoomHost
        let onDeleted: () -> Void
        weak var web: WKWebView?
        private var downloads: [ObjectIdentifier: URL] = [:]

        init(host: RoomHost, onDeleted: @escaping () -> Void) { self.host = host; self.onDeleted = onDeleted }

        private func isRoom(_ origin: WKSecurityOrigin) -> Bool {
            origin.host == "127.0.0.1" && origin.port == Int(host.port)
        }

        // the microphone, for the Room only; iOS still asks once for the app itself
        func webView(_ webView: WKWebView, requestMediaCapturePermissionFor origin: WKSecurityOrigin, initiatedByFrame frame: WKFrameInfo,
                     type: WKMediaCaptureType, decisionHandler: @escaping (WKPermissionDecision) -> Void) {
            decisionHandler(isRoom(origin) && type == .microphone ? .grant : .deny)
        }

        // the Room's own pages stay here; anything else (a link in a message) opens in Safari
        func webView(_ webView: WKWebView, decidePolicyFor action: WKNavigationAction, preferences: WKWebpagePreferences,
                     decisionHandler: @escaping (WKNavigationActionPolicy, WKWebpagePreferences) -> Void) {
            if action.shouldPerformDownload { return decisionHandler(.download, preferences) }
            guard let url = action.request.url else { return decisionHandler(.cancel, preferences) }
            if url.scheme == "blob" || url.scheme == "data" || url.scheme == "about" || (url.host == "127.0.0.1" && url.port == Int(host.port)) {
                return decisionHandler(.allow, preferences)
            }
            decisionHandler(.cancel, preferences)
            if ["http", "https", "mailto", "tel"].contains(url.scheme ?? "") { UIApplication.shared.open(url) }
        }

        func webView(_ webView: WKWebView, decidePolicyFor response: WKNavigationResponse, decisionHandler: @escaping (WKNavigationResponsePolicy) -> Void) {
            decisionHandler(response.canShowMIMEType ? .allow : .download)
        }

        func webView(_ webView: WKWebView, navigationAction: WKNavigationAction, didBecome download: WKDownload) { download.delegate = self }
        func webView(_ webView: WKWebView, navigationResponse: WKNavigationResponse, didBecome download: WKDownload) { download.delegate = self }

        // a file opened in the Room (decrypted on the phone) goes to the share sheet: Files, AirDrop, Mail
        func download(_ download: WKDownload, decideDestinationUsing response: URLResponse, suggestedFilename: String,
                      completionHandler: @escaping (URL?) -> Void) {
            let dir = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString, isDirectory: true)
            try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
            let url = dir.appendingPathComponent(suggestedFilename.isEmpty ? "file" : suggestedFilename)
            downloads[ObjectIdentifier(download)] = url
            completionHandler(url)
        }

        func downloadDidFinish(_ download: WKDownload) {
            guard let url = downloads.removeValue(forKey: ObjectIdentifier(download)) else { return }
            share([url])
        }

        func download(_ download: WKDownload, didFailWithError error: Error, resumeData: Data?) {
            downloads.removeValue(forKey: ObjectIdentifier(download))
        }

        private func share(_ items: [Any]) {
            guard let web, let root = web.window?.rootViewController else { return }
            let vc = UIActivityViewController(activityItems: items, applicationActivities: nil)
            vc.popoverPresentationController?.sourceView = web
            (root.presentedViewController ?? root).present(vc, animated: true)
        }

        func webView(_ webView: WKWebView, runJavaScriptAlertPanelWithMessage message: String, initiatedByFrame frame: WKFrameInfo,
                     completionHandler: @escaping () -> Void) {
            let alert = UIAlertController(title: nil, message: message, preferredStyle: .alert)
            alert.addAction(UIAlertAction(title: "OK", style: .default) { _ in completionHandler() })
            webView.window?.rootViewController?.present(alert, animated: true)
        }

        func webView(_ webView: WKWebView, runJavaScriptConfirmPanelWithMessage message: String, initiatedByFrame frame: WKFrameInfo,
                     completionHandler: @escaping (Bool) -> Void) {
            let alert = UIAlertController(title: nil, message: message, preferredStyle: .alert)
            alert.addAction(UIAlertAction(title: "Cancel", style: .cancel) { _ in completionHandler(false) })
            alert.addAction(UIAlertAction(title: "OK", style: .default) { _ in completionHandler(true) })
            webView.window?.rootViewController?.present(alert, animated: true)
        }

        /// The page's bridge: `await window.webkit.messageHandlers.saracen.postMessage({op, name, value})`.
        /// get / put / delete: this Studio's `device` key or Room `state` in the Keychain (this phone only, never
        /// backed up). haptic: a light tap. share: text to the share sheet. deleted: the account here was deleted.
        func userContentController(_ ucc: WKUserContentController, didReceive message: WKScriptMessage,
                                   replyHandler: @escaping (Any?, String?) -> Void) {
            guard isRoom(message.frameInfo.securityOrigin), let body = message.body as? [String: Any], let op = body["op"] as? String else {
                return replyHandler(nil, "not allowed")
            }
            let name = body["name"] as? String ?? ""
            let account = Keychain.account(host, name)
            switch op {
            case "get", "put", "delete":
                guard Keychain.names.contains(name) else { return replyHandler(nil, "unknown item") }
                if op == "get" { return replyHandler(Keychain.read(account: account), nil) }
                if op == "delete" { Keychain.delete(account: account); return replyHandler(true, nil) }
                guard let value = body["value"] as? String, !value.isEmpty, value.utf8.count <= 64 * 1024 else { return replyHandler(nil, "no value") }
                replyHandler(Keychain.write(value, account: account), nil)
            case "haptic":
                UIImpactFeedbackGenerator(style: .light).impactOccurred()
                replyHandler(true, nil)
            case "share":
                share([body["text"] as? String ?? ""])
                replyHandler(true, nil)
            case "deleted":                         // the person deleted their account in this Room
                replyHandler(true, nil)
                DispatchQueue.main.async { self.onDeleted() }
            default:
                replyHandler(nil, "unknown op")
            }
        }
    }
}
