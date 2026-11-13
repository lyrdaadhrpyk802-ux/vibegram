# ============================================
#  examples/user_api_master/130_scenario_send_bulk_messages.py - ارسال پیام به چند مخاطب (با تاخیر)
#  All code and comments are English. No emojis.
# ============================================
# این یک سناریوی واقعی است. برای اجرا باید لاگین باشید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected.")
        try:
            # استفاده از sleep
            print("[i] این بخش نیاز به تکمیل منطق توسط شما دارد.")
        except Exception as e:
            print(f"[!] Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
