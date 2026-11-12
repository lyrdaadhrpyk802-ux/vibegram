# ============================================
#  examples/06_groups_channels.py - create group, enable forum
#  All code and comments are English. No emojis.
# ============================================
# این مثال نشان می دهد چطور یک سوپرگروه بسازید، فروم را فعال کنید
# و یک تاپیک در آن ایجاد کنید. در انتها گروه حذف می شود.
# توجه: این کار روی اکانت شما انجام می شود.

import asyncio
import time
import os
from telethon.tl.functions.channels import ToggleForumRequest, DeleteChannelRequest
from telethon.tl.types import InputChannel, InputPeerChannel
from userapi import VibeClient


async def main():
    c = VibeClient()
    group = None
    try:
        await c.connect()
        print("[+] متصل شد\n")

        title = f"گروه تست {int(time.time()) % 10000}"
        print(f"[i] ساخت گروه: {title}")
        
        # 1) ساخت سوپرگروه
        result = await c.create_channel(title=title, about="تست گروه", megagroup=True)
        
        # پیدا کردن گروه در پاسخ
        for u in result.updates:
            if hasattr(u, "channel"):
                group = u.channel
                break
        
        if not group:
            print("[!] خطا در ساخت گروه")
            return
            
        print(f"[+] گروه ساخته شد (id={group.id})")
        await asyncio.sleep(1)

        # 2) فعال سازی فروم
        print("[i] فعال سازی حالت فروم...")
        inp = await c.get_input_entity(group)
        if isinstance(inp, InputPeerChannel):
            input_ch = InputChannel(channel_id=inp.channel_id, access_hash=inp.access_hash)
        else:
            input_ch = inp
            
        await c.raw(ToggleForumRequest(channel=input_ch, enabled=True, tabs=False))
        print("[+] فروم فعال شد")
        await asyncio.sleep(1)

        # 3) ساخت تاپیک
        print("[i] ساخت تاپیک 'سوالات'...")
        r = await c.create_forum_topic(
            peer=inp, title="سوالات",
            random_id=int.from_bytes(os.urandom(8), "big", signed=True)
        )
        
        # پیدا کردن id تاپیک
        topic_id = None
        for u in getattr(r, "updates", []):
            if hasattr(u, "message"):
                topic_id = u.message.id
                break
                
        if topic_id:
            print(f"[+] تاپیک ساخته شد (id={topic_id})")
            # 4) ارسال پیام در تاپیک
            print("[i] ارسال پیام در تاپیک...")
            await c.send_message(group, "سلام به همه در تاپیک سوالات", reply_to=topic_id)
            print("[+] پیام فرستاده شد")
        
    except Exception as e:
        print(f"[!] خطا: {type(e).__name__}: {e}")
    finally:
        # 5) پاکسازی
        if group:
            print("\n[i] پاک کردن گروه...")
            try:
                inp = await c.get_input_entity(group)
                if isinstance(inp, InputPeerChannel):
                    ch = InputChannel(channel_id=inp.channel_id, access_hash=inp.access_hash)
                else:
                    ch = inp
                await c.raw(DeleteChannelRequest(channel=ch))
                print("[+] گروه پاک شد")
            except Exception as e:
                print(f"[!] خطا در پاک کردن: {e}")
                
        await c.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
