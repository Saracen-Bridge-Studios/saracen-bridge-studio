import XCTest
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif
import FlyingFox
@testable import RoomCore

/// The relay against a stand-in hub and call server on this machine (FlyingFox), the same way the phone uses it.
final class RelayTests: XCTestCase {
    /// Ports nothing else here uses, in steps of ten so two tests never share one.
    func freePort() -> UInt16 { 40000 + 10 * UInt16.random(in: 0...499) }

    func makeHub(port: UInt16, callPort: UInt16) async throws -> HTTPServer {
        let hub = HTTPServer(address: try .inet(ip4: "127.0.0.1", port: port))
        await hub.appendRoute("GET /api/health") { _ in HTTPResponse(statusCode: .ok, body: Data(#"{"ok":true}"#.utf8)) }
        await hub.appendRoute("POST /api/echo") { req in
            let origin = req.headers[HTTPHeader("Origin")] ?? ""
            return HTTPResponse(statusCode: .ok, headers: [HTTPHeader("X-Seen-Origin"): origin], body: try await req.bodyData)
        }
        await hub.appendRoute("POST /api/meetings/m1/token") { _ in
            HTTPResponse(statusCode: .ok, body: Data(#"{"url":"ws://127.0.0.1:\#(callPort)","token":"tok","kind":"huddle"}"#.utf8))
        }
        await hub.appendRoute("GET /app/") { _ in HTTPResponse(statusCode: .ok, headers: [HTTPHeader("Content-Type"): "text/html"], body: Data("<h1>Room</h1>".utf8)) }
        await hub.appendRoute("GET /api/live", to: .webSocket(EchoWSMessageHandler()))
        await hub.appendRoute("GET /api/missing") { _ in HTTPResponse(statusCode: .notFound, body: Data(#"{"detail":"no"}"#.utf8)) }
        Task { try? await hub.run() }
        try await hub.waitUntilListening()
        return hub
    }

    func makeCallServer(port: UInt16) async throws -> HTTPServer {
        let call = HTTPServer(address: try .inet(ip4: "127.0.0.1", port: port))
        await call.appendRoute("GET /rtc", to: .webSocket(PrefixWS(prefix: "call:")))
        Task { try? await call.run() }
        try await call.waitUntilListening()
        return call
    }

    func testPagesRequestsSocketsAndCallsGoThroughTheRelay() async throws {
        let hubPort = freePort(), callPort = hubPort + 1, relayPort = hubPort + 2      // three apart from the other test's
        let hub = try await makeHub(port: hubPort, callPort: callPort)
        let call = try await makeCallServer(port: callPort)
        let host = RoomHost(id: "h", hub: URL(string: "http://127.0.0.1:\(hubPort)")!, name: "Test", port: relayPort, added: Date())
        let relay = RoomRelay(host: host)
        try await relay.start()
        try await relay.start()                                // again: already running, no error
        let base = host.relayBase
        let s = URLSession(configuration: .ephemeral)

        let (page, r1) = try await s.data(from: base.appendingPathComponent("app/"))
        XCTAssertEqual((r1 as? HTTPURLResponse)?.statusCode, 200)
        XCTAssertEqual(String(decoding: page, as: UTF8.self), "<h1>Room</h1>")

        var post = URLRequest(url: base.appendingPathComponent("api/echo"))
        post.httpMethod = "POST"
        post.httpBody = Data("hello".utf8)
        post.setValue("http://127.0.0.1:\(relayPort)", forHTTPHeaderField: "Origin")
        let (echo, r2) = try await s.data(for: post)
        XCTAssertEqual(String(decoding: echo, as: UTF8.self), "hello")
        XCTAssertEqual((r2 as? HTTPURLResponse)?.value(forHTTPHeaderField: "X-Seen-Origin"), "http://127.0.0.1:\(hubPort)")

        let (_, r3) = try await s.data(from: base.appendingPathComponent("api/missing"))
        XCTAssertEqual((r3 as? HTTPURLResponse)?.statusCode, 404)

        // the meeting token now names the relay, and the call's signalling reaches the real call server through it
        var tok = URLRequest(url: base.appendingPathComponent("api/meetings/m1/token"))
        tok.httpMethod = "POST"
        let (td, _) = try await s.data(for: tok)
        let obj = try JSONSerialization.jsonObject(with: td) as! [String: Any]
        XCTAssertEqual(obj["url"] as? String, "ws://127.0.0.1:\(relayPort)/livekit")
        XCTAssertEqual(obj["token"] as? String, "tok")
        let rtc = try await Upstream.connect(URL(string: "ws://127.0.0.1:\(relayPort)/livekit/rtc?access_token=tok")!, session: s)
        try await rtc.send(.text("join"))
        let reply = try await rtc.receive()
        XCTAssertEqual(reply, .text("call:join"))
        rtc.close()

        // the live link, text and binary, and a message larger than one frame
        let live = try await Upstream.connect(URL(string: "ws://127.0.0.1:\(relayPort)/api/live")!, session: s)
        try await live.send(.text("ping"))
        let pong = try await live.receive()
        XCTAssertEqual(pong, .text("ping"))
        let big = Data((0..<200_000).map { UInt8($0 % 251) })
        try await live.send(.data(big))
        let back = try await live.receive()
        XCTAssertEqual(back, .data(big))
        live.close()

        await relay.stop()
        await hub.stop()
        await call.stop()
    }

    func testAHostThatIsntThere() async throws {
        let relayPort = freePort()
        let host = RoomHost(id: "h", hub: URL(string: "http://127.0.0.1:9")!, name: "Gone", port: relayPort, added: Date())
        let relay = RoomRelay(host: host)
        try await relay.start()
        let reachable = await relay.reachable(timeout: 2)
        XCTAssertFalse(reachable)
        let (body, r) = try await URLSession(configuration: .ephemeral).data(from: host.relayBase.appendingPathComponent("api/sync"))
        XCTAssertEqual((r as? HTTPURLResponse)?.statusCode, 502)
        XCTAssertTrue(String(decoding: body, as: UTF8.self).contains("Can't reach this Studio"))
        await relay.stop()
    }

    func testRouting() {
        XCTAssertTrue(RelayHandler.isMeetingToken("/api/meetings/abc/token"))
        XCTAssertFalse(RelayHandler.isMeetingToken("/api/meetings/abc"))
        XCTAssertEqual(RelayHandler.join(URL(string: "http://h:8710")!, "/app/?x=1").absoluteString, "http://h:8710/app/?x=1")
        XCTAssertEqual(RelayHandler.wsURL(URL(string: "https://h:8710")!).absoluteString, "wss://h:8710")
        XCTAssertEqual(RelayHandler.defaultCallServer(for: URL(string: "http://192.168.1.20:8710")!).absoluteString, "ws://192.168.1.20:7880")
    }
}

struct PrefixWS: WSMessageHandler {
    let prefix: String
    func makeMessages(for client: AsyncStream<WSMessage>) async throws -> AsyncStream<WSMessage> {
        AsyncStream { c in
            Task {
                for await m in client {
                    if case .text(let s) = m { c.yield(.text(prefix + s)) }
                }
                c.finish()
            }
        }
    }
}
