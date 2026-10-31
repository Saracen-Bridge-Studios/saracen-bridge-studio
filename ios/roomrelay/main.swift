import Foundation
import RoomCore

// roomrelay INVITE-OR-HUB-URL [PORT]: runs the iPhone app's relay on this computer, for testing the Room page through it.
let args = CommandLine.arguments
guard args.count >= 2, let invite = Invite.parse(args[1]) ?? URL(string: args[1]).map({ Invite(hub: $0, token: "") }) else {
    FileHandle.standardError.write(Data("usage: roomrelay INVITE-LINK-OR-HUB-URL [PORT]\n".utf8)); exit(2)
}
let port = args.count >= 3 ? UInt16(args[2]) ?? HostStore.firstPort : HostStore.firstPort
let host = RoomHost(id: HostStore.key(for: invite.hub), hub: invite.hub, name: "test", port: port, added: Date())
let relay = RoomRelay(host: host)
Task {
    do {
        try await relay.start()
        // straight to the pipe, unbuffered, so a test reading it sees the address at once
        let line = "relay on \(host.relayBase) for \(invite.hub)" + (invite.token.isEmpty ? "" : "; join at \(host.pageURL(join: invite.token))") + "\n"
        FileHandle.standardOutput.write(Data(line.utf8))
    } catch {
        print("couldn't start: \(error)"); exit(1)
    }
}
RunLoop.main.run()
