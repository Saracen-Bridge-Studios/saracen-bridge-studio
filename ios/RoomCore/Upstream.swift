import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif
import FlyingSocks

/// The relay's connection to a WebSocket on the host (the live link, or a call's signalling).
///
/// On the iPhone this is Apple's URLSessionWebSocketTask (ws and wss, any host name). Linux's Foundation can't do
/// WebSockets (its libcurl lacks them), so there a small RFC 6455 client over FlyingSocks stands in, plain ws only:
/// it lets the relay be tested here against the real Room hub and call server.
public enum UpstreamMessage: Sendable, Equatable {
    case text(String)
    case data(Data)
}

public protocol UpstreamSocket: Sendable {
    func send(_ message: UpstreamMessage) async throws
    func receive() async throws -> UpstreamMessage
    func close()
}

enum Upstream {
    static func connect(_ url: URL, session: URLSession) async throws -> any UpstreamSocket {
        #if canImport(FoundationNetworking)
        return try await PlainWebSocket.connect(url)
        #else
        let task = session.webSocketTask(with: url)
        task.maximumMessageSize = 16 * 1024 * 1024
        task.resume()
        return URLSessionUpstream(task: task)
        #endif
    }
}

#if !canImport(FoundationNetworking)
struct URLSessionUpstream: UpstreamSocket, @unchecked Sendable {
    let task: URLSessionWebSocketTask
    func send(_ message: UpstreamMessage) async throws {
        switch message {
        case .text(let s): try await task.send(.string(s))
        case .data(let d): try await task.send(.data(d))
        }
    }
    func receive() async throws -> UpstreamMessage {
        switch try await task.receive() {
        case .string(let s): return .text(s)
        case .data(let d): return .data(d)
        @unknown default: return .data(Data())
        }
    }
    func close() { task.cancel(with: .normalClosure, reason: nil) }
}
#endif

/// A plain (ws://) WebSocket client: the opening handshake, masked frames out, frames in (fragments joined, pings
/// answered). Enough for the relay's tests; the phone uses Apple's.
public final class PlainWebSocket: UpstreamSocket, @unchecked Sendable {
    let socket: AsyncSocket
    private let writeLock = AsyncLock()

    init(socket: AsyncSocket) { self.socket = socket }

    public static func connect(_ url: URL, timeout: TimeInterval = 5) async throws -> PlainWebSocket {
        guard url.scheme == "ws", let host = url.host else { throw PlainWebSocketError.unsupported(url.absoluteString) }
        let port = UInt16(url.port ?? 80)
        let socket = try await AsyncSocket.connected(to: try .inet(ip4: resolve(host), port: port), timeout: timeout)
        var key = [UInt8](repeating: 0, count: 16)
        for i in key.indices { key[i] = UInt8.random(in: 0...255) }
        var target = url.path.isEmpty ? "/" : url.path
        if let q = url.query { target += "?" + q }
        let hello = "GET \(target) HTTP/1.1\r\nHost: \(host):\(port)\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n" +
            "Sec-WebSocket-Key: \(Data(key).base64EncodedString())\r\nSec-WebSocket-Version: 13\r\n\r\n"
        try await socket.write(Data(hello.utf8))
        var head = [UInt8]()
        while !(head.count >= 4 && head.suffix(4) == [13, 10, 13, 10]) {
            head.append(try await socket.read())
            if head.count > 16384 { throw PlainWebSocketError.handshake("header too long") }
        }
        let status = String(decoding: head, as: UTF8.self).split(separator: "\r\n").first.map(String.init) ?? ""
        guard status.contains(" 101") else { try? socket.close(); throw PlainWebSocketError.handshake(status) }
        return PlainWebSocket(socket: socket)
    }

