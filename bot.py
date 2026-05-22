import os
import asyncio
import random
import time
import schedule
import logging
from telegram import Bot
from groq import Groq

# Logging sozlamalari
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ========== SOZLAMALAR ==========
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
CHANNEL_ID = "@togrisini_etsa"

client = Groq(api_key=GROQ_API_KEY)
bot = Bot(token=BOT_TOKEN)

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
    "ёлғиз қолиш ва ўз-узини топиш — бу ёмон нарса эмас",
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

# 15 ta aniq vaqt
VAQTLAR = [
    "07:00", "08:00", "09:00", "10:00", "11:00", 
    "12:00", "13:00", "14:00", "15:00", "16:00", 
    "17:00", "18:00", "19:00", "20:00", "21:00"
]

def generate_post():
    mavzu = random.choice(MAVZULAR)
    prompt = f"Мавзу: {mavzu}. 1 ta keskin, achchiq haqiqat yoz. (8-15 soz, o'zbek kirill, #togrisini #xakikat xashtaglari bilan. 'To'g'risini aytsam' deb boshlama)."
    
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content.strip()

async def send_post():
    try:
        post_text = generate_post()
        await bot.send_message(chat_id=CHANNEL_ID, text=post_text)
        logger.info(f"✅ Yuborildi: {post_text[:30]}...")
    except Exception as e:
        logger.error(f"❌ Xato: {e}")

def run_async_post():
    asyncio.run(send_post())

if __name__ == "__main__":
    logger.info("🤖 Bot ishga tushdi!")
    logger.info(f"📅 Postlar quyidagi soatlarda chiqadi: {', '.join(VAQTLAR)}")
    
    for vaqt in VAQTLAR:
        schedule.every().day.at(vaqt).do(run_async_post)
    
    # Test uchun bitta post
    run_async_post()
    
    while True:
        schedule.run_pending()
        time.sleep(60)
