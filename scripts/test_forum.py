# ============================================
#  scripts/test_forum.py - probe forum-topic support
#  Usage:
#    python -B scripts/test_forum.py <forum_username_or_id>
#  Full cycle: list topics -> create topic -> send in topic -> edit -> delete
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import os
import sys
import time

from userapi import VibeClient


PROBE_TIMEOUT = 25


def _label(s):
    return f"{s:45s}"


async def probe(name, coro_factory):
    try:
        result = await asyncio.wait_for(coro_factory(), timeout=PROBE_TIMEOUT)
        summary = _summarize(result)
        print(f"[OK]   {_label(name)} -> {summary}")
        return result, True
    except asyncio.TimeoutError:
        print(f"[TIME] {_label(name)} -> timeout")
        return None, False
    except Exception as e:
        print(f"[FAIL] {_label(name)} -> {type(e).__name__}: {str(e)[:160]}")
        return None, False


def _summarize(obj):
    if obj is None:
        return "None"
    t = type(obj).__name__
    if hasattr(obj, "topics") and hasattr(obj.topics, "topics"):
        return f"{t}(topics_count={len(obj.topics.topics)})"
    if hasattr(obj, "id"):
        return f"{t}(id={obj.id})"
    return t


async def main():
    if len(sys.argv) < 2:
        print("usage: python -B scripts/test_forum.py <forum_username_or_id>")
        return
    target = sys.argv[1]

    if os.getenv("VIBE_DEBUG") != "1":
        import logging
        logging.getLogger("telethon.network.mtprotosender").setLevel(logging.CRITICAL)
        logging.getLogger("telethon.network.connection.connection").setLevel(logging.CRITICAL)
        logging.getLogger("websockets").setLevel(logging.CRITICAL)

    c = VibeClient()
    created_topic_id = None
    created_msg_id = None
    try:
        await c.connect()
        me = await c.get_me()
        print(f"[+] connected as id={me.id} @{getattr(me, 'username', '-')}\n")

        try:
            ent = await c.get_entity(target)
            inp = await c.get_input_entity(ent)
            title = getattr(ent, "title", None) or getattr(ent, "username", "?")
            print(f"[i] target: {title} (id={ent.id})")
        except Exception as e:
            print(f"[forum] error: {type(e).__name__}: {e}")
            return

        print("\n--- list topics ---")
        r, ok = await probe(
            "messages.getForumTopics",
            lambda: c.get_forum_topics(peer=inp, offset_date=None,
                                       offset_id=0, offset_topic=0, limit=10),
        )
        topics = getattr(getattr(r, "topics", None), "topics", []) if r else []
        print(f"       got {len(topics)} topic(s)")
        for t in topics[:5]:
            print(f"         - id={getattr(t, 'id', '?')} title={getattr(t, 'title', '?')!r}")

        if not ok:
            print("\n[!] get_forum_topics failed; cannot proceed with write tests")
            return

        print("\n--- create topic ---")
        topic_title = f"pyvibe test {int(time.time()) % 100000}"
        r, ok = await probe(
            "messages.createForumTopic",
            lambda: c.create_forum_topic(
                channel=ent, title=topic_title,
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

        if created_topic_id:
            print("\n--- send message inside topic ---")
            r, ok = await probe(
                "send_message in topic",
                lambda: c.send_message(ent, "hello from topic",
                                       reply_to=created_topic_id),
            )
            if ok and r is not None:
                created_msg_id = getattr(r, "id", None)
                print(f"       msg_id={created_msg_id}")

        if created_topic_id:
            print("\n--- edit topic title ---")
            r, ok = await probe(
                "messages.editForumTopic",
                lambda: c.edit_forum_topic(
                    channel=ent, topic_id=created_topic_id,
                    title=topic_title + " (edited)",
                ),
            )

        if created_msg_id:
            print("\n--- delete test message ---")
            r, ok = await probe(
                "delete_messages",
                lambda: c.delete_messages(ent, [created_msg_id], revoke=True),
            )

        if created_topic_id:
            print("\n--- close topic ---")
            r, ok = await probe(
                "messages.editForumTopic (close)",
                lambda: c.edit_forum_topic(
                    channel=ent, topic_id=created_topic_id, closed=True,
                ),
            )

    except Exception as e:
        print(f"[test_forum] fatal: {type(e).__name__}: {e}")
    finally:
        await c.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
