import SwiftUI
import RoomCore

/// Saracen Bridge for iPhone: the team companion. The Room of every production this phone is in (board, chat, call
/// sheets, encrypted huddles and meetings), from each host's Studio. Nothing runs on the phone but the Room page and
/// the relay that gives it a secure address; the AI and the Studio's tools stay on the host.
@main
struct SaracenBridgeApp: App {
    @StateObject private var model = AppModel()
    @Environment(\.scenePhase) private var phase

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(model)
                .onOpenURL { model.open($0) }
                .tint(Theme.gold)
                .preferredColorScheme(.dark)
        }
        .onChange(of: phase) { _, now in model.phaseChanged(now) }
    }
}

enum Theme {
    static let gold = Color(red: 0.776, green: 0.604, blue: 0.227)          // #C69A3A, the software's gold
    static let ink = Color(red: 0.035, green: 0.027, blue: 0.055)
    static let card = Color(red: 0.09, green: 0.075, blue: 0.13)
    static let plum = Color(red: 0.22, green: 0.157, blue: 0.263)           // #382843, the logo's purple
    static let muted = Color.white.opacity(0.62)
}

/// The phone's Studios, their relays, the invite being joined, and the lock.
@MainActor
final class AppModel: ObservableObject {
    @Published private(set) var hosts: [RoomHost] = []
    @Published var open: RoomHost?
    @Published var joinToken: String?
    @Published var locked = false
    @Published var notice: String?
    @Published var lockWithFaceID = UserDefaults.standard.bool(forKey: "lockWithFaceID") {
        didSet { UserDefaults.standard.set(lockWithFaceID, forKey: "lockWithFaceID") }
    }

    let store: HostStore
    private var relays: [String: RoomRelay] = [:]

    init() {
        let dir = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
        let file = dir.appendingPathComponent("SaracenBridge/hosts.json")
        if ProcessInfo.processInfo.arguments.contains("-uitestReset") { try? FileManager.default.removeItem(at: file) }   // UI tests start clean
        store = HostStore(file: file)
        hosts = store.hosts
        locked = lockWithFaceID
    }

    /// A `saracenbridge://join?invite=…` link from the invite page in Safari, or an http invite link.
    func open(_ url: URL) {
        guard let invite = Invite.parse(url.absoluteString) else {
            notice = "That link isn't an invite to a Room."
            return
        }
        join(invite)
    }

    func join(_ invite: Invite) {
        do {
            let host = try store.add(invite)
            hosts = store.hosts
            joinToken = invite.token
            open = host
        } catch {
            notice = error.localizedDescription
        }
    }

    func rename(_ host: RoomHost, _ name: String) {
        try? store.rename(host.id, to: name)
        hosts = store.hosts
    }

    func remove(_ host: RoomHost) {
        Task { await relays[host.id]?.stop() }
        relays[host.id] = nil
        for name in Keychain.names { Keychain.delete(account: Keychain.account(host, name)) }
        try? store.remove(host.id)
        hosts = store.hosts
    }

    /// The host's relay, started (again, after the app was in the background).
    func relay(for host: RoomHost) async throws -> RoomRelay {
        let r = relays[host.id] ?? RoomRelay(host: host)
        relays[host.id] = r
        try await r.start()
        return r
    }

    func phaseChanged(_ phase: ScenePhase) {
        switch phase {
        case .background:
            if lockWithFaceID { locked = true }
        case .active:
            if let host = open { Task { _ = try? await relay(for: host) } }
        default:
            break
        }
    }
}
