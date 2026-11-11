# ============================================
#  userapi/tests/examples/login_example.py
#  Example: connect and login to Vibe
#  All code and comments are English. No emojis.
# ============================================
import asyncio
from userapi import VibeClient


async def main():
    client = VibeClient()
    try:
        ok = await client.connect()
        print(f"[+] connected={ok}")
        if not ok:
            return
        me = await client.login(phone="+98912XXXXXXX")
        print(f"[+] logged in as {me!r}")
        await client.send_message("me", "Hello from pyvibe")
        print("[+] message sent")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
