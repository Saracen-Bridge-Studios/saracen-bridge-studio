# The demo Studio (for Apple's reviewers)

Apple's reviewer has to use a working Room, and Apple says a video isn't enough. A Room normally lives on a
production's own computer, on the office network, where a reviewer can't reach it. So this kit runs one Studio on a
small rented server, hosting a made-up production, **The Lighthouse Keeper**. A keeper program lets each reviewer
device in by itself.

Nothing real is on it: no script, no real production, no real person. Only this demo Room approves devices
automatically. In a real production, an executive checks three safety words with the person on a call.

## What you need

- A server: Ubuntu 24.04, 2 CPUs, 4 GB of memory, a public address. Any provider works.
- The GitHub repository's address, as `git@github.com:OWNER/saracen-bridge-studio.git`.
- Optionally, a name pointing at the server, such as `demo.yourcompany.com`. Without one, the server uses a free
  `<address>.sslip.io` name and still gets a real https certificate.

## Setting it up

1. Open `cloud-init.yaml`. Put the repository in `DEMO_REPO`, and the name in `DEMO_HOST` (or leave it as `AUTO`).
2. Create the server, and paste the whole file into the provider's **user data** (or "cloud-init") box.
3. When it's up, open the provider's console (or ssh in) and run `sudo cat /root/saracen-demo-setup.log`. It ends
   with a deploy key: one line starting `ssh-ed25519`.
4. In the GitHub repository: **Settings → Deploy keys → Add deploy key**. Paste that line, and leave write access
   **off**.
5. Back on the server: `sudo bash /root/saracen-demo-setup.sh`. This second run fetches the code and builds the call
   server, which takes a while. It then starts everything and prints the reviewer's page:
   `https://<name>/review/`.
6. Open that page in a browser to check it. It shows an invite link, a button that opens the app, and a QR code.

## What the reviewer does

The App Review notes say:

1. Open `https://<name>/review/` on the iPhone or iPad.
2. Tap **Open in the Saracen Bridge app**.
3. Type any name, tick the terms, and tap **Join**.

The device is let in within a few seconds, and that person is put on today's call sheet. Each invite works once, so
the page shows a fresh one after every device joins.

## Looking after it

- **Status:** `systemctl status saracen-studio saracen-demo-keeper caddy`
- **Logs:** `journalctl -u saracen-demo-keeper -f`
- **Updating to new code:** `sudo bash /root/saracen-demo-setup.sh` again. It pulls and restarts.
- **What's open to the internet:**
  - 443 and 80, for https through Caddy;
  - 7881/tcp and 50000–50100/udp, for call audio;
  - 22, for ssh.

  The Studio's own pages stay on the server itself, and the Room is reached only through https. Port 8799 is never
  used.
- **Cost:** whatever the provider charges for the smallest server of that size. Keep it running for as long as
  there are App Store reviews: every update is reviewed again.

## Files

| File | What it is |
|---|---|
| `setup.sh` | Installs and starts everything; run as root. The source of truth. |
| `cloud-init.yaml` | `setup.sh` wrapped for the provider's user-data box. Rebuild it with `python make_cloud_init.py` after changing `setup.sh`; a test checks they match. |
| `demo_keeper.py` | Seeds the made-up production, keeps a reviewer invite open, writes the review page, and approves reviewer devices. |
