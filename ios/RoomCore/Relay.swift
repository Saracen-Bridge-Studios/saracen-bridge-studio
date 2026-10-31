import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif
import FlyingFox

/// The loopback relay: the Room page on the phone is served from `http://127.0.0.1:PORT`, a secure context, and every
/// request (HTTP and WebSocket) is passed to the host's Room on the network.
///
/// Why (Rule 1, 30 Oct 2026): a page opened straight from the host's plain network address is not a secure context, so
/// the phone can't use the microphone or encrypt calls (S-90). Loopback is a secure context in WebKit, and the app's
/// own network requests to the host are allowed by App Transport Security's local-networking exception
/// (NSAllowsLocalNetworking, needed for IP addresses from iOS 17).
///
/// Calls: the hub's meeting token names the host's call server (`ws://HOST:7880`). The relay rewrites it to its own
/// `ws://127.0.0.1:PORT/livekit` and passes the call's signalling through; the encrypted audio itself goes straight to
/// the host's call server over UDP, as on any phone.
public final class RoomRelay: @unchecked Sendable {
    public let host: RoomHost
    private let session: URLSession
    private let state = RelayState()
    private var server: HTTPServer?
    private var task: Task<Void, Never>?

    public var verbose = false

    public init(host: RoomHost, session: URLSession? = nil) {
        self.host = host
        let cfg = URLSessionConfiguration.ephemeral
        cfg.timeoutIntervalForRequest = 60                     // a 4 MB encrypted file chunk on a slow network
        cfg.requestCachePolicy = .reloadIgnoringLocalCacheData
        cfg.httpShouldSetCookies = false
        self.session = session ?? URLSession(configuration: cfg)
    }

    /// Start listening on 127.0.0.1 only. Safe to call again after the app comes back from the background.
    public func start() async throws {
        if let server, await server.isListening { return }
        let handler = RelayHandler(host: host, session: session, state: state)
        let srv = HTTPServer(address: try .inet(ip4: "127.0.0.1", port: host.port), timeout: 120,
                             logger: verbose ? HTTPServer.defaultLogger() : .disabled, handler: handler)
        server = srv
        task = Task { try? await srv.run() }
        try await srv.waitUntilListening(timeout: 5)
    }

    public func stop() async {
        await server?.stop(timeout: 1)
        task?.cancel()
        server = nil
        task = nil
    }

    /// Whether the host's Room answers (for the "can't reach" screen).
    public func reachable(timeout: TimeInterval = 4) async -> Bool {
        var req = URLRequest(url: host.hub.appendingPathComponent("api/health"))
        req.timeoutInterval = timeout
        guard let (_, resp) = try? await session.data(for: req) else { return false }
        return (resp as? HTTPURLResponse)?.statusCode == 200
    }
}

/// What the relay learns while running: the host's call server, from the meeting tokens it passes.
actor RelayState {
    var callServer: URL?
    func setCallServer(_ url: URL) { callServer = url }
}

struct RelayHandler: HTTPHandler {
    let host: RoomHost
    let session: URLSession
    let state: RelayState

    static let hopByHop: Set<String> = ["host", "connection", "keep-alive", "transfer-encoding", "content-length", "upgrade",
                                        "proxy-connection", "te", "trailer", "accept-encoding", "sec-websocket-key",
                                        "sec-websocket-version", "sec-websocket-extensions", "sec-websocket-accept"]
    static let dropFromResponse: Set<String> = ["connection", "keep-alive", "transfer-encoding", "content-length",
                                                "content-encoding", "upgrade"]

    func handleRequest(_ request: HTTPRequest) async throws -> HTTPResponse {
        let target = request.target.rawValue
        let isSocket = request.headers[HTTPHeader("Upgrade")]?.lowercased() == "websocket"
        if target.hasPrefix("/livekit") {
            let rest = String(target.dropFirst("/livekit".count))
            let base = await state.callServer ?? Self.defaultCallServer(for: host.hub)
            if isSocket {
                return try await WebSocketHTTPHandler(handler: MessageFrameWSHandler(handler: WSRelay(upstream: Self.join(base, rest), session: session)))
                    .handleRequest(request)
            }
            return try await forward(request, to: Self.join(Self.httpURL(base), rest))
        }
        if isSocket {
            return try await WebSocketHTTPHandler(handler: MessageFrameWSHandler(handler: WSRelay(upstream: Self.join(Self.wsURL(host.hub), target), session: session)))
                .handleRequest(request)
        }
        var resp = try await forward(request, to: Self.join(host.hub, target))
        if request.method == .POST, Self.isMeetingToken(request.path), resp.statusCode.code == 200 {
            resp = await rewriteToken(resp)
        }
        return resp
    }

