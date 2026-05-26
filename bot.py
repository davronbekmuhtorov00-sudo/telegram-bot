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

# Bugungi ishlatilgan mavzularni eslab qoladi
ISHLATILGAN_MAVZULAR = []

MAVZULAR = [
    "пул ва бойлик",
    "дўстлик ва хиёнат",
    "ота-она ва фарзанд",
    "жамиятда икки юзламачилик",
    "севги ва никоҳ",
    "иш ва карьера",
    "вақт ва умр",
    "ўзбек менталитети",
    "муваффақиятсизлик ва қайта туриш",
    "одамларнинг қилиғи",
    "соғлиқ ва ҳаёт тарзи",
    "орзу ва мақсад",
    "ёлғиз қолиш",
    "алдов ва пул",
    "ҳаётда танлов",
    "ёш ва тажриба",
    "муносабатларда чегара",
    "ижтимоий тармоқлар ва ҳақиқат",
    "мактаб ва таълим",
    "эркак ва аёл муносабати",
    "ишонч ва алданиш",
    "бахт нима",
    "мақтов ва танқид",
    "пул ва дўстлик",
    "ҳаётнинг ўтиши",
]

MISOLLAR = """
Қуйидагилар каби қисқа, таъсирли гаплар ёз:

Калб қанчалик пок бўлса, инсон шунчалик ишонувчан бўлади.
Кун келиб кимдир айтган гаплари учун, кимдир эса айта олмаган гаплари учун афсусланади.
Ҳаётда чиройли инсонни эмас, ҳаётингизни чиройли қилган инсонни севинг.
Соат вақтни кўрсатади, вақт эса ёнингдагиларни.
Ҳеч кимга ишонмаслик кераклигини ишонганларимиз ўргатди.
Ёнимиздагилар яқин эмас, яқинларимиз ёнимизда эмас.
Уйқу ёрдам беролмайди агар қалбинг чарчаган бўлса.
Силаган қўлларни қадрига етмаганлар тепилган оёқларни ўпиб яшайдилар.
Нега ёзмаяпди дема, ўзига керакли инсонни топгандур балки.
Ўйлама, шунчаки яша — ўйлайверсанг яшагинг келмай қолади.
Оғриқ фақат кўз ёшда эмас, кулгу остида ҳам яширилган бўлади.
Сиз учун курашадиган инсонни севинг, оддий муаммода кетадиганни эмас.
Эришиб бўлмаган нарсаларимизга тақдир деб ном бердик.
Яхши нарсалар тугайди, яна ҳам яхшиси бошланиши учун.
Ўтмишга айланмайдиган дард йўқ, сабр қилмайдиган инсон бор.
"""

ZAXIRA_GAPLAR = [
    "Яқин одам хиёнат қилса, энг катта оғриқ шу бўлади.",
    "Пул борида ҳамма дўст, йўқида фақат ойна қаршингда.",
    "Одам чарчаганда эмас, умид узганда йиқилади.",
    "Ота-она ҳар доим ҳақ эмас, лекин улар сени яхши кўради.",
    "Вақт ўтади, лекин қилган яхшилик қолади.",
    "Дўст кўп бўлиши мумкин, лекин ишончли дўст топиш қийин.",
    "Соат вақтни кўрсатади, вақт эса ёнингдагиларни.",
    "Уйқу ёрдам беролмайди агар қалбинг чарчаган бўлса.",
]

def lotin_harfmi(matn):
    lotin = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    for harf in matn:
        if harf in lotin:
            return True
    return False

def taqiqlangan_boshlashmi(matn):
    tekshir = matn.lower().strip()
    taqiqlangan = [
        "тўғрисини", "тўғриси", "togrisini", "to'g'risini",
        "ростини", "айтганда", "торсни"
    ]
    for bosh in taqiqlangan:
        if tekshir.startswith(bosh):
            return True
    return False

def soz_soni_togriymi(matn):
    sozlar = matn.split()
    return 6 <= len(sozlar) <= 16

def ai_dan_gap_ol(mavzu):
    prompt = (
        "Сен ўзбек тилида қисқа, таъсирли гаплар ёзувчисан.\n\n"
        f"Мавзу: {mavzu}\n\n"
        f"{MISOLLAR}\n"
        "ҚАТЪИЙ ҚОИДАЛАР:\n"
        "1. ФАҚАТ ўзбек кирилл ҳарфлари — лотин ҳарф МУТЛАҚО йўқ\n"
        "2. Фақат 1 та жумла\n"
        "3. 8 дан 14 гача сўз\n"
        "4. Оддий, кундалик сўзлар — мураккаб ёки ясама сўз йўқ\n"
        "5. Мантиқли, тушунарли гап\n"
        "6. Эмодзи ва ҳэштэг йўқ\n"
        "7. 'Тўғрисини этсам' ёки 'Тўғриси' деб БОШЛАМА\n"
        "8. Фақат гапнинг ўзини ёз — бошқа ҳеч нарса ёзма\n"
        "9. Рус ёки бошқа тил сўзи йўқ"
    )

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "max_tokens": 120,
            "temperature": 0.8,
            "messages": [{"role": "user", "content": prompt}]
        }
    )
    return response.json()["choices"][0]["message"]["content"].strip()

def generate_post() -> str:
    global ISHLATILGAN_MAVZULAR
    # Barcha mavzular ishlatilsa — qayta boshlash
    if len(ISHLATILGAN_MAVZULAR) >= len(MAVZULAR):
        ISHLATILGAN_MAVZULAR = []
        logger.info("Barcha mavzular tugadi, qayta boshlandi")
    # Ishlatilmagan mavzulardan tanlash
    qolgan = [m for m in MAVZULAR if m not in ISHLATILGAN_MAVZULAR]
    mavzu = random.choice(qolgan)
    ISHLATILGAN_MAVZULAR.append(mavzu)
    logger.info(f"Mavzu: {mavzu}")
    for urinish in range(5):
        gap = ai_dan_gap_ol(mavzu)
        if lotin_harfmi(gap):
            logger.warning(f"Lotin harf! Qayta {urinish+1}: {gap[:40]}")
            continue
        if taqiqlangan_boshlashmi(gap):
            logger.warning(f"Taqiqlangan boshlash! Qayta {urinish+1}: {gap[:40]}")
            continue
        if not soz_soni_togriymi(gap):
            logger.warning(f"Soz soni xato! Qayta {urinish+1}: {gap[:40]}")
            continue
        logger.info(f"Gap tasdiqlandi: {gap[:60]}")
        return gap
    logger.warning("5 urinishda ham xato, zaxira gap")
    return random.choice(ZAXIRA_GAPLAR)

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
