# ============================================
#  botapi/keyboards.py - Keyboard Builders
#  All code and comments are English. No emojis.
# ============================================
from telethon.tl.custom import Button
from telethon.tl.types import (
    ReplyKeyboardMarkup, KeyboardButtonRow, KeyboardButton, ButtonTypeDefault
)

class InlineKeyboard:
    def __init__(self):
        self.rows = []
        self.current_row = []

    def add(self, text, data=None, url=None):
        if url:
            btn = Button.url(text, url)
        else:
            btn = Button.inline(text, data.encode('utf-8') if isinstance(data, str) else str(data).encode())
        self.current_row.append(btn)
        return self

    def row(self):
        if self.current_row:
            self.rows.append(self.current_row)
            self.current_row = []
        return self

    def build(self):
        self.row()
        return self.rows

class ReplyKeyboard:
    def __init__(self, resize=True, single_use=False):
        self.rows = []
        self.current_row = []
        self.resize = resize
        self.single_use = single_use

    def add(self, text):
        # Now providing the required 'type' argument
        btn = KeyboardButton(text=text, type=ButtonTypeDefault())
        self.current_row.append(btn)
        return self

    def row(self):
        if self.current_row:
            self.rows.append(self.current_row)
            self.current_row = []
        return self

    def build(self):
        self.row()
        markup_rows = [KeyboardButtonRow(buttons=r) for r in self.rows]
        return ReplyKeyboardMarkup(rows=markup_rows, resize=self.resize, single_use=self.single_use)
