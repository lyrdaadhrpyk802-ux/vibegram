# ============================================
#  userapi/tests/examples/login_interactive.py
#  Interactive login: phone + OTP (+ optional 2FA)
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import sys

from userapi import VibeClient


async def main():
    phone = input("Phone (with country code, e.g. +98912...): ").strip()
    phone = phone.replace(" ", "").replace("-", "")
    if not phone.startswith("+"):
        phone = "+" + phone.lstrip("0")
    if len(phone) < 8:
        print("[!] phone too short")
        return
    print(f"[i] using phone: {phone}")

    c = VibeClient()
    try:
        ok = await c.connect()
        if not ok:
            print("[!] connect failed")
            return
        print(f"[+] connected")

        authorized = await c._client.is_user_authorized()
        print(f"[+] is_user_authorized={authorized}")

        if not authorized:
            print(f"[>] sending code request to {phone}")
            await c._client.send_code_request(phone)
            code = input("OTP: ").strip()
            try:
                await c._client.sign_in(phone=phone, code=code)
            except Exception as e:
                err = str(e).lower()
                if "password" in err or "sessionpasswordneeded" in type(e).__name__.lower():
                    pw = input("2FA password: ").strip()
                    await c._client.sign_in(password=pw)
                else:
                    raise

        me = await c._client.get_me()
        if me is None:
            print("[!] get_me returned None")
            return
        print(f"[+] logged in: id={me.id} username={me.username} name={me.first_name}")

        # Single message test
        await c._client.send_message("me", "pyvibe: hello from Python")
        print("[+] test message sent to Saved Messages")

    except asyncio.TimeoutError:
        print("[-] TIMEOUT")
    except Exception as e:
        print(f"[!] {type(e).__name__}: {str(e)[:300]}")
    finally:
        await c.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(130)
