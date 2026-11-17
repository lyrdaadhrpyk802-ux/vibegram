# ============================================
#  scripts/vibe.py - Unified Command Line Interface
#  All code and comments are English. No emojis.
# ============================================
import argparse
import asyncio
import sys

def main():
    parser = argparse.ArgumentParser(prog="vibe", description="Vibe Messenger CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # backup command
    p_backup = subparsers.add_parser("backup", help="Backup a chat to JSON")
    p_backup.add_argument("peer", help="Chat username, ID, or 'me'")
    p_backup.add_argument("--limit", type=int, default=None)
    p_backup.add_argument("--no-media", action="store_true")

    # info command
    p_info = subparsers.add_parser("info", help="Start the info helper bot")
    
    # clock command
    p_clock = subparsers.add_parser("clock", help="Live clock in profile name")
    p_clock.add_argument("--interval", type=int, default=70)

    # login command
    p_login = subparsers.add_parser("login", help="Login to Vibe with a phone number")

    args = parser.parse_args()

    if args.command == "backup":
        from scripts.backup_chat import main as backup_main
        sys.argv = ["backup_chat", args.peer]
        if args.limit: sys.argv.extend(["--limit", str(args.limit)])
        if args.no_media: sys.argv.append("--no-media")
        asyncio.run(backup_main())
        
    elif args.command == "info":
        from scripts.chat_info import main as info_main
        try:
            asyncio.run(info_main())
        except KeyboardInterrupt:
            pass
            
    elif args.command == "clock":
        from scripts.name_clock import main as clock_main
        sys.argv = ["name_clock"] # Add interval logic if needed
        try:
            asyncio.run(clock_main())
        except KeyboardInterrupt:
            pass

    elif args.command == "login":
        async def do_login():
            from userapi import VibeClient
            async with VibeClient() as c:
                if await c.is_authorized():
                    print("Already logged in.")
                    return
                phone = input("Phone number: ")
                await c.login(phone)
        asyncio.run(do_login())

if __name__ == "__main__":
    main()
