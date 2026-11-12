# ============================================
#  scripts/test_forum_full.py - full forum cycle test
#  Automatically:
#    1. creates a new supergroup
#    2. enables forum mode
#    3. lists topics
#    4. creates a topic
#    5. sends a message inside the topic
#    6. edits topic title
#    7. closes topic
#    8. deletes topic
#    9. deletes the supergroup (unless --keep)
#  Usage:
#    python -B scripts/test_forum_full.py            # full cycle, deletes group
#    python -B scripts/test_forum_full.py --keep     # keeps the group for inspection
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import os
import sys
import time

from userapi import VibeClient


PROBE_TIMEOUT = 30


def _l(s):
    return f"{s:45s}"


async def probe(name, coro_factory):
    try:
        result = await asyncio.wait_for(coro_factory(), timeout=PROBE_TIMEOUT)
        summary = _summarize(result)
        print(f"[OK]   {_l(name)} -> {summary}")
        return result, True
    except asyncio.TimeoutError:
        print(f"[TIME] {_l(name)} -> timeout {PROBE_TIMEOUT}s")
        return None, False
    except Exception as e:
        print(f"[FAIL] {_l(name)} -> {type(e).__name__}: {str(e)[:160]}")
        return None, False


def _summarize(obj):
    if obj is None:
        return "None"
    t = type(obj).__name__
    if hasattr(obj, "topics") and hasattr(obj.topics, "topics"):
        return f"{t}(topics={len(obj.topics.topics)})"
    if hasattr(obj, "id"):
        return f"{t}(id={obj.id})"
    return t


def _extract_channel_from_updates(updates):
    """Find the newly created Channel in a create_channel Updates."""
    for u in getattr(updates, "updates", []):
        ch = getattr(u, "channel", None)
        if ch is not None:
            return ch
        msg = getattr(u, "message", None)
        if msg is not None and hasattr(msg, "peer_id"):
            pid = msg.peer_id
            if hasattr(pid, "channel_id"):
                return pid.channel_id
    for ch in getattr(updates, "chats", []) or []:
        if getattr(ch, "megagroup", False) or getattr(ch, "broadcast", False):
            return ch
    return None


