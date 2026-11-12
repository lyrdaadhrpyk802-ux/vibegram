# ============================================
#  scripts/test_2fa_login.py - test automatic 2FA login
#  Uses a fresh temporary session file to test the login flow.
#  All code and comments are English. No emojis.
# ============================================
# این اسکریپت برای تست لاگین با تایید دو مرحله ای (2FA) است.
# از یک نشست موقت استفاده می‌کند و به نشست اصلی شما کاری ندارد.

import asyncio
import os
from pathlib import Path
from userapi import VibeClient

async def main():
    # Define a temporary session path for testing
    test_session = Path.home() / ".vibe_session_2fa_test"
    
    # Remove old test session if it exists to force a fresh login
    if test_session.with_suffix(".session").exists():
        test_session.with_suffix(".session").unlink()
        
    print("[i] Starting fresh session test...")
    c = VibeClient(session_path=test_session)
    
    try:
        await c.connect()
        
        if await c.is_authorized():
            print("[!] Already authorized (this shouldn't happen with a new session).")
            return

        phone = input("Phone number (with country code, e.g., +98912...): ").strip()
        phone = phone.replace(" ", "").replace("-", "")
        if not phone.startswith("+"):
            phone = "+" + phone.lstrip("0")

        print("\n[+] Calling the new login() method...")
        # This will automatically handle OTP and 2FA password prompts
        me = await c.login(phone)
        
        print(f"\n[+] LOGIN SUCCESSFUL!")
        print(f"    Name: {me.first_name}")
        print(f"    ID: {me.id}")
        print(f"    Username: @{getattr(me, 'username', '-')}")
        
    except Exception as e:
        print(f"\n[!] Login failed: {type(e).__name__}: {e}")
    finally:
        await c.disconnect()
        # Cleanup the test session so it doesn't linger
        if test_session.with_suffix(".session").exists():
            test_session.with_suffix(".session").unlink()
            print("\n[i] Temporary test session deleted.")

if __name__ == "__main__":
    asyncio.run(main())
