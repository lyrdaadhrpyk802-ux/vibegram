#!/usr/bin/env python3
# ============================================
#  scripts/vibe.py - Vibe Messenger CLI
#  Commands: me, dialogs, send, read, listen, login
#  All code and comments are English. No emojis.
# ============================================
import argparse
import asyncio
import sys

from telethon import events

from userapi import VibeClient


async def cmd_me(c):
    me = await c.get_me()
    print(f"id:       {me.id}")
    print(f"username: {me.username}")
    print(f"name:     {me.first_name}")


async def cmd_dialogs(c, limit):
    dialogs = await c.get_dialogs(limit=limit)
    for d in dialogs:
        print(f"{d.id:>15}  {d.name}")


async def cmd_send(c, peer, text):
    msg = await c.send_message(peer, text)
    print(f"sent msg_id={msg.id}")


async def cmd_read(c, peer, limit):
    for m in await c.get_messages(peer, limit=limit):
        print(f"[{m.id}] {m.text}")


async def cmd_listen(c):
    print("listening (Ctrl+C to exit)...")

    @c.raw.on(events.NewMessage())
    async def handler(event):
        m = event.message
        print(f"[{m.id}] {m.text}")

    await c.raw.run_until_disconnected()


async def cmd_login(c, phone):
    if await c.is_authorized():
        print("already authorized")
        return
    await c.request_code(phone)
    code = input("OTP: ").strip()
    try:
        await c.sign_in(phone, code)
    except Exception as e:
        if "password" in str(e).lower():
            pw = input("2FA password: ").strip()
            await c.sign_in(phone, code, password=pw)
        else:
            raise
    me = await c.get_me()
    print(f"logged in as {me.username or me.first_name}")


def build_parser():
    p = argparse.ArgumentParser(prog="vibe")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("me")
    sub.add_parser("listen")
    sub.add_parser("login").add_argument("phone")
    sp = sub.add_parser("dialogs"); sp.add_argument("--limit", type=int, default=20)
    sp = sub.add_parser("send"); sp.add_argument("peer"); sp.add_argument("text")
    sp = sub.add_parser("read"); sp.add_argument("peer"); sp.add_argument("--limit", type=int, default=10)
    return p


async def run(args):
    c = VibeClient()
    try:
        await c.connect()
        if args.cmd == "login":
            await cmd_login(c, args.phone)
        elif args.cmd == "me":
            await cmd_me(c)
        elif args.cmd == "dialogs":
            await cmd_dialogs(c, args.limit)
        elif args.cmd == "send":
            await cmd_send(c, args.peer, args.text)
        elif args.cmd == "read":
            await cmd_read(c, args.peer, args.limit)
        elif args.cmd == "listen":
            await cmd_listen(c)
    finally:
        await c.disconnect()


def main():
    p = build_parser()
    args = p.parse_args()
    try:
        asyncio.run(run(args))
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
