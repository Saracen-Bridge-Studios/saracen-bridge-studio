import Foundation

/// An invite to a production's Room: the host's address and the one-time join token.
///
/// The Studio sends links like `http://192.168.1.20:8710/app/#join=TOKEN` (or `?join=TOKEN`). The invite page in Safari
/// can hand the same link to the app as `saracenbridge://join?invite=<the link, percent-encoded>`.
public struct Invite: Equatable, Sendable {
    public let hub: URL
    public let token: String

    public init(hub: URL, token: String) {
        self.hub = hub
        self.token = token
    }

    /// The invite in a pasted text, a link or the app's own `saracenbridge://` link; nil if there isn't one.
    public static func parse(_ text: String) -> Invite? {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        // the first link in the text (people paste whole messages)
        let candidate = trimmed.split(whereSeparator: { $0.isWhitespace }).map(String.init)
            .first(where: { $0.lowercased().hasPrefix("http://") || $0.lowercased().hasPrefix("https://") || $0.lowercased().hasPrefix("saracenbridge://") })
            ?? trimmed
        guard let url = URL(string: candidate), let scheme = url.scheme?.lowercased() else { return nil }
        if scheme == "saracenbridge" {
            guard let comps = URLComponents(url: url, resolvingAgainstBaseURL: false),
                  let inner = comps.queryItems?.first(where: { $0.name == "invite" })?.value else { return nil }
            return parse(inner)
        }
        guard scheme == "http" || scheme == "https", let host = url.host, !host.isEmpty else { return nil }
        guard let token = joinToken(in: url) else { return nil }
        var base = URLComponents()
        base.scheme = scheme
        base.host = host
        base.port = url.port
        guard let hub = base.url else { return nil }
        return Invite(hub: hub, token: token)
    }

    /// `join=TOKEN` in the fragment or the query; a token is letters, digits, `-` and `_` only.
    static func joinToken(in url: URL) -> String? {
        for part in [url.fragment ?? "", url.query ?? ""] {
            for pair in part.split(whereSeparator: { $0 == "&" || $0 == "?" || $0 == "#" }) {
                let kv = pair.split(separator: "=", maxSplits: 1).map(String.init)
                guard kv.count == 2, kv[0] == "join" else { continue }
                let token = kv[1]
                let allowed = CharacterSet(charactersIn: "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
                if !token.isEmpty, token.unicodeScalars.allSatisfy({ allowed.contains($0) }) { return token }
            }
        }
        return nil
    }
}
