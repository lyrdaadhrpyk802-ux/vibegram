# ============================================
#  examples/23_download_profile.py - Download Avatar
#  All code and comments are English. No emojis.
# ============================================
# این مثال نشان می‌دهد چطور عکس پروفایل یک کاربر یا کانال را دانلود کنید.

import asyncio
import os
from userapi import VibeClient

async def main():
    async with VibeClient() as client:
        print("[+] متصل شد.")
        
        target = "@username"  # یوزرنیم یا آیدی
        print(f"[i] در حال دانلود عکس پروفایل {target}...")
        
        # دانلود عکس در پوشه فعلی
        path = await client.download_profile_photo(target, file=f"{target}_avatar.jpg")
        
        if path:
            print(f"[+] عکس با موفقیت در این مسیر ذخیره شد: {path}")
        else:
            print("[-] این کاربر عکس پروفایل ندارد.")

if __name__ == "__main__":
    asyncio.run(main())
