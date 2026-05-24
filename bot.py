import os
import asyncio
import requests
from datetime import datetime, timezone
from telegram import Bot
from telegram.error import TelegramError, RetryAfter
import schedule
import time
import logging
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@togrisini_etsa"
POSTS_PER_DAY = 19
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

POST_HOURS_UTC = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

MAVZULAR = [
    "пул ва бойлик",
    "дустлик ва хиёнат",
    "ота-она ва фарзанд",
    "жамиятда икки юзламалик",
    "севги ва никох",
    "иш ва карьера",
    "вакт ва умр",
    "узбек менталитети",
    "муваффакиятсизлик ва кайта туриш",
    "одамларнинг килиги",
    "согликва хает тарзи",
    "орзу ва максад",
    "ёлгиз колиш",
    "алдов ва пул",
    "хаётда танлов",
    "ёш ва тажриба",
    "муносабатларда чегара",
    "ижтимоий тармоклар ва хакикат",
    "мактаб ва таълим",
    "эркак ва аёл муносабати",
    "ишонч ва алданиш",
    "бахт нима",
    "мактов ва танкид",
    "пул ва дустлик",
    "хаётнинг утиши",
]

def generate_post() -> str:
    mavzu = random.choice(MAVZULAR)
    prompt = (
        "Sen o'zbek tilida qisqa, ta'sirli gaplar yozadigan yozuvchisan.\n\n"
        f"Mavzu: {mavzu}\n\n"
        "Yaxshi misollar:\n"
        "- Yaqin do'sting xiyonat qilsa, eng katta og'riq shu bo'ladi.\n"
        "- Pul borida hamma do'st, yo'qida faqat oyna qarshingda.\n"
        "- Ota-ona har doim haq emas, lekin ular seni yaxshi ko'radi.\n"
        "- Odam charchaganda emas, umid uzganda yiqiladi.\n\n"
        "Yuqoridagi misollar kabi 1 ta gap yoz.\n\n"
        "QOIDALAR:\n"
        "1. Faqat o'zbek kirillida yoz - lotincha harf QOSHMA\n"
        "2. Faqat 1 ta jumla\n"
        "3. 8 dan 12 gacha soz\n"
        "4. Oddiy kundalik sozlar - odamlar ko'chada gapiradigan til\n"
        "5. Mantiqli, tushunarli gap\n"
        "6. Emoji, hashtag YOQ\n"
        "7. 'To'g'risini etsam' deb BOSHLAMA\n"
        "8. Faqat gapning o'zini yoz"
    )

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 150,
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    return response.json()["choices"][0]["message"]["content"].strip()

async def send_post():
    bot = Bot(token=BOT_TOKEN)
    post_text = ""
    try:
        post_text = generate_post()
        await bot.send_message(chat_id=CHANNEL_ID, text=post_text)
        logger.info(f"Post yuborildi: {post_text[:60]}...")
        await asyncio.sleep(2)
    except RetryAfter as e:
        logger.warning(f"Kutish: {e.retry_after} soniya")
        await asyncio.sleep(e.retry_after + 1)
        if post_text:
            await bot.send_message(chat_id=CHANNEL_ID, text=post_text)
    except TelegramError as e:
        logger.error(f"Telegram xatosi: {e}")
    except Exception as e:
        logger.error(f"Xato: {e}")
    finally:
        await bot.close()
        await asyncio.sleep(1)

def run_async_post():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(send_post())
    finally:
        loop.close()

def setup_schedule():
    current_utc_hour = datetime.now(timezone.utc).hour
    current_utc_minute = datetime.now(timezone.utc).minute
    for hour in POST_HOURS_UTC:
        if hour > current_utc_hour or (hour == current_utc_hour and current_utc_minute < 55):
            schedule.every().day.at(f"{hour:02d}:00").do(run_async_post)
            logger.info(f"UTC {hour:02d}:00 = GMT+5 {hour+5:02d}:00 da post")
        else:
            logger.info(f"UTC {hour:02d}:00 otib ketdi")
    schedule.every().day.at("00:01").do(reset_schedule)

def reset_schedule():
    schedule.clear()
    for hour in POST_HOURS_UTC:
        schedule.every().day.at(f"{hour:02d}:00").do(run_async_post)
    schedule.every().day.at("00:01").do(reset_schedule)
    logger.info("Jadval yangilandi")

def main():
    logger.info("Bot ishga tushdi!")
    logger.info(f"Kanal: {CHANNEL_ID}")
    logger.info(f"Kuniga: {POSTS_PER_DAY} ta post (06:00 - 00:00 GMT+5)")
    setup_schedule()
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
