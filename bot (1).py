import asyncio
import anthropic
from telegram import Bot
from telegram.error import TelegramError
import schedule
import time
import logging
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# ========== SOZLAMALAR ==========
BOT_TOKEN = "BU_YERGA_BOT_TOKENINGIZNI_YOZING"   # @BotFather dan olingan token
CHANNEL_ID = "@togrisini_etsa"                      # Kanalingiz username
POSTS_PER_DAY = 15                                  # Kuniga nechta post
ANTHROPIC_API_KEY = "BU_YERGA_ANTHROPIC_API_KEY"   # https://console.anthropic.com dan oling
# ================================

POST_HOURS = [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23][:POSTS_PER_DAY]

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

anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
bot = Bot(token=BOT_TOKEN)

def generate_post() -> str:
    mavzu = random.choice(MAVZULAR)
    prompt = f"""Telegram канал учун 1 та пост ёз.

Мавзу: {mavzu}

Қатъий қоидалар:
- Ўзбек КИРИЛЛ ёзувида бўлсин
- Фақат БИТТА жумла
- Минимал 8 та, максимал 15 та сўз
- Ҳақиқий, кескин, ўйлантирувчи гап — umumiy gap emas
- Эмодзи ва ҳэштэг ҚЎШМа
- "Тўғрисини этсам" ёки "Тўғриси" деб БОШЛАМА
- Фақат жумланинг ўзини ёз, бошқа ҳеч нарса ёзма"""

    message = anthropic_client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()

async def send_post():
    try:
        post_text = generate_post()
        await bot.send_message(chat_id=CHANNEL_ID, text=post_text)
        logger.info(f"✅ Post yuborildi: {post_text[:60]}...")
    except TelegramError as e:
        logger.error(f"❌ Telegram xatosi: {e}")
    except Exception as e:
        logger.error(f"❌ Xato: {e}")

def run_async_post():
    asyncio.run(send_post())

def setup_schedule():
    for hour in POST_HOURS:
        schedule.every().day.at(f"{hour:02d}:00").do(run_async_post)
        logger.info(f"📅 {hour:02d}:00 da post")

def main():
    logger.info("🤖 Bot ishga tushdi!")
    logger.info(f"📢 Kanal: {CHANNEL_ID}")
    logger.info(f"📊 Kuniga: {POSTS_PER_DAY} ta post")
    setup_schedule()
    logger.info("🚀 Test post yuborilmoqda...")
    run_async_post()
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
