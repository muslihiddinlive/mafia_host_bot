# O'rnatish

Konfiguratsiya endi **environment variable** orqali beriladi (`config.py` fayli
git'ga tushadi, sirlarni o'zida saqlamaydi - faqat ularni o'qish mantig'i bor).

## 1. Kerakli ENV o'zgaruvchilar

| Nomi | Majburiymi | Tavsif |
|---|---|---|
| `TOKEN` | ✅ | @BotFather'dan olingan bot token |
| `ADMIN_ID` | ✅ | Sizning Telegram user ID'ingiz (superadmin) |
| `DB_CHAT_ID` | ✅ | Pastga qarang (2-bo'lim) |
| `WEBHOOK_URL` | Render avtomatik beradi | `SET_WEBHOOK=true` bo'lsa kerak (Render'da odatda kerak emas) |
| `SET_WEBHOOK` | ❌ (standart: true) | false = long polling |
| `SKIP_PENDING` | ❌ (standart: false) | Eski xabarlarni o'tkazib yuborish |
| `PLAYERS_COUNT_TO_START` | ❌ (standart: 4) | O'yin boshlash uchun minimal o'yinchi |
| `PLAYERS_COUNT_LIMIT` | ❌ (standart: 10) | Maksimal o'yinchi |
| `REQUEST_OVERDUE_TIME` | ❌ (standart: 600) | So'rov necha soniyada eskirishi |
| `WORD_BASE` | ❌ (standart: `/root/words.txt`) | croco/gallows so'zlar bazasi fayli |
| `DELETE_FROM_EVERYONE` | ❌ (standart: false) | O'yin paytida hammaning xabarini o'chirish |
| `LOGGER_LEVEL` | ❌ (standart: INFO) | Log darajasi |

To'liq namuna uchun `.env.example` fayliga qarang (lokal test qilishda shu faylni
`.env` deb nomlab, haqiqiy qiymatlar bilan to'ldiring - Render'da bu fayl kerak emas).

## 2. DB_CHAT_ID uchun supergroup yaratish
1. Yopiq (private) **supergroup** yarating (oddiy guruh emas)
2. Botni o'sha guruhga qo'shing va **admin** qiling (pin, edit, delete, invite huquqlari bilan)
3. Guruh ID'sini oling (masalan @getidsbot yordamida) — odatda `-100` bilan boshlanadi
4. Shu ID'ni `DB_CHAT_ID` environment variable'iga yozing

Bu guruhda pul/olmos/statistika/shop/til/premium ma'lumotlari bitta JSON fayl
(document) sifatida saqlanadi va pin qilinadi. Diskni istalgancha tozalasangiz
ham (masalan Render qayta deploy qilganda) — bot shu pin qilingan fayldan
avtomatik tiklanadi.

## 3. Render'da joylashtirish (Web Service)
1. Render Dashboard'da yangi **Web Service** yarating, shu repo'ni ulang
2. **Build Command:** `pip install -r requirements.txt`
3. **Start Command:** `python __main__.py`
4. **Environment** bo'limiga yuqoridagi jadvaldagi ENV'larni kiriting
   (`WEBHOOK_URL`ni hozircha bo'sh qoldirsangiz ham bo'ladi - Render
   `RENDER_EXTERNAL_URL`ni o'zi avtomatik beradi)
5. Deploy qiling
6. `WORD_BASE` fayli konteynerda mavjud bo'lishi kerak - aks holda bot
   ishga tushishning o'zidayoq xato beradi (croco/gallows uchun kerak)
7. Bepul tarifda servis harakatsizlikdan uxlab qoladi — **UptimeRobot**
   (yoki shunga o'xshash) bilan har 5-10 daqiqada asosiy manzilga ping
   yuborib turing, aks holda Telegram'dan kelayotgan xabarlar servis
   uyg'onguncha yo'qolib qolishi mumkin

## 4. Lokal test qilish
```bash
cp .env.example .env
# .env faylni haqiqiy qiymatlar bilan toʻldiring
pip install -r requirements.txt --break-system-packages
python __main__.py
```

**MongoDB kerak emas** — barcha ma'lumotlar yo yuqoridagi Telegram guruhida
(doimiy), yo dastur xotirasida (vaqtinchalik: faol o'yinlar) saqlanadi. Faqat
bitta process/dyno bilan ishlang — xotiradagi faol o'yin holati processlar
o'rtasida almashinmaydi.

## Superadmin buyruqlari (asosiylari)
- `/narx <nom> <qiymat>` — shop narxini o'zgartirish
- `/sozlama <nom> <qiymat>` — referral/olmos kurslari va h.k.
- `/pulber <user_id yoki javoban> <miqdor> [olmos]` — pul/olmos berish
- `/pulkochir <kimdan> <kimga> <miqdor> [olmos]` — ikki user orasida o'tkazish
- `/kanalqoshish <kanal_id> <mukofot$>` — bonus kanal qo'shish (bot o'sha yerda admin bo'lishi kerak)
- `/kimkim` — (guruhda) faol o'yindagi rollarni maxfiy ko'rish
- `/oldir` — (o'yinchiga javoban) uni o'yindan o'ldirish
- `/rol <rol_nomi>` — (o'yinchiga javoban) uning rolini o'zgartirish
- `/reload` — Telegram-DB'ni qayta yuklash
- `.ban` `.unban` `.mute minut.soat.kun.oy` `.unmute` `.info` — (guruh a'zosiga javoban, guruh admin yoki superadmin uchun)

## Til
`/til <ru|uz|tr|en|kk>` — asosiy o'yin (mafia/croco/gallows) shu 5 tilda. Yangi
economy/shop/premium buyruqlari hozircha faqat o'zbekcha.

## Ma'lum cheklovlar
- Croco/Gallows so'z bazasi va harf tekshiruvi faqat rus tilida
- Telegram Stars orqali olmos xaridi kod jihatidan tayyor, lekin haqiqiy
  to'lov bilan hali sinalmagan
