# Saracen Bridge Studio on the web: phase 1 (1.3.0)

**Date:** 9 November 2026 · **Asked by:** Tim, for Jon. The requests:
- "Jon wants to make this a webpage to start so we can start using the service";
- "I need this running web … transfer all this data over";
- "let's do the mock up and cloud connection for the AI brain";
- "the engine will be through Jon's OpenAI account".

## What phase 1 is

The same Studio, running on a server, for Jon's team in their browsers. The desktop app is unchanged and keeps working
offline. One codebase runs both ways; the web version is switched on by `STUDIO_WEB=1` on the server.

| | Desktop Studio | Web version (phase 1) |
|---|---|---|
| Who | one person on their computer | Jon's team, each with their own login (admin or member) |
| Tools | all | all calculation and reading tools; Library; Word and Excel downloads |
| AI | Gemma on the computer, or the person's own cloud key | the **AI brain**: Jon's OpenAI account, key on the server only |
| Data | that computer's data folder | the server's; the desktop Library imports from a zip |
| Not yet | | the Room, Gemma on the server, launching A.I.D.E.N./F.R.A.T. programs, offline |

## Built (code in `engine/studio/web.py`, `server.py`, `ui/login.html`, `ui/studio.js`; kit in `packaging/web/`)

- **Sign-in:**
  - a login per person;
  - passwords hashed with scrypt (n=2^17, r=8, p=1, 16-byte salt), never stored in clear;
  - server-side sessions: a 256-bit random id in an HttpOnly, SameSite=Strict cookie, Secure over https;
  - a new id at each sign-in;
  - 12 hours idle, 7 days at most;
  - a password change or reset ends every session of that person.
- **Throttling:** 5 wrong passwords in 15 minutes for one email (20 from one address) means a 15-minute wait. It is never a permanent lock-out.
- **Cross-site refusal:** a request that changes something must come from the Studio's own pages (Sec-Fetch-Site or Origin), on top of SameSite.
- **Team:**
  - admins add people (the password is shown once), reset passwords and remove logins;
  - you can't remove yourself or the last admin.
- **AI brain:**
  - `STUDIO_AI_PROVIDER=openai` (the default), `STUDIO_AI_KEY`, `STUDIO_AI_MODEL` (blank uses the Studio's default) in a root-only file on the server;
  - used for writing tools and Ask Jonny;
  - the key never reaches a browser or a status reply;
  - Settings shows the provider and model, has **Test the AI brain**, and, for admins, **List the account's models**.
- **Import data:**
  - upload the desktop data folder as a zip;
  - only `runs/<tool>/<id>/…` is taken, and the Library index is updated;
  - a run already there is kept;
  - entries that would land outside the Library are refused: absolute paths, `..`, drive letters and symlinks;
  - a 20 GB unpacked limit;
  - settings, saved keys, the model and the Room stay behind.
- **Desktop-only endpoints answer 403 on the web:** the file dialog, opening programs and links on the server, the Gemma download, the user's own cloud key, and the Room.
- **Server kit (`packaging/web`):**
  - Ubuntu 24.04, with Caddy https on Tim's address and security headers;
  - Studio on 127.0.0.1 only, under systemd (NoNewPrivileges, ProtectSystem, PrivateTmp);
  - a firewall open on 22, 80 and 443 only;
  - Tesseract for scanned scripts;
  - nightly backups, keeping 14;
  - prints the first admin's password once.
- **Tests:** `tests/test_web.py` (13), including that the desktop app is unchanged without the switch.

## Decisions taken, and why

- **OpenAI through Jon's account (Tim, 9 Nov).**
  - OpenAI doesn't train on API data unless the account opts in.
  - It keeps inputs and outputs up to 30 days for abuse monitoring; zero data retention is available on approval.
  - So a confidential script sent to the AI is held by OpenAI for up to 30 days unless Jon's account gets ZDR. Calculation tools never send anything.
  - Tim's standing rule: scripts are confidential. **Jon should decide whether to request ZDR from OpenAI before the team sends scripts to writing tools.**
- **A server in London:** Jon is in London and the data is his company's.
- **One shared workspace for the team:** phase 2 (outside users, a separate workspace per company) needs every one of the 24 data-folder uses to be per-workspace. That hasn't been sized yet.
- **This reverses two earlier directions.** On 12 Oct the brief was standalone with no cloud; on 17 Oct the Room was to have no custom web address. Jon's direction on 9 Nov supersedes both, for the web version only; the desktop app keeps them.

## What Tim and Jon do

1. Rent the server (London, Ubuntu 24.04, 2 CPUs, 4 GB) in the company's name.
2. Point the web address at it (an A record).
3. Paste `packaging/web/cloud-init.yaml` with the four values filled in.
4. Add the deploy key to GitHub.
5. Put Jon's OpenAI key in `/etc/saracen-web/secrets.env`.
6. Run the setup again. The README has each step.

## Rule 1 (9 Nov)

**Leg 1, 10 searches:**
- FastAPI session authentication;
- Anthropic API data retention;
- OWASP session management and cookies;
- scrypt parameters;
- Caddy reverse proxy and forwarded headers;
- UK/London VPS hosting;
- brute-force throttling;
- secrets on Linux services;
- OpenAI and Gemini API data use;
- zip-slip on restore.

**Leg 2:**
- The conversation search found nothing in this project.
- The project memory and register were used instead: the 12 Oct no-cloud brief, the 17 Oct no-web-address Room, the confidential-scripts rule, the demo kit (S-117) and S-124.

**Leg 3, 4 searches:**
- uvicorn proxy headers behind Caddy (uvicorn trusts 127.0.0.1 by default, so the Studio stays on localhost behind Caddy);
- large FastAPI uploads (streamed to disk);
- Anthropic spend limits;
- OpenAI API retention.

Sources:
- [MDN: session management](https://developer.mozilla.org/en-US/docs/Web/Security/Authentication/Session_management)
- [OWASP ASVS V3 (session management)](https://github.com/OWASP/ASVS/blob/v4.0.3/4.0/en/0x12-V3-Session-management.md)
- [scrypt in Python (OWASP figures)](https://mojoauth.com/security-guides/scrypt-in-python)
- [FastAPI: behind a proxy](https://fastapi.tiangolo.com/advanced/behind-a-proxy)
- [Caddy reverse-proxy hardening](https://aicybr.com/blog/caddy-reverse-proxy-hardening-self-hosting)
- [Anthropic: API and data retention](https://platform.claude.com/docs/en/manage-claude/api-and-data-retention)
- [OpenAI API data retention summary (verified 18 Oct 2026)](https://www.developersdigest.tech/models/data-retention/openai), which cites OpenAI's "your data" guide
- [changedetection.io zip-slip in backup restore (CVE-2026-29065)](https://corgea.com/advisories/vulnerabilities/CVE-2026-29065)
- [OWASP WSTG: weak lock-out](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/04-Authentication_Testing/03-Testing_for_Weak_Lock_Out_Mechanism)
- [Claude Console spend limits](https://platform.claude.com/docs/en/api/admin/spend_limits/create)

## Not verified yet

- The kit on a real rented server: the same open item as the demo kit.
- A real OpenAI key through the AI brain. The tests use a stand-in, and the call path is the Studio's existing cloud code.
- Import of a full real Library from Jon's Mac.
