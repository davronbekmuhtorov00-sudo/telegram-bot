# 🤖 @togrisini_etsa Telegram Bot

Har kuni avtomatik 15 ta qisqa, ta'sirli post tashlaydi.

---

## 🚀 O'rnatish (Railway - BEPUL)

### 1-qadam: Fayllarni GitHub ga yuklang
1. GitHub.com da yangi repo yarating
2. `bot.py` va `requirements.txt` ni yuklang

### 2-qadam: bot.py ni sozlang
`bot.py` faylini oching va shu qatorlarni to'ldiring:

```python
BOT_TOKEN = "7123456789:AAFxxx..."        # @BotFather dan
ANTHROPIC_API_KEY = "sk-ant-xxx..."       # console.anthropic.com dan
```

### 3-qadam: Botni kanalga admin qiling
1. Kanalingizni oching → Boshqarish → Adminlar
2. Botingizni qidiring va admin qiling
3. "Post yuborish" huquqini bering

### 4-qadam: Railway ga joylashtiring
1. Railway.app ga kiring (GitHub bilan)
2. "New Project" → "Deploy from GitHub repo"
3. Reponi tanlang → Deploy

### 5-qadam: Anthropic API Key olish
1. console.anthropic.com ga kiring
2. "API Keys" → "Create Key"
3. Kalitni nusxalab oling

---

## 💰 Narx
- Railway: **Bepul** (oyiga $5 kredit bor)
- Anthropic API: Juda arzon (15 ta post/kun ≈ $0.50/oy)

---

## ⚙️ Sozlamalar (bot.py da)
```python
POSTS_PER_DAY = 15        # Kuniga nechta post
POST_HOURS = [6,7,8...]   # Qaysi soatlarda
```

---

## ❓ Muammo bo'lsa
Telegram: @togrisini_etsa kanalida ko'ring
