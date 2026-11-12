# ============================================
#  scripts/chat_info.py - "info" helper
#  Listens for "info" messages you send in any chat and replies with a
#  full dump: users / groups / channels / supergroups.
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import os
import sys
from datetime import datetime, timezone

from telethon import events
from telethon.tl.functions.messages import GetFullChatRequest
from telethon.tl.types import (
    User, UserEmpty, Channel, ChannelForbidden,
    Chat, ChatForbidden,
)

from userapi import VibeClient

# Silence benign Telethon shutdown noise (WebSocket ConnectionClosedOK) unless
# explicitly debugging. This is not part of INFO_DEBUG; keep the terminal clean.
if os.getenv("VIBE_DEBUG") != "1":
    import logging
    logging.getLogger("telethon.network.mtprotosender").setLevel(logging.CRITICAL)
    logging.getLogger("telethon.network.connection.connection").setLevel(logging.CRITICAL)
    logging.getLogger("websockets").setLevel(logging.CRITICAL)


def _fmt_date(dt):
    if dt is None:
        return "?"
    if isinstance(dt, datetime):
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return str(dt)


def _status_str(user):
    s = getattr(user, "status", None)
    if s is None:
        return "?"
    name = type(s).__name__
    if name == "UserStatusOnline":
        return f"online until {_fmt_date(getattr(s, 'expires', None))}"
    if name == "UserStatusOffline":
        return f"offline (last seen {_fmt_date(getattr(s, 'was_online', None))})"
    if name == "UserStatusRecently":
        return "recently"
    if name == "UserStatusLastWeek":
        return "last week"
    if name == "UserStatusLastMonth":
        return "last month"
    return name


async def info_user(client, user):
    lines = ["=== USER INFO ===", f"id: {user.id}"]
    lines.append(f"username: @{user.username}" if getattr(user, "username", None) else "username: -")
    lines.append(f"first_name: {getattr(user, 'first_name', None) or '-'}")
    lines.append(f"last_name: {getattr(user, 'last_name', None) or '-'}")
    lines.append(f"phone: {getattr(user, 'phone', None) or '-'}")
    lines.append(f"bot: {bool(getattr(user, 'bot', False))}")
    lines.append(f"verified: {bool(getattr(user, 'verified', False))}")
    lines.append(f"premium: {bool(getattr(user, 'premium', False))}")
    lines.append(f"deleted: {bool(getattr(user, 'deleted', False))}")
    lines.append(f"status: {_status_str(user)}")

    if not isinstance(user, UserEmpty):
        try:
            full = await client.get_full_user(user)
            fu = getattr(full, "full_user", None)
            if fu is not None:
                lines.append(f"about: {getattr(fu, 'about', None) or '-'}")
                lines.append(f"common_chats: {getattr(fu, 'common_chats_count', 0)}")
                lines.append(f"blocked: {bool(getattr(fu, 'blocked', False))}")
                lines.append(f"phone_calls_available: {getattr(fu, 'phone_calls_available', '?')}")
                lines.append(f"voice_messages_forbidden: {bool(getattr(fu, 'voice_messages_forbidden', False))}")
        except Exception as e:
            lines.append(f"(full_user fetch failed: {type(e).__name__}: {e})")
    return "\n".join(lines)


async def info_group(client, chat):
    lines = ["=== GROUP INFO ===", f"id: {chat.id}"]
    lines.append(f"title: {getattr(chat, 'title', '-')}")
    lines.append(f"participants_count: {getattr(chat, 'participants_count', '?')}")
    lines.append(f"date: {_fmt_date(getattr(chat, 'date', None))}")
    lines.append(f"creator: {bool(getattr(chat, 'creator', False))}")
    lines.append(f"kicked: {bool(getattr(chat, 'kicked', False))}")
    lines.append(f"deactivated: {bool(getattr(chat, 'deactivated', False))}")
    lines.append(f"version: {getattr(chat, 'version', '?')}")

    try:
        r = await client.raw(GetFullChatRequest(chat_id=chat.id))
        fc = getattr(r, "full_chat", None)
        if fc is not None:
            lines.append(f"about: {getattr(fc, 'about', None) or '-'}")
            parts = getattr(fc, "participants", None)
            if parts is not None:
                lines.append(f"participants_loaded: {len(getattr(parts, 'participants', []) or [])}")
            lines.append(f"can_set_username: {bool(getattr(fc, 'can_set_username', False))}")
            lines.append(f"can_set_stickers: {bool(getattr(fc, 'can_set_stickers', False))}")
            lines.append(f"can_set_location: {bool(getattr(fc, 'can_set_location', False))}")
            lines.append(f"hidden_prehistory: {bool(getattr(fc, 'hidden_prehistory', False))}")
    except Exception as e:
        lines.append(f"(full_chat fetch failed: {type(e).__name__}: {e})")
    return "\n".join(lines)