    static func resolve(_ host: String) throws -> String {
        if host.split(separator: ".").count == 4, host.allSatisfy({ $0.isNumber || $0 == "." }) { return host }
        if host == "localhost" { return "127.0.0.1" }
        var hints = addrinfo()
        hints.ai_family = AF_INET
        var res: UnsafeMutablePointer<addrinfo>?
        guard getaddrinfo(host, nil, &hints, &res) == 0, let first = res, let sa = first.pointee.ai_addr else {
            throw PlainWebSocketError.unsupported("can't resolve \(host)")
        }
        defer { freeaddrinfo(res) }
        var addr = sa.withMemoryRebound(to: sockaddr_in.self, capacity: 1) { $0.pointee.sin_addr }
        var buf = [CChar](repeating: 0, count: Int(INET_ADDRSTRLEN))
        inet_ntop(AF_INET, &addr, &buf, socklen_t(INET_ADDRSTRLEN))
        return String(cString: buf)
    }

    public func send(_ message: UpstreamMessage) async throws {
        switch message {
        case .text(let s): try await write(opcode: 0x1, Data(s.utf8))
        case .data(let d): try await write(opcode: 0x2, d)
        }
    }

    func write(opcode: UInt8, _ payload: Data) async throws {
        var frame = Data([0x80 | opcode])
        let n = payload.count
        if n < 126 {
            frame.append(0x80 | UInt8(n))
        } else if n <= 0xFFFF {
            frame.append(0x80 | 126)
            frame.append(contentsOf: [UInt8(n >> 8), UInt8(n & 0xFF)])
        } else {
            frame.append(0x80 | 127)
            frame.append(contentsOf: (0..<8).reversed().map { UInt8((UInt64(n) >> (UInt64($0) * 8)) & 0xFF) })
        }
        let mask = (0..<4).map { _ in UInt8.random(in: 0...255) }
        frame.append(contentsOf: mask)
        frame.append(contentsOf: payload.enumerated().map { $0.element ^ mask[$0.offset % 4] })
        let out = frame
        try await writeLock.withLock { try await self.socket.write(out) }
    }

    public func receive() async throws -> UpstreamMessage {
        var kind: UInt8 = 0
        var buffer = Data()
        while true {
            let h = try await socket.read(bytes: 2)
            let fin = h[0] & 0x80 != 0, opcode = h[0] & 0x0F, masked = h[1] & 0x80 != 0
            var len = Int(h[1] & 0x7F)
            if len == 126 {
                let b = try await socket.read(bytes: 2); len = Int(b[0]) << 8 | Int(b[1])
            } else if len == 127 {
                let b = try await socket.read(bytes: 8); len = b.reduce(0) { $0 << 8 | Int($1) }
            }
            let mask = masked ? try await socket.read(bytes: 4) : []
            var payload = len > 0 ? try await socket.read(bytes: len) : []
            if masked { for i in payload.indices { payload[i] ^= mask[i % 4] } }
            switch opcode {
            case 0x8:
                throw PlainWebSocketError.closed
            case 0x9:
                try await write(opcode: 0xA, Data(payload))
                continue
            case 0xA:
                continue
            case 0x0:
                buffer.append(contentsOf: payload)
            default:
                kind = opcode
                buffer = Data(payload)
            }
            if fin { return kind == 0x1 ? .text(String(decoding: buffer, as: UTF8.self)) : .data(buffer) }
        }
    }

    public func close() {
        Task { try? await self.write(opcode: 0x8, Data([0x03, 0xE8])); try? self.socket.close() }
    }
}

public enum PlainWebSocketError: Error {
    case unsupported(String)
    case handshake(String)
    case closed
}

/// Serialises frame writes on one socket.
actor AsyncLock {
    private var busy = false
    private var waiters: [CheckedContinuation<Void, Never>] = []

    func withLock<T: Sendable>(_ body: @Sendable () async throws -> T) async throws -> T {
        while busy { await withCheckedContinuation { waiters.append($0) } }
        busy = true
        defer {
            busy = false
            if !waiters.isEmpty { waiters.removeFirst().resume() }
        }
        return try await body()
    }
}
