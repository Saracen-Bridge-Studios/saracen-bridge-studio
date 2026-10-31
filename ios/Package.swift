// swift-tools-version:6.0
// RoomCore: the iPhone app's logic that isn't screens. Invite links, the list of hosts, and the loopback relay that
// gives the Room page a secure address on the phone. Builds and tests on Linux as well as Apple platforms, so it is
// checked against the real Room hub before it ever reaches a Mac.

import PackageDescription

let package = Package(
    name: "RoomCore",
    platforms: [.iOS(.v17), .macOS(.v14)],
    products: [
        .library(name: "RoomCore", targets: ["RoomCore"]),
        // a developer tool: run the relay on a desktop against a real hub, for testing the Room page through it
        .executable(name: "roomrelay", targets: ["roomrelay"]),
    ],
    dependencies: [
        // MIT, iOS 13+ and Linux: a small HTTP and WebSocket server (https://github.com/swhitty/FlyingFox)
        .package(url: "https://github.com/swhitty/FlyingFox.git", exact: "0.27.1"),
    ],
    targets: [
        .target(name: "RoomCore", dependencies: [.product(name: "FlyingFox", package: "FlyingFox")], path: "RoomCore"),
        .executableTarget(name: "roomrelay", dependencies: ["RoomCore"], path: "roomrelay"),
        .testTarget(name: "RoomCoreTests", dependencies: ["RoomCore", .product(name: "FlyingFox", package: "FlyingFox")], path: "RoomCoreTests"),
    ]
)