async def info_channel(client, channel):
    is_megagroup = bool(getattr(channel, "megagroup", False))
    is_broadcast = bool(getattr(channel, "broadcast", False))
    if is_megagroup:
        kind = "SUPERGROUP"
    elif is_broadcast:
        kind = "CHANNEL"
    else:
        kind = "CHANNEL/GROUP"

    lines = [f"=== {kind} INFO ===", f"id: {channel.id}"]
    lines.append(f"title: {getattr(channel, 'title', '-')}")
    if getattr(channel, "username", None):
        lines.append(f"username: @{channel.username}")
    else:
        lines.append("username: -")
    lines.append(f"broadcast: {is_broadcast}")
    lines.append(f"megagroup: {is_megagroup}")
    lines.append(f"verified: {bool(getattr(channel, 'verified', False))}")
    lines.append(f"scam: {bool(getattr(channel, 'scam', False))}")
    lines.append(f"fake: {bool(getattr(channel, 'fake', False))}")
    lines.append(f"restricted: {bool(getattr(channel, 'restricted', False))}")
    lines.append(f"signatures: {bool(getattr(channel, 'signatures', False))}")
    lines.append(f"date: {_fmt_date(getattr(channel, 'date', None))}")
    lines.append(f"creator: {bool(getattr(channel, 'creator', False))}")
    lines.append(f"left: {bool(getattr(channel, 'left', False))}")
    lines.append(f"kicked: {bool(getattr(channel, 'kicked', False))}")
    if getattr(channel, "linked_chat_id", None):
        lines.append(f"linked_chat_id: {channel.linked_chat_id}")
    if getattr(channel, "slowmode_seconds", None):
        lines.append(f"slowmode_seconds: {channel.slowmode_seconds}")

    if isinstance(channel, ChannelForbidden):
        lines.append("(ChannelForbidden: no full info available)")
        return "\n".join(lines)

    # creator/admin flag check
    try:
        admin_rights = getattr(channel, "admin_rights", None)
        if admin_rights is not None:
            lines.append(f"admin_rights: {admin_rights}")
    except Exception:
        pass

    try:
        full = await client.get_full_channel(channel)
        fc = getattr(full, "full_chat", None)
        if fc is not None:
            for key in [
                "about", "participants_count", "online_count",
                "admins_count", "kicked_count", "banned_count",
                "can_view_participants", "can_set_username",
                "can_set_stickers", "hidden_prehistory",
                "can_set_location", "has_scheduled",
            ]:
                v = getattr(fc, key, None)
                if isinstance(v, bool):
                    lines.append(f"{key}: {v}")
                elif v not in (None, ""):
                    lines.append(f"{key}: {v}")
    except Exception as e:
        lines.append(f"(full_channel fetch failed: {type(e).__name__}: {e})")
    return "\n".join(lines)


async def collect_info(client, entity):
    if isinstance(entity, (User, UserEmpty)):
        return await info_user(client, entity)
    if isinstance(entity, (Channel, ChannelForbidden)):
        return await info_channel(client, entity)
    if isinstance(entity, (Chat, ChatForbidden)):
        return await info_group(client, entity)
    return f"=== UNKNOWN entity: {type(entity).__name__} ==="


async def main():
    c = VibeClient()
    try:
        await c.connect()
        me = await c.get_me()
        print(f"[+] connected as id={me.id} @{me.username}")
        print("[+] listening for 'info' / '/info' messages (yours only)")
        print("    Ctrl+C to stop\n")

        debug = os.getenv("INFO_DEBUG") == "1"

        @c.raw.on(events.NewMessage())
        async def handler(event):
            text = (event.raw_text or "").strip().lower()
            if text not in ("info", "/info", ".info"):
                return

            # Robust chat resolution (channels sometimes need fallback)
            chat = await event.get_chat()
            if chat is None and getattr(event, "chat_id", None) is not None:
                try:
                    chat = await c.get_entity(event.chat_id)
                except Exception:
                    chat = None
            if chat is None:
                if debug:
                    print(f"[debug] 'info' msg with no chat: chat_id={getattr(event, 'chat_id', None)}")
                return

            # Robust sender detection: works for users, groups, supergroups,
            # and channels (both as-user and anonymous-as-channel posts).
            sender = None
            try:
                sender = await event.get_sender()
            except Exception:
                sender = None

            out = getattr(event, "out", None)
            sender_id = getattr(sender, "id", None) if sender is not None else None
            chat_id = getattr(chat, "id", None)

            is_mine = (
                out is True
                or sender_id == me.id
                or (chat_id is not None and sender_id == chat_id)
            )

            if debug:
                print(f"[debug] 'info' in chat_id={chat_id} "
                      f"sender_id={sender_id} out={out} is_mine={is_mine}")

            if not is_mine:
                return

            try:
                info = await collect_info(c, chat)
            except Exception as e:
                info = f"[chat_info] error: {type(e).__name__}: {e}"

            title = getattr(chat, "title", None) or getattr(chat, "username", None) or getattr(chat, "id", "?")
            if debug:
                print("\n" + info + "\n")

            try:
                await event.reply(info)
                print(f"[+] info sent -> {title}")
            except Exception as e:
                print(f"[chat_info] reply failed: {type(e).__name__}: {e}")
                try:
                    await c.send_message(chat, info)
                    print(f"[+] info sent (fallback) -> {title}")
                except Exception as e2:
                    print(f"[chat_info] send_message also failed: {type(e2).__name__}: {e2}")

        await c.raw.run_until_disconnected()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"[chat_info] fatal: {type(e).__name__}: {e}")
    finally:
        await c.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
