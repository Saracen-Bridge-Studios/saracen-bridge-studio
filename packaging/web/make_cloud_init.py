"""Builds cloud-init.yaml from setup.sh, so the server can be set up by pasting one file into the provider's
"user data" box. Run after changing setup.sh:  python packaging/web/make_cloud_init.py  (a test checks they match).
The AI key is not in this file: it goes in /etc/saracen-web/secrets.env on the server afterwards."""
from pathlib import Path

HERE = Path(__file__).resolve().parent


def build() -> str:
    script = (HERE / "setup.sh").read_text()
    body = "".join("      " + line if line.strip() else "\n" for line in script.splitlines(keepends=True))
    return f"""#cloud-config
# Saracen Bridge Studio, web version (built from setup.sh by make_cloud_init.py; don't edit by hand).
# Before pasting: the repository in WEB_REPO, your address in WEB_HOST (or AUTO), and the first admin's email.
write_files:
  - path: /etc/saracen-web.env
    permissions: "0644"
    content: |
      WEB_REPO=git@github.com:OWNER/saracen-bridge-studio.git
      WEB_HOST=AUTO
      ADMIN_EMAIL=you@example.com
      ADMIN_NAME=Your Name
  - path: /root/saracen-web-setup.sh
    permissions: "0755"
    content: |
{body}runcmd:
  - [bash, -c, "bash /root/saracen-web-setup.sh > /root/saracen-web-setup.log 2>&1"]
"""


if __name__ == "__main__":
    (HERE / "cloud-init.yaml").write_text(build())
    print("wrote", HERE / "cloud-init.yaml")
