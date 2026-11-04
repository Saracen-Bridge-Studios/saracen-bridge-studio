"""Builds cloud-init.yaml from setup.sh, so the server can be set up by pasting one file into the provider's
"user data" box. Run after changing setup.sh:  python packaging/demo/make_cloud_init.py  (a test checks they match)."""
from pathlib import Path

HERE = Path(__file__).resolve().parent


def build() -> str:
    script = (HERE / "setup.sh").read_text()
    body = "".join("      " + line if line.strip() else "\n" for line in script.splitlines(keepends=True))
    return f"""#cloud-config
# Saracen Bridge demo Studio for App Review (built from setup.sh by make_cloud_init.py; don't edit by hand).
# Before pasting: put the repository in DEMO_REPO, and a name pointing at this server in DEMO_HOST (or leave AUTO).
write_files:
  - path: /etc/saracen-demo.env
    permissions: "0644"
    content: |
      DEMO_REPO=git@github.com:OWNER/saracen-bridge-studio.git
      DEMO_HOST=AUTO
  - path: /root/saracen-demo-setup.sh
    permissions: "0755"
    content: |
{body}runcmd:
  - [bash, -c, "bash /root/saracen-demo-setup.sh > /root/saracen-demo-setup.log 2>&1"]
"""


if __name__ == "__main__":
    (HERE / "cloud-init.yaml").write_text(build())
    print("wrote", HERE / "cloud-init.yaml")
