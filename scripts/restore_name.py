# ============================================
#  scripts/restore_name.py - restore original first/last name
#  Usage:
#    python -B scripts/restore_name.py                 # clear time suffix, keep current first_name
#    python -B scripts/restore_name.py "Ali" ""        # explicit
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import re
import sys

from userapi import VibeClient


_SUFFIX_RE = re.compile(r"[\u2022|]\s*\d{2}:\d{2}(?::\d{2})?\s*$")


async def main():
    explicit_first = sys.argv[1] if len(sys.argv) > 1 else None
    explicit_last = sys.argv[2] if len(sys.argv) > 2 else None

    c = VibeClient()
    try:
        await c.connect()
        me = await c.get_me()
        cur_first = getattr(me, "first_name", "") or ""
        cur_last = getattr(me, "last_name", "") or ""

        if explicit_first is None:
            # Strip "<sep>HH:MM" suffix from current first_name
            stripped = _SUFFIX_RE.sub("", cur_first).strip()
            new_first = stripped
        else:
            new_first = explicit_first

        new_last = explicit_last if explicit_last is not None else cur_last

        print(f"[i] current first_name={cur_first!r} last_name={cur_last!r}")
        print(f"[i] target  first_name={new_first!r} last_name={new_last!r}")
        await c.update_profile(
            first_name=new_first or None,
            last_name=new_last or None,
        )
        me2 = await c.get_me()
        print(f"[+] now first_name={getattr(me2, 'first_name', '')!r} "
              f"last_name={getattr(me2, 'last_name', '')!r}")
    except Exception as e:
        print(f"[restore_name] error: {type(e).__name__}: {e}")
    finally:
        await c.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
