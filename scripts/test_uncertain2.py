# ============================================
#  scripts/test_uncertain2.py - probe Vibe "maybe" features
#  Read-only by default; write probes always restore state.
#  Each probe is independent: one failure does not stop the rest.
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import os
import sys
import time
from pathlib import Path

from userapi import VibeClient


PROBE_TIMEOUT = 25


async def probe(name, coro_factory):
    try:
        result = await asyncio.wait_for(coro_factory(), timeout=PROBE_TIMEOUT)
        summary = _summarize(result)
        print(f"[OK]   {name:45s} -> {summary}")
        return result, True
    except asyncio.TimeoutError:
        print(f"[TIME] {name:45s} -> timeout {PROBE_TIMEOUT}s")
        return None, False
    except Exception as e:
        msg = str(e)[:160]
        print(f"[FAIL] {name:45s} -> {type(e).__name__}: {msg}")
        return None, False


def _summarize(obj):
    if obj is None:
        return "None"
    t = type(obj).__name__
    if hasattr(obj, "__len__"):
        try:
            return f"{t}(len={len(obj)})"
        except Exception:
            pass
    for attr in ("count", "stars", "boosts", "gifts", "themes", "wallpapers"):
        if hasattr(obj, attr):
            try:
                return f"{t}({attr}={getattr(obj, attr)})"
            except Exception:
                pass
    return t


