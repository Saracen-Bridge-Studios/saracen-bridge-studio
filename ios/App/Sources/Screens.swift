import SwiftUI
import LocalAuthentication
import VisionKit
import RoomCore

struct RootView: View {
    @EnvironmentObject var model: AppModel

    var body: some View {
        ZStack {
            Theme.ink.ignoresSafeArea()
            if model.locked {
                LockView()
            } else {
                NavigationStack {
                    StudiosView()
                        .navigationDestination(item: $model.open) { host in
                            RoomScreen(host: host, joinToken: model.joinToken)
                                .onDisappear { model.joinToken = nil }
                        }
                }
            }
        }
        .alert("Saracen Bridge", isPresented: Binding(get: { model.notice != nil }, set: { if !$0 { model.notice = nil } })) {
            Button("OK", role: .cancel) {}
        } message: { Text(model.notice ?? "") }
    }
}

/// The Studios this phone is in. With none yet: how to join.
struct StudiosView: View {
    @EnvironmentObject var model: AppModel
    @State private var joining = false
    @State private var settings = false

    var body: some View {
        Group {
            if model.hosts.isEmpty {
                WelcomeView(join: { joining = true })
            } else {
                List {
                    Section {
                        ForEach(model.hosts) { host in
                            Button { model.open = host } label: { HostRow(host: host) }
                                .listRowBackground(Theme.card)
                                .swipeActions {
                                    Button("Leave", role: .destructive) { model.remove(host) }
                                }
                                .accessibilityIdentifier("host-\(host.name)")
                        }
                    } header: {
                        Text("Your Studios").font(.caption.weight(.semibold)).tracking(2).foregroundStyle(Theme.gold)
                    } footer: {
                        Text("Each Studio hosts its own productions. Open one to see its Room: your day, the board, chat and meetings.")
                            .foregroundStyle(Theme.muted)
                    }
                }
                .scrollContentBackground(.hidden)
            }
        }
        .background(Theme.ink)
        .navigationTitle("Saracen Bridge")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .topBarLeading) {
                Button { settings = true } label: { Image(systemName: "gearshape") }.accessibilityLabel("Settings")
            }
            ToolbarItem(placement: .topBarTrailing) {
                Button { joining = true } label: { Image(systemName: "plus") }.accessibilityLabel("Join with an invite")
            }
        }
        .sheet(isPresented: $joining) { JoinSheet() }
        .sheet(isPresented: $settings) { SettingsSheet() }
    }
}

struct HostRow: View {
    let host: RoomHost
    var body: some View {
        HStack(spacing: 14) {
            Image("Crest").resizable().scaledToFit().frame(width: 40, height: 40)
                .clipShape(RoundedRectangle(cornerRadius: 10))
            VStack(alignment: .leading, spacing: 3) {
                Text(host.name).font(.headline).foregroundStyle(.white)
                Text(host.hub.host ?? "").font(.caption.monospaced()).foregroundStyle(Theme.muted)
            }
            Spacer()
            Image(systemName: "chevron.right").foregroundStyle(Theme.muted)
        }
        .padding(.vertical, 6)
    }
}

struct WelcomeView: View {
    let join: () -> Void
    var body: some View {
        VStack(spacing: 22) {
            Spacer()
            Image("Crest").resizable().scaledToFit().frame(width: 120, height: 120)
                .clipShape(RoundedRectangle(cornerRadius: 28))
                .shadow(color: Theme.gold.opacity(0.25), radius: 24)
            Text("The Room").font(.system(size: 38, weight: .regular, design: .serif)).foregroundStyle(.white)
            Text("Your production's private, encrypted hub: your day, the board, chat and meetings. Join with the invite your production office sent you.")
                .multilineTextAlignment(.center).foregroundStyle(Theme.muted).padding(.horizontal, 28)
            Button(action: join) {
                Text("Join with an invite").font(.headline).frame(maxWidth: .infinity).padding(.vertical, 16)
            }
            .buttonStyle(GoldButton())
            .padding(.horizontal, 28)
            .accessibilityIdentifier("join-invite")
            Text("Everything is encrypted on this phone before it leaves.").font(.footnote).foregroundStyle(Theme.muted)
            Spacer()
        }
    }
}

struct GoldButton: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .foregroundStyle(Theme.ink)
            .background(LinearGradient(colors: [Color(red: 0.93, green: 0.79, blue: 0.42), Theme.gold], startPoint: .top, endPoint: .bottom))
            .clipShape(RoundedRectangle(cornerRadius: 14))
            .opacity(configuration.isPressed ? 0.8 : 1)
    }
}

