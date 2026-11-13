# ============================================
#  userapi/_intro.py - Welcome Animation
#  All code and comments are English. No emojis.
# ============================================
import sys
import time
import urllib.request
import json

def get_daily_downloads():
    """Fetch daily download stats from PyPI Stats."""
    try:
        url = "https://pypistats.org/api/packages/vibegram/recent"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=1.5) as response:
            data = json.loads(response.read().decode())
            # Use last_day as the primary metric since it's the most reliable
            return data["data"].get("last_day", "?")
    except Exception:
        return "?"

def show_intro():
    # Skip animation if running in non-interactive environment
    if not sys.stdout.isatty():
        return

    spinner = ['|', '/', '-', '\\']
    sys.stdout.write("\033[?25l") # Hide cursor
    for i in range(12):
        sys.stdout.write(f"\r\033[2mLoading vibegram {spinner[i % 4]}\033[0m")
        sys.stdout.flush()
        time.sleep(0.05)
        
    daily = get_daily_downloads()
    
    # Clear previous line and print info
    sys.stdout.write(f"\r\033[K\033[1mvibegram\033[0m \033[2m|\033[0m Dev: Ali VEX \033[2m|\033[0m Today: {daily}\n")
    sys.stdout.flush()
    sys.stdout.write("\033[?25h") # Show cursor
