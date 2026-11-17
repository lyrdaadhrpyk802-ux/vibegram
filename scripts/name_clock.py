# ============================================
#  scripts/name_clock.py - live clock in first_name
#  Updates first_name to "<original>•HH:MM" (Tehran time) every 70s.
#  Restores original name on Ctrl+C or SIGTERM.
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import os
import signal
import sys
from datetime import datetime, timedelta, timezone

from telethon.errors import FloodWaitError

from userapi import VibeClient


# Iran: fixed offset UTC+3:30 (no DST since 2022). Using a fixed offset
# avoids relying on the tzdata package being installed on Termux.
TEHRAN = timezone(timedelta(hours=3, minutes=30))

UPDATE_INTERVAL = 70.0          # seconds between updates
SEPARATOR = "\u2022"            # bullet
FIRST_NAME_MAX = 64             # Telegram limit (bytes for safety we use chars)


def _tehran_hhmm():
    return datetime.now(TEHRAN).strftime("%H:%M")


def _build_first_name(base, hhmm):
    """Compose base + separator + HH:MM, truncating base if needed."""
    suffix = f"{SEPARATOR}{hhmm}"
    room = FIRST_NAME_MAX - len(suffix)
    if room < 1:
        return suffix[-FIRST_NAME_MAX:]
    return base[:room] + suffix


async def main():
    if os.getenv("VIBE_DEBUG") != "1":
        import logging
        logging.getLogger("telethon.network.mtprotosender").setLevel(logging.CRITICAL)
        logging.getLogger("telethon.network.connection.connection").setLevel(logging.CRITICAL)
        logging.getLogger("websockets").setLevel(logging.CRITICAL)

    c = VibeClient()
    stop_event = asyncio.Event()

    def _stop(*_):
        stop_event.set()

    try:
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, _stop)
            except NotImplementedError:
                # Termux/android fallback
                signal.signal(sig, lambda *_: stop_event.set())

        await c.connect()

        me = await c.get_me()
        original_first = getattr(me, "first_name", "") or ""
        original_last = getattr(me, "last_name", "") or ""
        base = original_first.strip()

        print(f"[+] connected as id={me.id} @{getattr(me, 'username', '-')}")
        print(f"[+] original first_name = {original_first!r}")
        print(f"[+] original last_name  = {original_last!r}")
        print(f"[+] base = {base!r}")
        print(f"[+] updating every {int(UPDATE_INTERVAL)}s to '{base}{SEPARATOR}HH:MM' (Tehran)")
        print("[+] Ctrl+C to stop and restore\n")

        last_sent = None

        while not stop_event.is_set():
            hhmm = _tehran_hhmm()
            new_first = _build_first_name(base, hhmm)

            if new_first == last_sent:
                # Avoid redundant update_profile calls when minute didn't
                # change (can happen due to 70s interval).
                if os.getenv("NAME_DEBUG") == "1":
                    print(f"[debug] skipping unchanged name {new_first!r}")
            else:
                try:
                    await c.update_profile(
                        first_name=new_first,
                        last_name=original_last or None,
                    )
                    last_sent = new_first
                    print(f"[+] name -> {new_first!r}")
                except FloodWaitError as e:
                    wait_s = getattr(e, "seconds", 60) + 5
                    print(f"[!] FLOOD_WAIT {wait_s}s, backing off")
                    try:
                        await asyncio.wait_for(stop_event.wait(), timeout=wait_s)
                    except asyncio.TimeoutError:
                        pass
                    continue
                except Exception as e:
                    print(f"[!] update_profile failed: {type(e).__name__}: {e}")

            # Wait the remaining interval, but wake up early on Ctrl+C
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=UPDATE_INTERVAL)
            except asyncio.TimeoutError:
                pass

        print("\n[i] stopping, restoring original name...")
        try:
            await c.update_profile(
                first_name=original_first or None,
                last_name=original_last or None,
            )
            print(f"[+] restored first_name={original_first!r} last_name={original_last!r}")
        except Exception as e:
            print(f"[!] restore failed: {type(e).__name__}: {e}")
            print(f"    run: python -B scripts/restore_name.py")
    except Exception as e:
        print(f"[name_clock] fatal: {type(e).__name__}: {e}")
    finally:
        try:
            await c.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
