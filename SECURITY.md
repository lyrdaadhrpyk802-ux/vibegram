# Security Policy

## Supported versions

Only the latest released version of `vibegram` receives security fixes.

## Reporting a vulnerability

Report security issues privately to the maintainer at
`lyrdaadhrpyk802@gmail.com`. Do **not** open a public GitHub issue for
security problems. Include a clear description, a minimal reproduction,
and the affected version. You will receive an acknowledgment within a
reasonable timeframe; please allow time for a fix to be prepared before
any public disclosure.

## Threat model and known limitations

- **Reverse-engineered cryptography.** The Vibe authentication scheme
  (`userapi/crypto/vibe_auth.py`) and the obfuscated2 transport
  (`userapi/crypto/obfuscated.py`) were reconstructed from observed
  network traffic, not from a published specification. They have not
  received an independent cryptographic audit. Do not assume the
  transport is secure against an active attacker who can modify traffic
  between the client and Vibe's servers.
- **Telethon runtime patching.** The library monkey-patches two Telethon
  internals (`PQInnerData` and `rsa.encrypt`) at import time. A version
  guard rejects unsupported Telethon builds; originals are saved and can
  be restored with `unapply_patches()`. Treat the patched state as load
  bearing — never mix patched and unpatched `PQInnerData` objects in the
  same process.
- **Session files.** `*.session` and related journal/WAL files contain
  live login material. Keep them on disk with restrictive permissions
  (`chmod 600`) and never commit them. They are listed in `.gitignore`.

## Credential handling

- API id, API hash, DC host/port/id, and bot tokens are read from the
  environment (see `README.md` → Environment Variables). Defaults are
  Vibe's public app credentials; override them only with values you own.
- Never hardcode phone numbers, 2FA passwords, or tokens in source.
  Examples use the placeholder `YOUR_TOKEN_HERE`.
- Before every `git push`, run the project checklist:
  `grep -rnwiE '\b(ai|prompt|chatgpt|session|token|98912)\b' .`
  and confirm no personal data or AI traces are present.

## Hardening checklist

- [ ] `.env` is present locally and never committed.
- [ ] `.gitignore` contains `*.session`, `.env`, `*HANDOVER*`.
- [ ] `python scripts/check_syntax.py` passes.
- [ ] `pytest -v` passes.
- [ ] Telethon is within the pinned range (`>=1.36,<2.0`).
