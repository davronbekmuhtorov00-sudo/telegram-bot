import os
import asyncio
from datetime import datetime, timezone
import requests
from telegram import Bot
from telegram.error import TelegramError, RetryAfter
import logging
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@togrisini_etsa"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# GMT+5 da: 6:00 - 00:00 = UTC da: 1:00 - 19:00
POST_HOURS_UTC = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

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

MISOLLAR = (
    "Калб қанчалик пок бўлса, инсон шунчалик ишонувчан бўлади.\n"
    "Кун келиб кимдир айтган гаплари учун, кимдир эса айта олмаган гаплари учун афсусланади.\n"
    "Ҳаётда чиройли инсонни эмас, ҳаётингизни чиройли қилган инсонни севинг.\n"
    "Соат вақтни кўрсатади, вақт эса ёнингдагиларни.\n"
    "Ҳеч кимга ишонмаслик кераклигини ишонганларимиз ўргатди.\n"
    "Ёнимиздагилар яқин эмас, яқинларимиз ёнимизда эмас.\n"
    "Уйқу ёрдам беролмайди агар қалбинг чарчаган бўлса.\n"
    "Нега ёзмаяпди дема, ўзига керакли инсонни топгандур балки.\n"
    "Оғриқ фақат кўз ёшда эмас, кулгу остида ҳам яширилган бўлади.\n"
    "Сиз учун курашадиган инсонни севинг, оддий муаммода кетадиганни эмас.\n"
    "Вафо қимматбаҳо ҳадия, уни арзон инсонлар бера олмайди.\n"
    "Аслида ҳеч ким банд эмас, шунчаки муҳимроғи биз эмасмиз.\n"
    "Ишонч руҳ кабидир, тарк этдими қайтиб келмайди.\n"
    "Чиройлиси минглаб учрайди, аммо вафолиси битта бўлади.\n"
    "Арзимаган пулларни топамиз деб болаликни йўқотдик.\n"
    "Кетишни хоҳлаганларни қўйиб юбор, улар ҳаётингдаги ролини ўйнаб бўлди.\n"
    "Одамларга қанча кўп яхшилик қилма, улар фақатгина хатоларингни эслаб қолади.\n"
    "Тушунадиган инсонга сукутнинг ўзи кифоя, тушунмайдиганга бир умр гапирсанг ҳам фойдаси йўқ.\n"
    "Аслида ҳаётга эмас, одамларга чидаш қийин.\n"
    "Ҳеч ким ҳеч нарсани қадрига етмайди, токи йўқотмагунича.\n"
)

ZAXIRA_GAPLAR = [
    "Яқин одам хиёнат қилса, энг катта оғриқ шу бўлади.",
    "Пул борида ҳамма дўст, йўқида фақат ойна қаршингда.",
    "Одам чарчаганда эмас, умид узганда йиқилади.",
    "Ота-она ҳар доим ҳақ эмас, лекин улар сени яхши кўради.",
    "Вақт ўтади, лекин қилган яхшилик қолади.",
    "Соат вақтни кўрсатади, вақт эса ёнингдагиларни.",
    "Ишонч руҳ кабидир, тарк этдими қайтиб келмайди.",
    "Чиройлиси минглаб учрайди, аммо вафолиси битта бўлади.",
]

ishlatilgan_mavzular = []

def lotin_harfmi(matn):
    lotin = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
    for harf in matn:
        if harf in lotin:
            return True
    return False

def taqiqlangan_boshlashmi(matn):
    tekshir = matn.lower().strip()
    taqiqlangan = ["тўғрисини", "тўғриси", "togrisini", "to'g'risini", "торсни", "ростини"]
    for bosh in taqiqlangan:
        if tekshir.startswith(bosh):
            return True
    return False

def soz_soni_togriymi(matn):
    return 6 <= len(matn.split()) <= 18

