#!/usr/bin/env bash
# Saracen Bridge Studio, web version (1.3.0), on a fresh Ubuntu 24.04 server. See README.md.
#
# Run as root. The first run installs everything and prints a deploy key: add it to the GitHub repository
# (Settings > Deploy keys > Add, read-only), then run this script again. The second run fetches the code, starts the
# Studio behind https on your address, and prints the first admin's password once.
#
# /etc/saracen-web.env (not secret):
#   WEB_REPO      the repository, as git@github.com:OWNER/NAME.git                      (required)
#   WEB_HOST      your address, such as studio.saracenbridge.com, pointing at this server  (AUTO uses <ip>.sslip.io)
#   ADMIN_EMAIL   the first admin's email                                                 (required)
#   ADMIN_NAME    their name
# /etc/saracen-web/secrets.env (root only, chmod 600; the AI brain):
#   STUDIO_AI_PROVIDER=openai        openai (Jon's account, Tim 9 Nov), anthropic or gemini
#   STUDIO_AI_KEY=...                the company's API key: on this server only, never in a browser
#   STUDIO_AI_MODEL=                 blank uses the Studio's default; Settings > AI brain lists the account's models
#
# Open to the internet: 443 and 80 (https through Caddy) and 22 (ssh). The Studio itself listens on 127.0.0.1 only.
# Never port 8799.
set -euo pipefail

[ "$(id -u)" = 0 ] || { echo "Run this as root (sudo)."; exit 1; }
[ -f /etc/saracen-web.env ] && . /etc/saracen-web.env
WEB_REPO="${WEB_REPO:?Set WEB_REPO in /etc/saracen-web.env, such as git@github.com:OWNER/saracen-bridge-studio.git}"
WEB_HOST="${WEB_HOST:-AUTO}"
ADMIN_EMAIL="${ADMIN_EMAIL:?Set ADMIN_EMAIL in /etc/saracen-web.env}"
ADMIN_NAME="${ADMIN_NAME:-Admin}"
APP=/opt/saracen
DATA=/var/lib/saracen
SECRETS=/etc/saracen-web/secrets.env
PORT=8795

export DEBIAN_FRONTEND=noninteractive

# ------------------------------------------------------------------ 1. system packages, Caddy, uv, OCR
if [ ! -f /var/lib/saracen-web.base ]; then
  apt-get update -q
  apt-get install -yq git curl ca-certificates gnupg ufw tesseract-ocr debian-keyring debian-archive-keyring apt-transport-https
  curl -1sLf https://dl.cloudsmith.io/public/caddy/stable/gpg.key | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
  curl -1sLf https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt > /etc/apt/sources.list.d/caddy-stable.list
  apt-get update -q && apt-get install -yq caddy
  id saracen >/dev/null 2>&1 || useradd --system --create-home --home-dir "$DATA" --shell /usr/sbin/nologin saracen
  install -d -o saracen -g saracen -m 750 "$DATA"
  curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin INSTALLER_NO_MODIFY_PATH=1 sh
  ufw allow 22/tcp && ufw allow 80/tcp && ufw allow 443/tcp
  ufw --force enable
  touch /var/lib/saracen-web.base
fi
install -d -m 700 /etc/saracen-web
[ -f "$SECRETS" ] || printf 'STUDIO_AI_PROVIDER=openai\nSTUDIO_AI_KEY=\nSTUDIO_AI_MODEL=\n' > "$SECRETS"
chmod 600 "$SECRETS"; chown root:root "$SECRETS"

# ------------------------------------------------------------------ 2. the deploy key (read-only access to the code)
KEY=/root/.ssh/saracen_web
if [ ! -f "$KEY" ]; then
  install -d -m 700 /root/.ssh
  ssh-keygen -q -t ed25519 -N "" -C "saracen-web@$(hostname)" -f "$KEY"
fi
cat > /root/.ssh/config <<CFG
Host github.com
  IdentityFile $KEY
  IdentitiesOnly yes
  StrictHostKeyChecking accept-new
