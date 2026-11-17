# examples

Practical examples for the `vibegram` library.

## Directory layout

- `http_bot/` - examples using `VibeBotHTTP` (HTTP Bot API, Telegram-compatible)
- `legacy_mtproto_bots/` - examples using the legacy MTProto `VibeBot`
- `01_login.py` ... `24_privacy.py` - MTProto user-API examples (VibeClient)

## HTTP bots (recommended)

The `http_bot/` examples use the official HTTP Bot API at
`https://api.vibegram.chat`. They are Telegram-compatible: any code you wrote
for Telegram bots works here after swapping the base URL.

Set the token once:

```
export VIBE_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
```

Then run any example:

```
python -B examples/http_bot/01_echo.py
```

|File|What it shows|
|------|---------------|
| `01_echo.py` | Long polling and message echo |
| `02_inline_buttons.py` | Inline keyboards (callback_data + url) and callback queries |
| `03_reply_keyboard.py` | Bottom reply keyboard |
| `04_file_upload.py` | Send photo, document, and media group (album) |
| `05_file_download.py` | Download photos sent by users |
| `06_fsm_form.py` | Simple finite state machine (multi-step form) |
| `07_group_admin.py` | Ban/unban, pin/unpin in a group |
| `08_webhook_server.py` | Local aiohttp webhook receiver |

For `08_webhook_server.py`, you also need a public HTTPS URL:

```
export VIBE_WEBHOOK_URL="https://yourdomain.com/webhook"
```

## Legacy MTProto bots

`legacy_mtproto_bots/` contains examples for the older `VibeBot` MTProto
client. They are kept for reference, but the MTProto path has server-side
limitations (inline keyboards blocked, voice notes blocked, etc.). Prefer
`VibeBotHTTP` for new work.

## MTProto user-API examples

The numbered files at the top level (`01_login.py`, `02_send_message.py`,
...) exercise the user client `VibeClient` from `userapi/`. They require a
logged-in session (`~/.vibe_session.session`).
