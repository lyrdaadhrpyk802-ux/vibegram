# Vibe Compatibility Matrix

Verified against the live Vibe backend.

Feature Status Notes
-------------------------------
Basic Messaging        OK
Silent & Scheduled     OK
Reply Markup (Buttons) OK
Media (Photo, File)    OK
Location & Venue       OK
Polls                  OK    Requires TextWithEntities
Reactions              FAIL  Requires Premium Account
Stories                OK
Forums                 OK
Themes & Wallpapers    OK
Emoji Status           OK
Profile Color          OK
Channel Boosts         OK
Bot Methods            FAIL  Requires bot login
Voice Calls            FAIL  Not supported by Vibe
Real Payments          FAIL  No payment gateway

(جدول پشتیبانی: تست‌های واقعی نشان می‌دهد Vibe از استوری، فروم و مدیا پشتیبانی می‌کند. ری‌اکشن نیازمند اکانت پرمیوم است. متدهای مربوط به ربات‌ها و تماس صوتی در سرور Vibe غیرفعال هستند.)

### Bot API Limitations
- **Inline Buttons (دکمه‌های شیشه‌ای):** The Vibe server actively blocks unofficial bots from sending inline keyboards (`BUTTON_INVALID`). Only officially verified/premium bots (like the Vibe Premium Bot) have the whitelist permission to send them. Use `ReplyKeyboard` (bottom buttons) instead, which are fully supported.
- **Voice Notes:** Bots are not allowed to send voice notes (`ChatSendVoicesForbiddenError`).