CFG
if ! GIT_SSH_COMMAND="ssh -F /root/.ssh/config" git ls-remote "$WEB_REPO" >/dev/null 2>&1; then
  echo
  echo "Add this deploy key to the GitHub repository (Settings > Deploy keys > Add deploy key, leave write access off):"
  echo
  cat "$KEY.pub"
  echo
  echo "Then run this script again:  sudo bash /root/saracen-web-setup.sh"
  exit 0
fi

# ------------------------------------------------------------------ 3. the code and Python 3.13
if [ -d "$APP/.git" ]; then
  GIT_SSH_COMMAND="ssh -F /root/.ssh/config" git -C "$APP" pull --ff-only
else
  GIT_SSH_COMMAND="ssh -F /root/.ssh/config" git clone --depth 1 "$WEB_REPO" "$APP"
fi
uv venv --allow-existing --python 3.13 "$APP/.venv"
uv pip install --python "$APP/.venv/bin/python" -q -r "$APP/requirements.txt"

# ------------------------------------------------------------------ 4. the address, https, the service
if [ "$WEB_HOST" = AUTO ]; then
  IP=$(curl -fsS https://api.ipify.org)
  WEB_HOST="$(echo "$IP" | tr . -).sslip.io"
fi
cat > /etc/caddy/Caddyfile <<CADDY
$WEB_HOST {
	encode zstd gzip
	request_body {
		max_size 20GB
	}
	header {
		Strict-Transport-Security "max-age=31536000; includeSubDomains"
		X-Content-Type-Options "nosniff"
		X-Frame-Options "DENY"
		Referrer-Policy "same-origin"
		-Server
	}
	reverse_proxy 127.0.0.1:$PORT
}
CADDY

cat > /etc/systemd/system/saracen-studio.service <<UNIT
[Unit]
Description=Saracen Bridge Studio, web version
After=network-online.target
Wants=network-online.target

[Service]
User=saracen
WorkingDirectory=$APP
Environment=STUDIO_WEB=1
Environment=STUDIO_HOME=$DATA/studio
EnvironmentFile=$SECRETS
ExecStart=$APP/.venv/bin/python studio_launcher.py --headless --port $PORT
Restart=always
RestartSec=5
NoNewPrivileges=yes
ProtectSystem=full
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
UNIT

# a copy of the data every night, the last 14 kept (root only)
cat > /etc/cron.daily/saracen-backup <<BACKUP
#!/bin/sh
install -d -m 700 /var/backups/saracen
tar -czf /var/backups/saracen/studio-\$(date +%F).tgz -C $DATA studio 2>/dev/null
ls -1t /var/backups/saracen/studio-*.tgz | tail -n +15 | xargs -r rm --
BACKUP
chmod 755 /etc/cron.daily/saracen-backup

install -d -o saracen -g saracen -m 750 "$DATA/studio"
chown -R saracen:saracen "$DATA"
systemctl daemon-reload
systemctl enable --now saracen-studio
systemctl restart saracen-studio
systemctl restart caddy
for i in $(seq 1 60); do curl -fsS "http://127.0.0.1:$PORT/api/health" >/dev/null 2>&1 && break; sleep 2; done

# ------------------------------------------------------------------ 5. the first admin (once)
if [ ! -s "$DATA/studio/web_users.json" ]; then
  echo
  runuser -u saracen -- env STUDIO_HOME="$DATA/studio" PYTHONPATH="$APP/engine" "$APP/.venv/bin/python" -m studio.web add-user "$ADMIN_EMAIL" "$ADMIN_NAME" --admin
fi
grep -q '^STUDIO_AI_KEY=.\+' "$SECRETS" || echo "Note: the AI brain has no key yet. Put the company's key in $SECRETS, then: systemctl restart saracen-studio"
echo
echo "Saracen Bridge Studio is running at:  https://$WEB_HOST/"