def mavzu_tanlash():
    global ishlatilgan_mavzular
    if len(ishlatilgan_mavzular) >= len(MAVZULAR):
        ishlatilgan_mavzular = []
        logger.info("Barcha mavzular tugadi, qayta boshlandi")
    qolgan = [m for m in MAVZULAR if m not in ishlatilgan_mavzular]
    mavzu = random.choice(qolgan)
    ishlatilgan_mavzular.append(mavzu)
    return mavzu

def ai_dan_gap_ol(mavzu):
    prompt = (
        "Сен ўзбек тилида қисқа, таъсирли гаплар ёзувчисан.\n\n"
        f"Мавзу: {mavzu}\n\n"
        "Қуйидаги гаплар каби ёз:\n"
        f"{MISOLLAR}\n"
        "ҚАТЪИЙ ҚОИДАЛАР:\n"
        "1. ФАҚАТ ўзбек кирилл ҳарфлари — лотин ҳарф МУТЛАҚО йўқ\n"
        "2. Фақат 1 та жумла\n"
        "3. 8 дан 16 гача сўз\n"
        "4. Оддий, кундалик сўзлар — ясама сўз йўқ\n"
        "5. Мантиқли, тушунарли гап\n"
        "6. Эмодзи ва ҳэштэг йўқ\n"
        "7. 'Тўғрисини этсам' ёки 'Тўғриси' деб БОШЛАМА\n"
        "8. Фақат гапнинг ўзини ёз\n"
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

def generate_post():
    mavzu = mavzu_tanlash()
    logger.info(f"Mavzu: {mavzu}")
    for urinish in range(5):
        gap = ai_dan_gap_ol(mavzu)
        if lotin_harfmi(gap):
            logger.warning(f"Lotin harf! Qayta {urinish+1}")
            continue
        if taqiqlangan_boshlashmi(gap):
            logger.warning(f"Taqiqlangan boshlash! Qayta {urinish+1}")
            continue
        if not soz_soni_togriymi(gap):
            logger.warning(f"Soz soni xato! Qayta {urinish+1}")
            continue
        logger.info(f"Gap tasdiqlandi: {gap[:60]}")
        return gap
    logger.warning("5 urinishda xato, zaxira gap")
    return random.choice(ZAXIRA_GAPLAR)

async def post_tashlash(bot):
    post_text = ""
    try:
        post_text = generate_post()
        await bot.send_message(chat_id=CHANNEL_ID, text=post_text)
        logger.info(f"Post yuborildi: {post_text[:60]}...")
    except RetryAfter as e:
        logger.warning(f"Flood limit! {e.retry_after} soniya kutiladi...")
        await asyncio.sleep(e.retry_after + 5)
        if post_text:
            await bot.send_message(chat_id=CHANNEL_ID, text=post_text)
            logger.info("Qayta yuborildi!")
    except TelegramError as e:
        logger.error(f"Telegram xatosi: {e}")
    except Exception as e:
        logger.error(f"Xato: {e}")

async def main():
    bot = Bot(token=BOT_TOKEN)
    logger.info("Bot ishga tushdi!")
    logger.info(f"Kanal: {CHANNEL_ID}")
    logger.info(f"Kuniga: {len(POST_HOURS_UTC)} ta post (06:00 - 00:00 GMT+5)")

    yuborilgan_soatlar = set()

    while True:
        try:
            hozir_utc = datetime.now(timezone.utc)
            hozir_soat = hozir_utc.hour
            hozir_daqiqa = hozir_utc.minute

            kalit = f"{hozir_utc.date()}-{hozir_soat}"

            if hozir_soat in POST_HOURS_UTC and hozir_daqiqa == 0 and kalit not in yuborilgan_soatlar:
                logger.info(f"Post vaqti: UTC {hozir_soat:02d}:00 = GMT+5 {hozir_soat+5:02d}:00")
                await post_tashlash(bot)
                yuborilgan_soatlar.add(kalit)

                # Eski kalitlarni tozalash
                if len(yuborilgan_soatlar) > 50:
                    yuborilgan_soatlar = set(list(yuborilgan_soatlar)[-30:])

            await asyncio.sleep(30)

        except Exception as e:
            logger.error(f"Asosiy xato: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
