import os
import asyncio
import random
from datetime import datetime
from telethon import TelegramClient, events, errors
from telethon.tl.types import UpdateChannelParticipant, ChannelParticipantLeft
from telethon.sessions import StringSession

# متغیرها از تنظیمات ریل‌وی خوانده می‌شوند
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
SESSION_STRING = os.environ.get("SESSION_STRING", "")

# آیدی کانال مدنظر (با فرمت عددی مثلا -1004413564062)
TARGET_CHANNEL_ID = int(os.environ.get("TARGET_CHANNEL_ID", "0"))

# سقف ارسال پیام در هر روز برای محافظت از اکانت
DAILY_SEND_LIMIT = 20

# متون متغیر با هدف دور زدن فیلترهای ضداسپم تلگرام
MESSAGES = [
    "سلام وقتتون بخیر 🌹\nدیدیم از کانال لفت دادید، خوشحال می‌شیم دلیلتون یا انتقادتون رو بهمون بگید تا کیفیت رو بهتر کنیم.\nاگر مایل بودید باز هم همراه ما باشید:\n@remixiyu",
    "درود بر شما دوست عزیز 🌱\nمتوجه خروجتون از کانال شدیم. پیشنهادی برای بهتر شدن مطالب دارید؟ مشتاق شنیدن نظرتون هستیم.\nلینک کانال برای همراهی مجدد:\n@remixiyu",
    "سلام و وقت بخیر 🤍\nدلیل خروجتون از کانال چی بود؟ با گفتن نظرتون کمکمون می‌کنید عملکرد بهتری داشته باشیم.\nخوشحال می‌شیم دوباره ببینیمتون:\n@remixiyu"
]

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

processed_users = set()
sent_count_today = 0
last_day_reset = datetime.utcnow().day

@client.on(events.Raw(UpdateChannelParticipant))
async def on_user_left(event):
    global sent_count_today, last_day_reset

    try:
        # ساخت آیدی استاندارد سوپرکانال تلگرام
        raw_channel_id = int(f"-100{event.channel_id}")
        if raw_channel_id != TARGET_CHANNEL_ID:
            return

        # ریست شمارنده در آغاز روز جدید
        current_day = datetime.utcnow().day
        if current_day != last_day_reset:
            sent_count_today = 0
            last_day_reset = current_day

        # بررسی رسیدن به سقف مجاز روزانه
        if sent_count_today >= DAILY_SEND_LIMIT:
            print("[Limit] سقف مجاز ارسال روزانه پر شده است. پیام ارسال نمی‌شود.", flush=True)
            return

        # بررسی خروج قطعی کاربر
        if isinstance(event.new_participant, ChannelParticipantLeft):
            user_id = event.user_id

            if user_id in processed_users:
                return

            processed_users.add(user_id)
            print(f"[Detect] کاربر {user_id} از کانال خارج شد.", flush=True)

            # تأخیر تصادفی بین ۲ تا ۵ دقیقه
            delay = random.randint(120, 300)
            print(f"[Delay] وقفه {delay} ثانیه‌ای...", flush=True)
            await asyncio.sleep(delay)

            msg = random.choice(MESSAGES)

            try:
                await client.send_message(user_id, msg)
                sent_count_today += 1
                print(f"[Success] پیام ارسال شد به {user_id} (مجموع امروز: {sent_count_today})", flush=True)

            except errors.UserPrivacyRestrictedError:
                print(f"[Privacy] پیام‌های ناشناس کاربر {user_id} قفل است.", flush=True)
            except errors.PeerFloodError:
                print("[Flood] اکانت محدود شد. توقف ارسال تا ۴۵ دقیقه...", flush=True)
                await asyncio.sleep(2700)
            except errors.FloodWaitError as e:
                print(f"[Wait] تلگرام اعلام لیمیت {e.seconds} ثانیه کرد.", flush=True)
                await asyncio.sleep(e.seconds + 5)
            except Exception as e:
                print(f"[Send Error] خطا در ارسال به {user_id}: {e}", flush=True)

    except Exception as e:
        print(f"[Event Error] {e}", flush=True)

async def main():
    await client.start()
    print("🚀 ربات مجزای جذب ممبر کانال آنلاین و فعال است!", flush=True)
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
