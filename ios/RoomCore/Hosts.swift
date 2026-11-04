import Foundation

/// A Studio that hosts productions this phone is in (Jon's on Jon's computer, Colin's on Colin's).
///
/// Each host gets its own loopback port for the relay, kept for good: the Room page's storage belongs to its origin
/// (`http://127.0.0.1:PORT`), so a host must always come back on the same port, and two hosts never share one.
public struct RoomHost: Codable, Hashable, Identifiable, Sendable {
    public var id: String
    public var hub: URL
    public var name: String
    public var port: UInt16
    public var added: Date

    public init(id: String, hub: URL, name: String, port: UInt16, added: Date) {
        self.id = id
        self.hub = hub
        self.name = name
        self.port = port
        self.added = added
    }

    public var relayBase: URL { URL(string: "http://127.0.0.1:\(port)")! }

    /// Where the Room page opens through the relay: the app's start page, the join screen for an invite, or a part of
    /// the page named by `fragment` (such as `delete-account`, from the app's Settings).
    public func pageURL(join token: String? = nil, fragment: String? = nil) -> URL {
        if let token { return URL(string: "http://127.0.0.1:\(port)/app/#join=\(token)")! }
        if let fragment, !fragment.isEmpty { return URL(string: "http://127.0.0.1:\(port)/app/#\(fragment)")! }
        return URL(string: "http://127.0.0.1:\(port)/app/")!
    }
}

/// The hosts on this phone, saved as JSON in the app's own folder (no secrets: device keys live in the Keychain).
public final class HostStore: @unchecked Sendable {
    public static let firstPort: UInt16 = 47380
    public static let lastPort: UInt16 = 47479

    private let file: URL
    private let lock = NSLock()
    private var saved: [RoomHost]

    public init(file: URL) {
        self.file = file
        if let data = try? Data(contentsOf: file),
           let list = try? JSONDecoder.iso.decode([RoomHost].self, from: data) {
            saved = list
        } else {
            saved = []
        }
    }

    public var hosts: [RoomHost] {
        lock.lock(); defer { lock.unlock() }
        return saved
    }

    /// The host for an invite: the one already saved for that address, or a new one on the next free port.
    @discardableResult
    public func add(_ invite: Invite, name: String? = nil, now: Date = Date()) throws -> RoomHost {
        lock.lock(); defer { lock.unlock() }
        let key = Self.key(for: invite.hub)
        if let had = saved.first(where: { $0.id == key }) { return had }
        let used = Set(saved.map(\.port))
        guard let port = (Self.firstPort...Self.lastPort).first(where: { !used.contains($0) }) else {
            throw HostStoreError.full
        }
        let host = RoomHost(id: key, hub: invite.hub, name: name ?? invite.hub.host ?? "Studio", port: port,
                            added: Date(timeIntervalSince1970: (now.timeIntervalSince1970).rounded(.down)))   // whole seconds, as saved
        saved.append(host)
        try write()
        return host
    }

    public func rename(_ id: String, to name: String) throws {
        lock.lock(); defer { lock.unlock() }
        guard let i = saved.firstIndex(where: { $0.id == id }) else { return }
        saved[i].name = name.trimmingCharacters(in: .whitespacesAndNewlines)
        try write()
    }

    /// The host's address changed (a new network address after a re-invite): same host, same port, so its Room
    /// page keeps its storage.
    public func move(_ id: String, to hub: URL) throws {
        lock.lock(); defer { lock.unlock() }
        guard let i = saved.firstIndex(where: { $0.id == id }) else { return }
        saved[i].hub = hub
        try write()
    }

    public func remove(_ id: String) throws {
        lock.lock(); defer { lock.unlock() }
        saved.removeAll { $0.id == id }
        try write()
    }

    /// One id per address: scheme, host and port, lowercased.
    public static func key(for hub: URL) -> String {
        "\(hub.scheme?.lowercased() ?? "http")://\(hub.host?.lowercased() ?? ""):\(hub.port ?? (hub.scheme == "https" ? 443 : 80))"
    }

    private func write() throws {
        try FileManager.default.createDirectory(at: file.deletingLastPathComponent(), withIntermediateDirectories: true)
        try JSONEncoder.iso.encode(saved).write(to: file, options: .atomic)
    }
}

public enum HostStoreError: Error, LocalizedError {
    case full
    public var errorDescription: String? { "This phone already has 100 Studios. Remove one first." }
}

extension JSONDecoder {
    static var iso: JSONDecoder { let d = JSONDecoder(); d.dateDecodingStrategy = .iso8601; return d }
}

extension JSONEncoder {
    static var iso: JSONEncoder { let e = JSONEncoder(); e.dateEncodingStrategy = .iso8601; e.outputFormatting = [.sortedKeys]; return e }
}