async def main():
    keep_group = "--keep" in sys.argv[1:]

    if os.getenv("VIBE_DEBUG") != "1":
        import logging
        logging.getLogger("telethon.network.mtprotosender").setLevel(logging.CRITICAL)
        logging.getLogger("telethon.network.connection.connection").setLevel(logging.CRITICAL)
        logging.getLogger("websockets").setLevel(logging.CRITICAL)

    c = VibeClient()
    group_entity = None
    created_topic_id = None
    created_msg_id = None
    cleanup_done = False

    try:
        await c.connect()
        me = await c.get_me()
        print(f"[+] connected as id={me.id} @{getattr(me, 'username', '-')}")
        print(f"[i] mode: {'KEEP group after test' if keep_group else 'DELETE group after test'}\n")

        # ---- 1) create supergroup ----
        title = f"pyvibe-forum-test-{int(time.time()) % 100000}"
        print("--- 1) create supergroup ---")
        r, ok = await probe(
            "channels.createChannel (megagroup)",
            lambda: c.create_channel(title=title, about="pyvibe forum test",
                                     megagroup=True, broadcast=False),
        )
        if not ok or r is None:
            print("[!] could not create group; aborting")
            return

        group_entity = _extract_channel_from_updates(r)
        if group_entity is None:
            print(f"[!] could not extract Channel from Updates: {r!r}")
            return

        # If we got only an id (int), fetch the entity
        if isinstance(group_entity, int):
            group_entity = await c.get_entity(group_entity)

        group_id = getattr(group_entity, "id", "?")
        print(f"       created group id={group_id} title={title!r}")
        await asyncio.sleep(1)  # give server a moment

        # ---- 2) enable forum ----
        print("\n--- 2) enable forum ---")
        from telethon.tl.functions.channels import ToggleForumRequest
        from telethon.tl.types import InputChannel, InputPeerChannel
        inp = await c.get_input_entity(group_entity)
        if isinstance(inp, InputPeerChannel):
            input_ch = InputChannel(channel_id=inp.channel_id, access_hash=inp.access_hash)
        else:
            input_ch = inp
        r, ok = await probe(
            "channels.toggleForum (tabs=False)",
            lambda: c.raw(ToggleForumRequest(channel=input_ch, enabled=True, tabs=False)),
        )
        if not ok:
            # try tabs=True (newer schema variant)
            r, ok = await probe(
                "channels.toggleForum (tabs=True)",
                lambda: c.raw(ToggleForumRequest(channel=input_ch, enabled=True, tabs=True)),
            )
        if not ok:
            print("[!] could not enable forum; aborting")
            return
        await asyncio.sleep(1)

        # ---- 3) list topics ----
        print("\n--- 3) list topics ---")
        r, ok = await probe(
            "messages.getForumTopics",
            lambda: c.get_forum_topics(peer=inp, offset_date=None,
                                       offset_id=0, offset_topic=0, limit=10),
        )
        topics = getattr(getattr(r, "topics", None), "topics", []) if r else []
        print(f"       got {len(topics)} topic(s)")
        for t in topics[:5]:
            print(f"         - id={getattr(t, 'id', '?')} title={getattr(t, 'title', '?')!r}")

        # ---- 4) create topic ----
        print("\n--- 4) create topic ---")
        topic_title = "bugs"
        r, ok = await probe(
            "messages.createForumTopic",
            lambda: c.create_forum_topic(
                peer=inp, title=topic_title,
                random_id=int.from_bytes(os.urandom(8), "big", signed=True),
            ),
        )
        if ok and r is not None:
            for u in getattr(r, "updates", []):
                msg = getattr(u, "message", None)
                if msg is not None and getattr(msg, "id", None):
                    created_topic_id = getattr(msg, "id")
                    break
        print(f"       created_topic_id={created_topic_id}")

        # ---- 5) send inside topic ----
        if created_topic_id:
            print("\n--- 5) send message in topic ---")
            r, ok = await probe(
                "send_message in topic",
                lambda: c.send_message(group_entity, "hello from forum topic",
                                       reply_to=created_topic_id),
            )
            if ok and r is not None:
                created_msg_id = getattr(r, "id", None)
                print(f"       msg_id={created_msg_id}")

        # ---- 6) edit topic ----
        if created_topic_id:
            print("\n--- 6) edit topic title ---")
            r, ok = await probe(
                "messages.editForumTopic (rename)",
                lambda: c.edit_forum_topic(
                    peer=inp, topic_id=created_topic_id,
                    title="bugs (renamed)",
                ),
            )

        # ---- 7) close topic ----
        if created_topic_id:
            print("\n--- 7) close topic ---")
            r, ok = await probe(
                "messages.editForumTopic (close)",
                lambda: c.edit_forum_topic(
                    peer=inp, topic_id=created_topic_id,
                    closed=True,
                ),
            )

        # ---- 8) delete topic ----
        if created_topic_id:
            print("\n--- 8) delete topic ---")
            try:
                from telethon.tl.functions.messages import DeleteTopicHistoryRequest
                r, ok = await probe(
                    "messages.deleteTopicHistory",
                    lambda: c.raw(DeleteTopicHistoryRequest(
                        peer=inp, top_msg_id=created_topic_id,
                    )),
                )
            except Exception as e:
                print(f"[skip] delete topic: {type(e).__name__}: {e}")

    except Exception as e:
        print(f"[test_forum_full] fatal: {type(e).__name__}: {e}")
    finally:
        # ---- 9) cleanup ----
        try:
            if group_entity is not None and not keep_group:
                print("\n--- 9) delete supergroup ---")
                from telethon.tl.functions.channels import DeleteChannelRequest
                from telethon.tl.types import InputChannel, InputPeerChannel
                try:
                    inp = await c.get_input_entity(group_entity)
                    if isinstance(inp, InputPeerChannel):
                        ch = InputChannel(channel_id=inp.channel_id, access_hash=inp.access_hash)
                    else:
                        ch = inp
                    r = await asyncio.wait_for(
                        c.raw(DeleteChannelRequest(channel=ch)), timeout=PROBE_TIMEOUT,
                    )
                    print(f"[OK]   delete_channel -> {type(r).__name__}")
                    cleanup_done = True
                except Exception as e:
                    print(f"[FAIL] delete_channel: {type(e).__name__}: {e}")
            elif group_entity is not None and keep_group:
                gid = getattr(group_entity, "id", "?")
                print(f"\n[i] group kept (id={gid}) for inspection")
        except Exception as e:
            print(f"[cleanup] {type(e).__name__}: {e}")

        if group_entity is not None and not cleanup_done and not keep_group:
            print(f"\n[!] AUTO-CLEANUP FAILED — manually delete group:")
            print(f"    title={title if 'title' in dir() else '?'}")

        await c.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
