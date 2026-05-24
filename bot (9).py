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

# GMT+5 da: 6:00 - 00:00 = UTC da: 1:00 - 19:00
POST_HOURS_UTC = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

MAVZULAR = [
    "пул ва бойлик — одамлар буни очиқчасига гапирмайди, лекин ҳамманинг миясида",
    "дўстлик ва хиёнат — яқин одамлар баъзан энг катта душман бўлади",
    "ота-она ва фарзанд муносабатлари — севги бор, лекин оғриқ ҳам кўп",
    "жамиятда икки юзламалик — кўчада бир хил, уйда бошқача одамлар",
    "севги ва никоҳ ҳақида ҳақиқат — романтика эмас, ҳақиқий ҳаёт",
    "иш ва карьера — муваффақият учун нима керак, нима керак эмас",
    "вақт ва умр — ёшлигимизда англолмайдиган нарсалар",
    "ўзбек менталитети — яхши томонлари ҳам бор, ёмон томонлари ҳам",
    "муваффақиятсизлик ва қайта туриш — йиқилганлар ҳақида ҳеч ким гапирмайди",
    "одамларнинг қилиғи — кузатсанг, кўп нарса кўринади",
    "соғлиқ ва ҳаёт тарзи — эътибор бермасак кейин афсус қиламиз",
    "орзу ва мақсад — баъзилар орзу қилади, баъзилар ҳаракат қилади",
    "ёлғиз қолиш ва ўз-ўзини топиш — бу ёмон нарса эмас",
    "пул топиш йўллари ва алдовлар — кўпчилик бу ҳақда билмайди",
    "ҳаётда танлов — ҳар бир қарор кейинги 5 йилни белгилайди",
    "ёш ва тажриба — 20 ёшда ва 40 ёшда дунёни бошқача кўрасан",
    "инсоний муносабатларда чегара қўйиш — нима учун бу муҳим",
    "ижтимоий тармоқлар ва ҳақиқий ҳаёт — кўрсатиладиган ва яширилаган нарса",
    "мактаб ва таълим — бизга нима ўргатди, нима ўргатмади",
    "эркаклар ва аёллар муносабатидаги ҳақиқатлар — икки томондан ҳам",
    "ишонч ва алданиш — одамларга ишонишнинг нархи",
    "бахт нима — кўпчилик нотўғри жойдан қидиради",
    "мақтов ва танқид — ортингдан гапиришади, юзингга эса бошқача",
    "пул ва дўстлик — пул борида дўст кўп, йўқида ҳеч ким йўқ",
    "ҳаётнинг ўтиши — кеча бола эдинг, бугун ўзинг ҳам билмайсан қаерга кетаётганингни",
]

def generate_post() -> str:
    mavzu = random.choice(MAVZULAR)
    prompt = f"""Telegram канал учун 1 та пост ёз.

Мавзу: {mavzu}

Қатъий қоидалар:
- Ўзбек КИРИЛЛ ёзувида бўлсин
- Фақат БИТТА жумла
- Минимал 8 та, максимал 15 та сўз
- Ҳақиқий, кескин, ўйлантирувчи гап
- Эмодзи ва ҳэштэг ҚЎШМа
- "Тўғрисини этсам" ёки "Тўғриси" деб БОШЛАМА
- Фақат кирилл ҳарфларини ишлат, лотин ҳарф ҚЎШМа
- Фақат оддий, кундалик ўзбек сўзларини ишлат — одамлар кўчада ишлатадиган сўзлар
- Ясама, нотўғри, тушунб бўлмайдиган сўз ЁЗМа
- Рус ёки бошqa тил сўзлари ИШЛАТМа
- Фақат жумланинг ўзини ёз, бошқа ҳеч нарса ёзма"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 200,
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    return response.json()["choices"][0]["message"]["content"].strip()

async def send_post():
    bot = Bot(token=BOT_TOKEN)
    try:
        post_text = generate_post()
        await bot.send_message(chat_id=CHANNEL_ID, text=post_text)
        logger.info(f"✅ Post yuborildi: {post_text[:60]}...")
        await asyncio.sleep(2)
    except RetryAfter as e:
        logger.warning(f"⏳ Kutish: {e.retry_after} soniya")
        await asyncio.sleep(e.retry_after + 1)
        await bot.send_message(chat_id=CHANNEL_ID, text=post_text)
    except TelegramError as e:
        logger.error(f"❌ Telegram xatosi: {e}")
    except Exception as e:
        logger.error(f"❌ Xato: {e}")
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
        # Faqat keyingi soatlarni qo'sh, o'tib ketganlarni o'tkazib yubor
        if hour > current_utc_hour or (hour == current_utc_hour and current_utc_minute < 55):
            schedule.every().day.at(f"{hour:02d}:00").do(run_async_post)
            logger.info(f"📅 UTC {hour:02d}:00 = GMT+5 {hour+5:02d}:00 da post")
        else:
            logger.info(f"⏭ UTC {hour:02d}:00 o'tib ketdi, o'tkazildi")

    # Ertangi kun uchun hammasi qayta sozlansin
    schedule.every().day.at("00:01").do(reset_schedule)

def reset_schedule():
    """Har kuni yarim tungda jadvalni qayta sozlaydi"""
    schedule.clear()
    for hour in POST_HOURS_UTC:
        schedule.every().day.at(f"{hour:02d}:00").do(run_async_post)
        logger.info(f"📅 Yangilandi: UTC {hour:02d}:00 = GMT+5 {hour+5:02d}:00")
    schedule.every().day.at("00:01").do(reset_schedule)

def main():
    logger.info("🤖 Bot ishga tushdi!")
    logger.info(f"📢 Kanal: {CHANNEL_ID}")
    logger.info(f"📊 Kuniga: {POSTS_PER_DAY} ta post (06:00 - 00:00 GMT+5)")
    setup_schedule()
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
