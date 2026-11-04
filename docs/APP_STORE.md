# Saracen Bridge for iPhone and iPad: the App Store pack

Everything App Store Connect asks for, ready to paste. Words in **[brackets]** are the company's details, which
only Jon's company can fill in. Checked against Apple's rules on 4 November 2026; sources are at the end of
`CIPHER_SARACEN_IPHONE_APP_STORE_SETUP_20261104.md`.

---

## 1. The listing

| Field | Text |
|---|---|
| **Name** (30 max) | Saracen Bridge |
| **Subtitle** (30 max) | Your production's private Room |
| **Category** | Primary: Productivity. Secondary: Business. |
| **Price** | Free |
| **Promotional text** (170 max) | The Room for film and TV productions: today's call sheet, the production board, chat, files and encrypted huddles, from your production's own Studio. |
| **Keywords** (100 max) | film,production,call sheet,crew,cast,producer,shoot,set,schedule,encrypted,team,chat,huddle,board |
| **Support URL** | **[https://company-site/saracen-bridge/support]** (text in section 3) |
| **Privacy policy URL** | **[https://company-site/saracen-bridge/privacy]** (text in section 2) |
| **Copyright** | 2026 **[Company legal name]** |

### Description

The Room is your production's private, end-to-end encrypted hub, on your phone and iPad.

Crew and cast see their own day: call time or pickup, location, weather cover, the scenes being shot, and the full
call sheet. One tap tells the production office you've seen it. The production board shows what everyone needs to
know. Chat runs by department, with private conversations along the lines the production allows, plus files and
encrypted voice huddles and meetings.

Saracen Bridge for iPhone and iPad is the companion to Saracen Bridge Studio, which runs on the production's own
computer. Every production you're in, from every Studio, sits in one place.

- **Encrypted on your device.** Messages, notes, files, call sheets and calls are encrypted before they leave your
  phone. The Studio that hosts the production stores only what it can't read.
- **Join with an invite.** Your production office sends a link or shows a QR code. An executive checks three safety
  words with you on a call before your phone is let in.
- **Safe by design.** Report anything posted, block anyone, filter offensive words, and delete your account at any
  time. Reports go to the production's executives and producers.
- **Face ID lock.** Your Room keys stay in this phone's Keychain and never leave it.

You need an invite from a production that uses Saracen Bridge Studio.

---

## 2. Privacy policy (for the company's website)

> ### Saracen Bridge for iPhone and iPad: privacy policy
>
> **[Company legal name]** ("we") makes Saracen Bridge. This policy covers the Saracen Bridge app for iPhone and
> iPad. It was last updated on **[date]**.
>
> **What the app is.** The app is a companion to Saracen Bridge Studio. It shows the Room of each film or TV
> production you've been invited to. A production's Room is hosted by that production's own Studio, on a computer
> the production company runs. We don't run those Studios, and we can't read what's in them.
>
> **What we collect.** Nothing. The app has no analytics, no advertising and no tracking, and it sends nothing to us.
>
> **What stays on your phone:**
> - your Room keys, kept in the iPhone Keychain for this device only and never backed up;
> - the Studios you've joined;
> - a cache of the Room's content, encrypted as it arrives;
> - your settings.
>
> **What goes to the production's Studio.** Your messages, notes, files, call-sheet confirmations, the name you join
> with, and call audio. All of it is encrypted on your phone first, so the Studio stores only what it can't read. To
> route it, the Studio sees which spaces and people things are for, when they were sent, and their sizes. The
> production's executives can read every space and private message in their Room, and each read is recorded in the
> Room's audit log. The production company that hosts the Studio decides how long its Room keeps content.
>
> **Camera, microphone, Face ID, local network:**
> - The camera only scans an invite's QR code. Nothing is recorded or kept.
> - The microphone is used only in huddles and meetings you join. Audio is end-to-end encrypted and never recorded.
> - Face ID is handled by iOS. The app never sees your face or fingerprint.
> - Local network access lets the app reach your production's Studio on the office network.
>
> **Reports and blocking.** When you report something, the production's executives and producers receive which item
> or person you reported and the reason you chose. The item itself stays encrypted; they read it in their own Room.
> Blocking is recorded by the production's Studio so it applies on all your devices.
>
> **Deleting your account.** In the app, tap your initials in a Room and choose **Delete my account**, or go to
> **Settings → Delete my account in [Studio]**. This deletes your account in that production's Room: your
> messages, notes, files, confirmations, memberships and devices. The Room's audit log keeps a record that the
> account was deleted, because the log can't be changed.
>
> **Children.** The app is for people working on film and TV productions. It isn't meant for children.
>
> **Contact.** **[support email]** · **[postal address]**
>
> **Changes.** If this policy changes, the new version appears here with its date.

---

## 3. Support page (for the company's website)

> ### Saracen Bridge for iPhone and iPad: support
>
> **Joining.** Open the invite link your production office sent, or scan the QR code they show you. Then type your
> name, tick the terms, and tap Join. Read the three safety words on screen to the executive on the call.
>
> **"Can't reach" the Studio.** The Studio that hosts your production has to be open, and your phone has to be on
> the same network (or on the production's private network). If iOS asked about finding devices on your network,
> allow it: Settings → Saracen Bridge → Local Network.
>
> **Reporting abuse.** In any Room, tap ⋯ on a message, note or file and choose Report. The production's executives
> and producers act within 24 hours. You can also email **[support email]**.
>
> **Deleting your account.** Tap your initials in the Room, then Delete my account. Or go to Settings → Delete my
> account in [Studio].
>
> **Contact.** **[support email]**

---

## 4. App Privacy (the "nutrition label")

- **Do you or your third-party partners collect data from this app?** **No.**
- **Why:** Apple counts data as collected only when it's sent off the device in a way the developer or its partners
  can access for longer than it takes to handle the request. The Room's content goes, end-to-end encrypted, to the
  production's own Studio, which the developer doesn't run and can't read. The app contains no analytics,
  advertising or third-party data SDKs.
- The privacy manifest inside the app says the same (no tracking, no collected data types).

## 5. Age rating

Answer the questionnaire as it stands, for an app where people **message each other and share files**, with
**reporting, blocking, a filter and moderation** by the production's executives. Under "unrestricted web access",
answer **no**: links in messages open in Safari, and the app shows only the Room. The developer provides no mature
content itself. Apple works out the rating from the answers.

## 6. Export compliance (asked at the first upload)

1. Does the app use encryption? **Yes.**
2. Which kind? **Industry-standard algorithms not provided by Apple's operating system**: libsodium (X25519,
   XChaCha20-Poly1305, Ed25519) in the Room page, and encrypted calls.
3. Available in France? **No**, for the first release. Under **Pricing and Availability**, leave France out until
   the company files the French encryption declaration. Then upload it here and add France.

Apple's table says this needs no documents outside France. A 2021 US rule removed the yearly self-classification
report for most mass-market encryption products. This isn't legal advice; it's worth a line from the company's
lawyer.

## 7. App Review Information

- **Sign-in required:** No. The app joins with an invite instead (see the notes).
- **Contact:** **[name, phone, email of the person who answers Apple]**
- **Notes** (paste, with the demo address filled in):

> Saracen Bridge is the iPhone and iPad companion to Saracen Bridge Studio, a desktop app for film and TV
> productions. Each production's Room is hosted by its own Studio, normally on the production office's network, so
> we run a demo Studio on a public server for review. It hosts a made-up production, THE LIGHTHOUSE KEEPER.
>
> TO JOIN (no username or password: the app joins by invite):
> 1. On the iPhone or iPad, open https://**[DEMO HOST]**/review/
> 2. Tap "Open in the Saracen Bridge app". Or copy the link, open the app, tap "Join with an invite", then Paste.
> 3. Type any name, tick the terms, and tap Join. The demo approves the device within a few seconds. In real use, an
>    executive checks three safety words with the person on a call. The page shows a fresh invite after each device
>    joins, so reload it for a second device.
>
> WHAT TO TRY: Today (the call sheet; tap "Got it, I'll be there"), Board, Chat (Production office), and Meet. "Huddle"
> starts an end-to-end encrypted voice call.
>
> SAFETY (guideline 1.2):
> - Joining requires accepting terms with zero tolerance for objectionable content and abusive users.
> - Every message, note and file has ⋯ → Report / Hide / Block, and a private conversation's ⋯ reports or blocks the
>   person. An offensive-words filter is on by default (initials → "Hide offensive words").
> - Reports go to the production's executives and producers, who see a Reports list and act within 24 hours: remove
>   the content, remove the person from the production, or dismiss the report. Every decision is recorded in the
>   Room's append-only audit log. Content is end-to-end encrypted, so the production's executives (who hold the keys)
>   moderate their own Room; we can't read it.
> - Contact for reporting to us: Settings → "Report a problem or abuse" (**[support email]**).
>
> ACCOUNT DELETION (5.1.1(v)): tap your initials → "Delete my account", or Settings → "Delete my account in
> [Studio]". This deletes the account in that Room, with its messages, files, memberships and devices.
>
> WHY IT'S MORE THAN A WEBSITE (4.2): the app runs a local relay that gives the Room a secure origin on the device.
> That's what lets the microphone and end-to-end encrypted calls work against a Studio on an office network, which
> Safari can't do there. The app also:
> - keeps each device's Room keys in the iOS Keychain (this device only);
> - locks with Face ID;
> - scans invite QR codes with VisionKit;
> - keeps several Studios side by side;
> - opens decrypted files in the share sheet.
>
> BACKGROUND AUDIO: UIBackgroundModes "audio" keeps a live encrypted huddle or meeting going when the screen locks.
> It's used only while the person is in a call.
>
> LOCAL NETWORK: used to reach the production's Studio on the office network. The demo Studio is reached over https.

## 8. Screenshots

The workflow makes them on GitHub's Macs from the demo production, in the iPhone simulators, at Apple's sizes:
- **iPhone 6.9-inch** (iPhone Pro Max: 1320 × 2868)
- **iPhone 6.3-inch** (iPhone Pro: 1206 × 2622)
- **iPad 13-inch** (iPad Pro 13-inch: 2064 × 2752)

They're in the run's **iphone-screenshots** download, one folder per size. Pick three to six per size:
- Today (the call sheet)
- Board
- Chat
- Meet or a huddle
- the Report menu
- Settings

Apple requires the screenshots to show the app in use, and to be suitable for all ages.