    /// Pass one HTTP request to the host and its answer back. The page's Origin is replaced with the host's own, as if
    /// the page had come from the host, which it did, through the relay.
    func forward(_ request: HTTPRequest, to url: URL) async throws -> HTTPResponse {
        var req = URLRequest(url: url)
        req.httpMethod = request.method.rawValue
        let body = try await request.bodyData
        if !body.isEmpty || [.POST, .PUT, .PATCH].contains(request.method) { req.httpBody = body }
        for (name, value) in request.headers where !Self.hopByHop.contains(name.rawValue.lowercased()) {
            if name.rawValue.lowercased() == "origin" {
                req.setValue(Self.origin(of: host.hub), forHTTPHeaderField: "Origin")
            } else if name.rawValue.lowercased() == "referer" {
                continue
            } else {
                req.addValue(value, forHTTPHeaderField: name.rawValue)
            }
        }
        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await session.data(for: req)
        } catch {
            return HTTPResponse(statusCode: HTTPStatusCode(502, phrase: "Bad Gateway"),
                                headers: [HTTPHeader("Content-Type"): "application/json"],
                                body: Data(#"{"detail":"Can't reach this Studio. Is it open, and is this phone on the same network?"}"#.utf8))
        }
        guard let http = response as? HTTPURLResponse else { throw URLError(.badServerResponse) }
        var headers = HTTPHeaders()
        for (k, v) in http.allHeaderFields {
            guard let name = k as? String, let value = v as? String, !Self.dropFromResponse.contains(name.lowercased()) else { continue }
            headers.addValue(value, for: HTTPHeader(name))
        }
        return HTTPResponse(statusCode: HTTPStatusCode(http.statusCode, phrase: HTTPURLResponse.localizedString(forStatusCode: http.statusCode)),
                            headers: headers, body: data)
    }

    /// The meeting token's call-server address, pointed at the relay; the real one is kept for the relay's own use.
    func rewriteToken(_ resp: HTTPResponse) async -> HTTPResponse {
        guard let body = try? await resp.bodyData else { return resp }
        guard var obj = (try? JSONSerialization.jsonObject(with: body)) as? [String: Any],
              let raw = obj["url"] as? String, let upstream = URL(string: raw) else { return resp }
        await state.setCallServer(upstream)
        obj["url"] = "ws://127.0.0.1:\(host.port)/livekit"
        guard let data = try? JSONSerialization.data(withJSONObject: obj) else { return resp }
        var out = resp
        out.payload = .httpBody(HTTPBodySequence(data: data))
        return out
    }

    static func isMeetingToken(_ path: String) -> Bool {
        let parts = path.split(separator: "/")
        return parts.count == 4 && parts[0] == "api" && parts[1] == "meetings" && parts[3] == "token"
    }

    static func join(_ base: URL, _ target: String) -> URL {
        var s = base.absoluteString
        while s.hasSuffix("/") { s.removeLast() }
        let t = target.isEmpty ? "/" : (target.hasPrefix("/") || target.hasPrefix("?") ? target : "/" + target)
        return URL(string: s + t)!
    }

    static func origin(of url: URL) -> String {
        "\(url.scheme ?? "http")://\(url.host ?? "")" + (url.port.map { ":\($0)" } ?? "")
    }

    static func wsURL(_ url: URL) -> URL {
        var c = URLComponents(url: url, resolvingAgainstBaseURL: false)!
        c.scheme = url.scheme == "https" ? "wss" : "ws"
        return c.url!
    }

    static func httpURL(_ url: URL) -> URL {
        var c = URLComponents(url: url, resolvingAgainstBaseURL: false)!
        c.scheme = url.scheme == "wss" ? "https" : (url.scheme == "ws" ? "http" : url.scheme)
        return c.url!
    }

    /// Before any token has been seen: the call server bundled with the Studio, on the host, port 7880.
    static func defaultCallServer(for hub: URL) -> URL {
        URL(string: "\(hub.scheme == "https" ? "wss" : "ws")://\(hub.host ?? "127.0.0.1"):7880")!
    }
}

/// One WebSocket passed through: the page's messages to the host, the host's back to the page, until either closes.
struct WSRelay: WSMessageHandler {
    let upstream: URL
    let session: URLSession

    func makeMessages(for client: AsyncStream<WSMessage>) async throws -> AsyncStream<WSMessage> {
        let socket = try await Upstream.connect(upstream, session: session)
        Task {
            for await message in client {
                switch message {
                case .text(let s): try? await socket.send(.text(s))
                case .data(let d): try? await socket.send(.data(d))
                case .close: socket.close(); return
                }
            }
            socket.close()
        }
        return AsyncStream { continuation in
            let reader = Task {
                while !Task.isCancelled {
                    do {
                        switch try await socket.receive() {
                        case .text(let s): continuation.yield(.text(s))
                        case .data(let d): continuation.yield(.data(d))
                        }
                    } catch {
                        continuation.yield(.close(.goingAway))
                        break
                    }
                }
                continuation.finish()
            }
            continuation.onTermination = { _ in reader.cancel(); socket.close() }
        }
    }
}
