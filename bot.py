import os
import asyncio
import random
import time
import schedule
import logging
from telegram import Bot
from groq import Groq

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Sozlamalar
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
CHANNEL_ID = "@togrisini_etsa"

client = Groq(api_key=GROQ_API_KEY)
bot = Bot(token=BOT_TOKEN)

MAVZULAR = [
    "пул ва бойлик", "дўстлик ва хиёнат", "ота-она муносабатлари",
    "жамиятда икки юзламалик", "севги ва никоҳ", "иш ва карьера",
    "вақт ва умр", "ўзбек менталитети", "муваффақиятсизлик",
    "одамларнинг қилиғи", "соғлиқ", "орзу ва мақсад",
    "ёлғиз қолиш", "пул топиш йўллари", "ҳаётда танлов"
]

def generate_post():
    mavzu = random.choice(MAVZULAR)
    prompt = f"Мавзу: {mavzu}. Аччиқ ҳақиқатни 1 та гапда ёз (кирилл, 8-15 сўз, #тогрисини #хакикат)."
    
    # Groq orqali yozdirish
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content.strip()

async def send_post():
    try:
        post_text = generate_post()
        await bot.send_message(chat_id=CHANNEL_ID, text=post_text)
        logger.info(f"✅ Yuborildi: {post_text}")
    except Exception as e:
        logger.error(f"❌ Xatolik: {e}")

def run_async_post():
    asyncio.run(send_post())

if __name__ == "__main__":
    logger.info("🤖 Bot Groq bilan ishga tushdi!")
    # Test uchun
    run_async_post()
    
    # Har soatda post (07:00 dan 23:00 gacha)
    for hour in range(7, 24):
        schedule.every().day.at(f"{hour:02d}:00").do(run_async_post)
        
    while True:
        schedule.run_pending()
        time.sleep(60)
