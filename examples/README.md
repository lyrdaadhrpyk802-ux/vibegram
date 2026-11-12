# examples

مثال‌های آموزشی برای کتابخانه pyvibe. هر فایل مستقل و قابل اجراست.

## پیش‌نیاز
- کتابخانه نصب شده (یا PYTHONPATH به ریشه پروژه)
- یک‌بار لاگین (فایل 01_login.py)

## اجرا
cd ~/pyvibe
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD" python -B examples/01_login.py

## ترتیب پیشنهادی
01 - 01_login.py - ورود با شماره تلفن + کد + رمز دو مرحله‌ای
02 - 02_send_message.py - ارسال، ویرایش، حذف، پاسخ، پین
03 - 03_read_messages.py - خواندن پیام‌ها، دیالوگ‌ها، جستجو
04 - 04_send_media.py - ارسال عکس، فایل، ویس، لوکیشن، نظرسنجی
05 - 05_live_updates.py - شنیدن پیام‌های زنده
06 - 06_groups_channels.py - ساخت گروه، کانال، forum
07 - 07_stories.py - استوری: ارسال، خواندن، حذف
08 - 08_account.py - پروفایل، اسم، عکس، حریم خصوصی
09 - 09_contacts.py - مخاطبین: افزودن، بلاک، لیست
10 - 10_backup.py - پشتیبان‌گیری چت به JSON
11 - 11_advanced.py - raw TL، دسترسی کامل

## نکات
- هر فایل از session ذخیره‌شده در ~/.vibe_session.session استفاده می‌کند.
- پیام‌ها پیش‌فرض به Saved Messages فرستاده می‌شوند.
- ری‌اکشن در Vibe نیاز به پرمیوم دارد.
