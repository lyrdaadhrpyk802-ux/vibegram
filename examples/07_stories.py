# ============================================
#  examples/07_stories.py - read stories
#  All code and comments are English. No emojis.
# ============================================
# این مثال نشان می‌دهد چطور استوری های خودتان و مخاطبین را بخوانید.

import asyncio
from userapi import VibeClient


async def main():
    c = VibeClient()
    try:
        await c.connect()
        print("[+] متصل شد\n")

        # 1) خواندن استوری های خودتان
        print("[+] استوری های شما:")
        my_stories = await c.get_peer_stories("me")
        
        count = 0
        if hasattr(my_stories, "stories"):
            for story in my_stories.stories:
                date = getattr(story, "date", "")
                print(f"    - id={story.id} (تاریخ: {date})")
                count += 1
                
        if count == 0:
            print("    (شما استوری ندارید)")

        # 2) خواندن استوری های همه
        print("\n[+] دریافت استوری های جدید از مخاطبین:")
        # (در Vibe این متد ممکن است خالی برگردد اگر کسی استوری نگذاشته باشد)
        all_stories = await c.get_all_stories()
        
        if hasattr(all_stories, "peer_stories"):
            print(f"    تعداد مخاطبین دارای استوری: {len(all_stories.peer_stories)}")
            for ps in all_stories.peer_stories[:3]:
                peer_id = getattr(ps.peer, "user_id", getattr(ps.peer, "channel_id", "?"))
                stories_count = len(getattr(ps, "stories", []))
                print(f"    - peer_id={peer_id} ({stories_count} استوری)")
        else:
            print("    (استوری جدیدی یافت نشد)")

    finally:
        await c.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
