import XCTest
@testable import RoomCore

final class InviteTests: XCTestCase {
    func testLinksTheStudioSends() {
        let i = Invite.parse("http://192.168.1.20:8710/app/#join=abc_DEF-123")
        XCTAssertEqual(i?.hub.absoluteString, "http://192.168.1.20:8710")
        XCTAssertEqual(i?.token, "abc_DEF-123")
        XCTAssertEqual(Invite.parse("https://room.example:8710/app/?join=T0k")?.token, "T0k")
        XCTAssertEqual(Invite.parse("http://10.0.0.5:8710/app/#join=xyz")?.hub.port, 8710)
    }

    func testAPastedMessageAndTheAppLink() {
        let msg = "Hi Tim, here's your invite:\n http://192.168.1.20:8710/app/#join=tok123 \nSee you Monday"
        XCTAssertEqual(Invite.parse(msg)?.token, "tok123")
        let inner = "http://192.168.1.20:8710/app/#join=tok123".addingPercentEncoding(withAllowedCharacters: .alphanumerics)!
        XCTAssertEqual(Invite.parse("saracenbridge://join?invite=\(inner)"), Invite.parse(msg))
    }

    func testNotInvites() {
        XCTAssertNil(Invite.parse(""))
        XCTAssertNil(Invite.parse("http://192.168.1.20:8710/app/"))                  // no token
        XCTAssertNil(Invite.parse("http://192.168.1.20:8710/app/#join=<script>"))     // not a token
        XCTAssertNil(Invite.parse("ftp://192.168.1.20/app/#join=abc"))
        XCTAssertNil(Invite.parse("saracenbridge://join"))
    }
}

final class HostStoreTests: XCTestCase {
    func file() -> URL { FileManager.default.temporaryDirectory.appendingPathComponent("hosts-\(UUID().uuidString)/hosts.json") }

    func testEachHostKeepsItsOwnPortForGood() throws {
        let f = file()
        let store = HostStore(file: f)
        let jon = try store.add(Invite.parse("http://192.168.1.20:8710/app/#join=a")!, name: "Jon's Studio")
        let colin = try store.add(Invite.parse("http://192.168.1.30:8710/app/#join=b")!)
        XCTAssertEqual(jon.port, HostStore.firstPort)
        XCTAssertEqual(colin.port, HostStore.firstPort + 1)
        // a second invite from the same host is the same host
        XCTAssertEqual(try store.add(Invite.parse("http://192.168.1.20:8710/app/#join=c")!), jon)
        // saved and read back
        let again = HostStore(file: f)
        XCTAssertEqual(again.hosts, store.hosts)
        // removing one doesn't move the other; a new one takes the free port
        try again.remove(jon.id)
        let new = try again.add(Invite.parse("http://192.168.1.40:8710/app/#join=d")!)
        XCTAssertEqual(new.port, HostStore.firstPort)
        XCTAssertEqual(again.hosts.first { $0.id == colin.id }?.port, colin.port)
        // a host that moved keeps its port (its Room page's storage is tied to it)
        try again.move(colin.id, to: URL(string: "http://192.168.1.31:8710")!)
        XCTAssertEqual(HostStore(file: f).hosts.first { $0.id == colin.id }?.port, colin.port)
    }

    func testPages() {
        let h = RoomHost(id: "x", hub: URL(string: "http://192.168.1.20:8710")!, name: "Jon", port: 47380, added: Date())
        XCTAssertEqual(h.pageURL().absoluteString, "http://127.0.0.1:47380/app/")
        XCTAssertEqual(h.pageURL(join: "tok").absoluteString, "http://127.0.0.1:47380/app/#join=tok")
    }
}
