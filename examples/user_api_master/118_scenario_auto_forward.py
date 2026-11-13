# ============================================
#  examples/user_api_master/118_scenario_auto_forward.py - فوروارد خودکار از یک چت به چت دیگر
#  All code and comments are English. No emojis.
# ============================================
# این یک سناریوی واقعی است. برای اجرا باید لاگین باشید.

import asyncio
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] Connected.")
        try:
            # گوش دادن به آپدیت‌ها و فوروارد
            print("[i] این بخش نیاز به تکمیل منطق توسط شما دارد.")
        except Exception as e:
            print(f"[!] Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
