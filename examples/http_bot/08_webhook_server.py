# ============================================
#  examples/http_bot/08_webhook_server.py - Running a local webhook server
#  All code and comments are English. No emojis.
# ============================================
import asyncio
import os
import sys
from aiohttp import web

from botapi import VibeBotHTTP

async def handle_webhook(request):
    try:
        update = await request.json()
        print(f"[webhook] received update: {update.get('update_id')}")
        msg = update.get("message")
        if msg and msg.get("text"):
            print(f"[webhook] message text: {msg['text']}")
    except Exception as e:
        print(f"[webhook] error: {e}")
    return web.Response(text="ok")

async def main():
    token = os.getenv("VIBE_BOT_TOKEN", "").strip()
    webhook_url = os.getenv("VIBE_WEBHOOK_URL", "").strip()
    
    if not token:
        print("[webhook] error: set VIBE_BOT_TOKEN")
        sys.exit(1)
    if not webhook_url:
        print("[webhook] error: set VIBE_WEBHOOK_URL (must be HTTPS)")
        sys.exit(1)

    app = web.Application()
    app.router.add_post("/webhook", handle_webhook)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8080)
    await site.start()
    print("[webhook] local server started on port 8080")

    async with VibeBotHTTP(token) as bot:
        print(f"[webhook] setting webhook to {webhook_url}")
        await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
        print("[webhook] waiting for updates... (Ctrl+C to stop)")

        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            pass
        finally:
            print("[webhook] removing webhook...")
            await bot.delete_webhook()
            await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
