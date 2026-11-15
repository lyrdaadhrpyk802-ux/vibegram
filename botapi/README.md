# botapi

Two Bot client implementations for Vibe Messenger:

- `VibeBot` - MTProto bot client (Telethon-based, `botapi/client.py`).
- `VibeBotHTTP` - HTTP Bot API client, Telegram-compatible (`botapi/http_client.py`).

## Which one to use

Use **`VibeBotHTTP`** for new projects. It is fully compatible with the
official Vibe Bot API (`https://api.vibegram.chat`) and inherits all
Telegram Bot API conventions: JSON responses, camelCase method names,
`ok`/`result`/`error_code` envelopes.

Use `VibeBot` only if you specifically need MTProto-level control.

## Quick start (VibeBotHTTP)

```python
import asyncio
from botapi import VibeBotHTTP

async def main():
    async with VibeBotHTTP("YOUR_BOT_TOKEN") as bot:
        me = await bot.get_me()
        print("connected as", me["username"])
        await bot.send_message(chat_id=123456789, text="hello")

asyncio.run(main())
```

## Long polling

```python
async def echo():
    async with VibeBotHTTP("YOUR_BOT_TOKEN") as bot:
        async for update in bot.poll_updates(timeout=30):
            msg = update.get("message")
            if msg and msg.get("text"):
                await bot.send_message(
                    chat_id=msg["chat"]["id"],
                    text=f"echo: {msg['text']}",
                )
```

## Inline buttons

```python
await bot.send_message(
    chat_id=123456789,
    text="choose:",
    reply_markup={
        "inline_keyboard": [
            [{"text": "Button 1", "callback_data": "btn1"}],
            [{"text": "Website", "url": "https://vibegram.chat"}],
        ]
    },
)
```

Answer callback queries with `bot.answer_callback_query(callback_query_id, text="ok")`.

## Reply keyboard

```python
await bot.send_message(
    chat_id=123456789,
    text="menu",
    reply_markup={
        "keyboard": [[{"text": "A"}, {"text": "B"}]],
        "resize_keyboard": True,
    },
)
```

## Uploading files

Any method that takes a media parameter (`photo`, `document`, `video`,
`audio`, `voice`, `sticker`, ...) accepts:

- `str` or `Path` - local file path (multipart/form-data upload)
- `bytes` - raw bytes (multipart)
- file-like object with `.read()`
- a `file_id` string previously returned by the API

```python
from pathlib import Path
await bot.send_photo(chat_id=123456789, photo=Path("cat.jpg"), caption="cat")
await bot.send_document(chat_id=123456789, document=b"raw bytes")
```

### Albums

Local files are auto-converted to `attach://N` refs:

```python
await bot.send_media_group(
    chat_id=123456789,
    media=[
        {"type": "photo", "media": Path("a.jpg"), "caption": "one"},
        {"type": "photo", "media": Path("b.jpg"), "caption": "two"},
    ],
)
```

## Downloading files

```python
data = await bot.download_file(file_id="...")                 # bytes
await bot.download_file(file_id="...", dest=Path("out.bin"))  # write to disk
```

## Errors

```python
from botapi import VibeBotAPIError
try:
    await bot.send_message(chat_id=1, text="hi")
except VibeBotAPIError as e:
    print(e.error_code, e.description)
```

## Webhook

```python
await bot.set_webhook(url="https://yourdomain.com/vibe-webhook/",
                      secret_token="random-secret")
info = await bot.get_webhook_info()
await bot.delete_webhook(drop_pending_updates=False)
```

## Server feature matrix (verified against api.vibegram.chat)

### Working

- Identity: `getMe`, `getMyName`, `setMyName`, `getMyDescription`,
  `setMyDescription`, `getMyShortDescription`, `setMyShortDescription`
- Commands: `getMyCommands`, `setMyCommands`, `deleteMyCommands`
- Menu: `getChatMenuButton`, `setChatMenuButton`
- Admin rights: `getMyDefaultAdministratorRights`,
  `setMyDefaultAdministratorRights`
- Messages: `sendMessage`, `editMessageText`, `editMessageReplyMarkup`,
  `deleteMessage`, `deleteMessages`, `forwardMessage`, `forwardMessages`,
  `copyMessage`, `copyMessages`
- Media: `sendPhoto`, `sendDocument`, `sendMediaGroup` (file upload OK)
- Polls / dice: `sendPoll`, `sendDice`
- Reactions: `setMessageReaction`
- Actions: `sendChatAction`
- Pinning: `pinChatMessage`, `unpinChatMessage`
- Chat info: `getChat`, `getChatMember`, `getChatMemberCount`,
  `getUserProfilePhotos`
- Files: `getFile`, plus `download_file` helper
- Webhook: `setWebhook`, `getWebhookInfo`, `deleteWebhook`
- Updates: `getUpdates` (long polling)
- Misc: `getForumTopicIconStickers`, `getAvailableGifts`,
  `getStarTransactions`
- Callback / inline: `answerCallbackQuery`, `answerInlineQuery`
- Inline keyboards (callback_data and url) and reply keyboards

### Not working / unknown (server-side limitations)

- `sendLocation`, `sendVenue`, `sendContact` - return
  `EPHEMERAL_TARGET_REQUIRED` unless `chat_id="me"` and `receiver_user_id`
  are both supplied; even then the media payload format is rejected with
  `MEDIA_INVALID`. The required schema is not documented.
- `sendRichMessage` - server recognises the method but every block shape
  we tried returned `RICH_MESSAGE_BLOCKS_UNSUPPORTED` or
  `RICH_MESSAGE_INVALID`. Block schema not publicly documented.
- `stopPoll` - always returns `400 BAD_REQUEST`, regardless of parameters.
  Likely a server bug.
- `getChatAdministrators` - only works on groups/channels, not on private
  chats (expected).

### Untested

Generated and exposed, but not yet exercised end-to-end:

- Sticker set management (`getStickerSet`, `createNewStickerSet`, ...)
- Payments (`sendInvoice`, `refundStarPayment`, `answerPreCheckoutQuery`,
  `editUserStarSubscription`)
- Gifts (`sendGift`, `giftPremiumSubscription`)
- Games (`sendGame`, `setGameScore`, `getGameHighScores`)
- Boosts (`getUserChatBoosts`)
- Business (`getBusinessConnection`)
- Forum topic CRUD
- Invite link management and join requests
- Moderation (`banChatMember`, `restrictChatMember`, `promoteChatMember`,
  `setChatPermissions`, ...)

The client is ready for these; they have just not been validated against
the live server yet.

## Regenerating methods

`botapi/http_methods.py` is auto-generated. After editing the spec:

```
python -B scripts/gen_http_methods.py
python -c "import ast; ast.parse(open('botapi/http_methods.py').read())"
```

## Notes on the MTProto client (VibeBot)

Legacy `VibeBot` (MTProto) has server-side limitations that do NOT apply to
`VibeBotHTTP`:

- Inline keyboards blocked for non-official bots (`BUTTON_INVALID`).
- Voice notes blocked for bots (`ChatSendVoicesForbiddenError`).
- Bot login via `sign_in(bot_token=...)`.

Prefer `VibeBotHTTP` for all new work.