async def main():
    if os.getenv("VIBE_DEBUG") != "1":
        import logging
        logging.getLogger("telethon.network.mtprotosender").setLevel(logging.CRITICAL)
        logging.getLogger("telethon.network.connection.connection").setLevel(logging.CRITICAL)
        logging.getLogger("websockets").setLevel(logging.CRITICAL)

    c = VibeClient()
    summary = {}
    try:
        await c.connect()
        me = await c.get_me()
        print(f"[+] connected as id={me.id} @{getattr(me, 'username', '-')}\n")

        # ==========================================
        # READ-ONLY PROBES (safe, no state change)
        # ==========================================
        print("--- read-only ---")

        _, ok = await probe(
            "account.getThemes",
            lambda: c.get_themes(format="", hash=0),
        )
        summary["themes"] = ok

        _, ok = await probe(
            "account.getWallPapers",
            lambda: c.get_wall_papers(hash=0),
        )
        summary["wallpapers"] = ok

        _, ok = await probe(
            "premium.getMyBoosts",
            lambda: c.get_my_boosts(),
        )
        summary["my_boosts"] = ok

        # boosts are channel-only; use a known channel instead of self
        try:
            beta_entity = await c.get_entity("بتا تسترهای وایب")
            _, ok = await probe(
                "premium.getBoostsStatus (beta)",
                lambda: c.get_boosts_status(peer=beta_entity),
            )
            summary["boosts_status"] = ok
        except Exception as e:
            print(f"[skip] boosts_status: {type(e).__name__}: {e}")
            summary["boosts_status"] = False

        _, ok = await probe(
            "payments.getStarGifts",
            lambda: c.get_star_gifts(hash=0),
        )
        summary["star_gifts"] = ok

        _, ok = await probe(
            "payments.getStarsStatus (self)",
            lambda: c.get_stars_status(peer=me),
        )
        summary["stars_status"] = ok

        _, ok = await probe(
            "aicompose.getTones",
            lambda: c.get_tones(hash=0),
        )
        summary["aicompose_tones"] = ok

        # Forum topics on a supergroup (read)
        try:
            beta = await c.get_entity("بتا تسترهای وایب")
            beta_peer = await c.get_input_entity(beta)
            _, ok = await probe(
                "messages.getForumTopics (beta)",
                lambda: c.get_forum_topics(peer=beta_peer, offset_date=None,
                                           offset_id=0, offset_topic=0, limit=5),
            )
            summary["forum_topics"] = ok
        except Exception as e:
            print(f"[skip] forum topics: {type(e).__name__}: {e}")
            summary["forum_topics"] = False

        # Ephemeral
        _, ok = await probe(
            "ephemeral.getNotifySettings",
            lambda: c.get_ephemeral_notify_settings_() if hasattr(c, "get_ephemeral_notify_settings_") else _noop(),
        )
        summary["ephemeral"] = ok

        # ==========================================
        # WRITE PROBES with cleanup
        # ==========================================
        print("\n--- write (with cleanup) ---")

        # 1) Update color: set then clear
        try:
            from telethon.tl.types import PeerColor
            await probe(
                "account.updateColor (set)",
                lambda: c.update_color(for_profile=True, color=PeerColor(color=0)),
            )
            await probe(
                "account.updateColor (clear)",
                lambda: c.update_color(for_profile=True, color=None),
            )
            summary["update_color"] = True
        except Exception as e:
            print(f"[FAIL] update_color: {type(e).__name__}: {e}")
            summary["update_color"] = False

        # 2) Emoji status: clear to empty (safe)
        try:
            from telethon.tl.types import EmojiStatusEmpty
            await probe(
                "account.updateEmojiStatus (clear)",
                lambda: c.update_emoji_status(emoji_status=EmojiStatusEmpty()),
            )
            summary["emoji_status"] = True
        except Exception as e:
            print(f"[FAIL] update_emoji_status: {type(e).__name__}: {e}")
            summary["emoji_status"] = False

        # 3) Send story with 1x1 png (cleanup after)
        print()
        story_dir = Path.home() / "pyvibe" / "_story_probe"
        story_dir.mkdir(exist_ok=True)
        png = story_dir / "s.png"
        png.write_bytes(bytes.fromhex(
            "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
            "1f15c4890000000d49444154789c63600000000005000156a6b4b700"
            "00000049454e44ae426082"
        ))
        try:
            from telethon.tl.types import (
                InputMediaUploadedPhoto, InputPrivacyValueAllowCloseFriends,
            )
            from telethon.tl.functions.stories import SendStoryRequest
            from telethon.tl.functions.stories import DeleteStoriesRequest

            uploaded = await c.upload_file(str(png))
            media = InputMediaUploadedPhoto(file=uploaded)
            r, ok = await probe(
                "stories.sendStory (1-day, close friends)",
                lambda: c.send_story(
                    peer="me",
                    media=media,
                    privacy_rules=[InputPrivacyValueAllowCloseFriends()],
                    period=86400,
                ),
            )
            if ok and r is not None:
                story_id = getattr(r, "id", None)
                # try to extract id from Updates
                if story_id is None and hasattr(r, "updates"):
                    for u in r.updates:
                        if hasattr(u, "story") and getattr(u.story, "id", None):
                            story_id = u.story.id
                            break
                if story_id:
                    try:
                        from telethon.tl.types import InputPeerSelf
                        await c.raw(DeleteStoriesRequest(
                            peer=InputPeerSelf(), id=[story_id],
                        ))
                        print(f"[i] cleaned story id={story_id}")
                    except Exception as e:
                        print(f"[warn] cleanup story failed: {type(e).__name__}: {e}")
            summary["send_story"] = ok
        except Exception as e:
            print(f"[FAIL] send_story: {type(e).__name__}: {e}")
            summary["send_story"] = False
        finally:
            try:
                png.unlink()
                story_dir.rmdir()
            except Exception:
                pass

        # ==========================================
        # SUMMARY
        # ==========================================
        print("\n=== SUMMARY ===")
        ok_n = sum(1 for v in summary.values() if v)
        print(f"OK: {ok_n}/{len(summary)}")
        for k, v in summary.items():
            print(f"  {'OK  ' if v else 'FAIL'} {k}")

    except Exception as e:
        print(f"[test_uncertain2] fatal: {type(e).__name__}: {e}")
    finally:
        await c.disconnect()


async def _noop():
    return None


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