/// Join: paste the invite link (or the whole message), or scan the QR code on the Studio's screen.
struct JoinSheet: View {
    @EnvironmentObject var model: AppModel
    @Environment(\.dismiss) private var dismiss
    @State private var text = ""
    @State private var scanning = false
    @State private var problem: String?

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    TextField("http://…/app/#join=…", text: $text, axis: .vertical)
                        .textInputAutocapitalization(.never).autocorrectionDisabled().font(.callout.monospaced())
                        .accessibilityIdentifier("invite-field")
                    Button("Paste") { text = UIPasteboard.general.string ?? "" }
                } header: { Text("Invite link") } footer: {
                    Text("Paste the link, or the whole message it came in.").foregroundStyle(Theme.muted)
                }
                if DataScannerViewController.isSupported {
                    Section {
                        Button { scanning = true } label: { Label("Scan the QR code", systemImage: "qrcode.viewfinder") }
                    } footer: { Text("On the Studio, Members & access shows each invite's QR code.").foregroundStyle(Theme.muted) }
                }
                if let problem { Section { Text(problem).foregroundStyle(.orange) } }
            }
            .scrollContentBackground(.hidden)
            .background(Theme.ink)
            .navigationTitle("Join a Room")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) { Button("Cancel") { dismiss() } }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Join") { submit(text) }.disabled(text.isEmpty).accessibilityIdentifier("join-submit")
                }
            }
            .sheet(isPresented: $scanning) {
                QRScanner { found in scanning = false; text = found; submit(found) }.ignoresSafeArea()
            }
        }
    }

    func submit(_ value: String) {
        guard let invite = Invite.parse(value) else {
            problem = "That isn't an invite link. It starts http and has join= in it."
            return
        }
        dismiss()
        model.join(invite)
    }
}

struct QRScanner: UIViewControllerRepresentable {
    let found: (String) -> Void

    func makeUIViewController(context: Context) -> DataScannerViewController {
        let vc = DataScannerViewController(recognizedDataTypes: [.barcode(symbologies: [.qr])], qualityLevel: .balanced,
                                           isHighlightingEnabled: true)
        vc.delegate = context.coordinator
        try? vc.startScanning()
        return vc
    }

    func updateUIViewController(_ vc: DataScannerViewController, context: Context) {}
    func makeCoordinator() -> Coordinator { Coordinator(found: found) }

    final class Coordinator: NSObject, DataScannerViewControllerDelegate {
        let found: (String) -> Void
        var done = false
        init(found: @escaping (String) -> Void) { self.found = found }
        func dataScanner(_ scanner: DataScannerViewController, didAdd items: [RecognizedItem], allItems: [RecognizedItem]) {
            for item in items {
                if case .barcode(let code) = item, let value = code.payloadStringValue, Invite.parse(value) != nil, !done {
                    done = true
                    scanner.stopScanning()
                    found(value)
                }
            }
        }
    }
}

struct SettingsSheet: View {
    @EnvironmentObject var model: AppModel
    @Environment(\.dismiss) private var dismiss
    @State private var renaming: RoomHost?
    @State private var newName = ""

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    Toggle("Lock with Face ID", isOn: $model.lockWithFaceID)
                } footer: {
                    Text("Asks for Face ID (or your passcode) whenever the app comes back from the background.").foregroundStyle(Theme.muted)
                }
                if !model.hosts.isEmpty {
                    Section("Studios") {
                        ForEach(model.hosts) { host in
                            Button(host.name) { renaming = host; newName = host.name }
                        }
                    }
                }
                Section {
                    LabeledContent("Version", value: Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "")
                } footer: {
                    Text("The Room's encryption keys for this phone are kept in its Keychain and never leave it.").foregroundStyle(Theme.muted)
                }
            }
            .scrollContentBackground(.hidden)
            .background(Theme.ink)
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar { ToolbarItem(placement: .confirmationAction) { Button("Done") { dismiss() } } }
            .alert("Name this Studio", isPresented: Binding(get: { renaming != nil }, set: { if !$0 { renaming = nil } })) {
                TextField("Name", text: $newName)
                Button("Save") { if let h = renaming { model.rename(h, newName) }; renaming = nil }
                Button("Cancel", role: .cancel) { renaming = nil }
            }
        }
    }
}

struct LockView: View {
    @EnvironmentObject var model: AppModel
    @State private var failed = false

    var body: some View {
        VStack(spacing: 20) {
            Image("Crest").resizable().scaledToFit().frame(width: 96, height: 96).clipShape(RoundedRectangle(cornerRadius: 22))
            Text("Saracen Bridge is locked").font(.title3).foregroundStyle(.white)
            Button { unlock() } label: { Label("Unlock", systemImage: "faceid").font(.headline).padding(.horizontal, 28).padding(.vertical, 14) }
                .buttonStyle(GoldButton())
            if failed { Text("Not unlocked. Try again.").foregroundStyle(Theme.muted) }
        }
        .onAppear(perform: unlock)
    }

    func unlock() {
        let ctx = LAContext()
        var err: NSError?
        guard ctx.canEvaluatePolicy(.deviceOwnerAuthentication, error: &err) else { model.locked = false; return }
        ctx.evaluatePolicy(.deviceOwnerAuthentication, localizedReason: "Unlock the Room") { ok, _ in
            DispatchQueue.main.async { if ok { model.locked = false } else { failed = true } }
        }
    }
}
