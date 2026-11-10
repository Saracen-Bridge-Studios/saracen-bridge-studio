# Saracen Bridge Studio on the web (1.3.0)

The same Studio, on a server, for a team in their browsers: everyone signs in with their own login, the AI brain is the
company's cloud AI account (Jon's OpenAI account), and the desktop Studio's Library can be imported. The desktop app
is unchanged.

## What you need

- A server: Ubuntu 24.04, 2 CPUs, 4 GB of memory, a public address. Somewhere in London keeps Jon's data in the UK.
- Your web address (such as `studio.saracenbridge.com`) pointing at the server: an **A record** with the server's
  address, set where the domain was bought. Without one, the server uses a free `<address>.sslip.io` name; https works
  either way.
- The GitHub repository's address, as `git@github.com:Saracen-Bridge-Studios/saracen-bridge-studio.git`.
- Jon's OpenAI API key (platform.openai.com › API keys). It goes on the server only, never into this file or a browser.

## Setting it up

1. Open `cloud-init.yaml`. Fill in `WEB_REPO`, `WEB_HOST` (your address, or leave `AUTO`), `ADMIN_EMAIL` and
   `ADMIN_NAME` (the first admin, usually Jon).
2. Create the server and paste the whole file into the provider's **user data** (or "cloud-init") box.
3. When it's up, open the provider's console (or ssh in) and run `sudo cat /root/saracen-web-setup.log`. It ends with
   a deploy key: one line starting `ssh-ed25519`.
4. In the GitHub repository: **Settings › Deploy keys › Add deploy key**. Paste that line; leave write access **off**.
5. Put the AI key on the server: `sudo nano /etc/saracen-web/secrets.env` and fill in `STUDIO_AI_KEY=` (leave
   `STUDIO_AI_PROVIDER=openai`; `STUDIO_AI_MODEL` blank uses the Studio's default).
6. Back on the server: `sudo bash /root/saracen-web-setup.sh`. It fetches the code, starts the Studio behind https and
   prints **the first admin's password, once**, and the address.
7. Sign in at the address. In **Settings**: **Test the AI brain**; add the team under **Team** (each new login's
   password is shown once, to send privately); bring Jon's Library across under **Import data**.

## Moving the desktop Library over

On Jon's Mac, zip the folder `~/Library/Application Support/SaracenStudio` (in Finder: Go › Go to Folder…, paste it,
go up one level, right-click **SaracenStudio** › Compress). On Windows it's `%APPDATA%\SaracenStudio`. Then in the web
version, **Settings › Import data**: choose the zip, **Import**. Every saved script, breakdown, budget, report and
workbook comes across; items already there are kept as they are. Settings, saved cloud keys (locked to the old
computer), the AI model and the Room stay behind.

## Looking after it

- **Status and logs:** `systemctl status saracen-studio caddy` · `journalctl -u saracen-studio -f`
- **Updating to new code:** `sudo bash /root/saracen-web-setup.sh` again (it pulls and restarts).
- **Backups:** a copy of the data every night in `/var/backups/saracen` (the last 14). Copy them off the server too.
- **Logins from the command line:** `sudo runuser -u saracen -- env STUDIO_HOME=/var/lib/saracen/studio
  PYTHONPATH=/opt/saracen/engine /opt/saracen/.venv/bin/python -m studio.web list` (or `add-user EMAIL "Name" --admin`,
  `reset EMAIL`).
- **Open to the internet:** 443 and 80 (https through Caddy) and 22 (ssh). The Studio listens on 127.0.0.1 only.

## Not in the web version yet

The Room (it stays in the desktop Studio and the iPhone app for now), running Gemma on the server, launching
A.I.D.E.N. and F.R.A.T. as programs, and working offline.
