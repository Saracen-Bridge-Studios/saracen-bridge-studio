import Foundation
import Security
import RoomCore

/// The Room's device key for each Studio, in the Keychain: readable after the phone's first unlock, on this device
/// only (never in a backup or iCloud Keychain). Web storage on iOS isn't guaranteed to last, so the page keeps its key
/// here through the app's bridge (S-83: "a native key store is phase 2").
enum Keychain {
    static let service = "com.saracenbridge.room.device"

    /// What the Room page may keep here: its device key and its Room state (who this phone is, the root key it
    /// trusts, its status), one of each per Studio.
    static let names: Set<String> = ["device", "state"]

    static func account(_ host: RoomHost, _ name: String) -> String { name + ":" + host.id }

    static func read(account: String) -> String? {
        let q: [String: Any] = [kSecClass as String: kSecClassGenericPassword, kSecAttrService as String: service,
                                kSecAttrAccount as String: account, kSecReturnData as String: true,
                                kSecMatchLimit as String: kSecMatchLimitOne]
        var out: AnyObject?
        guard SecItemCopyMatching(q as CFDictionary, &out) == errSecSuccess, let data = out as? Data else { return nil }
        return String(data: data, encoding: .utf8)
    }

    @discardableResult
    static func write(_ value: String, account: String) -> Bool {
        let q: [String: Any] = [kSecClass as String: kSecClassGenericPassword, kSecAttrService as String: service,
                                kSecAttrAccount as String: account]
        SecItemDelete(q as CFDictionary)
        var add = q
        add[kSecValueData as String] = Data(value.utf8)
        add[kSecAttrAccessible as String] = kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
        return SecItemAdd(add as CFDictionary, nil) == errSecSuccess
    }

    static func delete(account: String) {
        let q: [String: Any] = [kSecClass as String: kSecClassGenericPassword, kSecAttrService as String: service,
                                kSecAttrAccount as String: account]
        SecItemDelete(q as CFDictionary)
    }
}
