# ============================================
#  userapi/utils.py - Utility helpers
#  All code and comments are English. No emojis.
# ============================================
import sys

def make_progress_bar(prefix="Progress"):
    """Creates a simple text-based progress bar for uploads/downloads."""
    def callback(current, total):
        percent = current / total * 100 if total > 0 else 0
        bar_length = 20
        filled = int(bar_length * current // total) if total > 0 else 0
        bar = '=' * filled + '-' * (bar_length - filled)
        sys.stdout.write(f'\r{prefix} |{bar}| {percent:.1f}% ({current}/{total})')
        sys.stdout.flush()
        if current == total:
            sys.stdout.write('\n')
    return callback
