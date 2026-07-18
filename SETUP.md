# O'rnatish

## 1. config.py yaratish
```bash
cp config.py.sample config.py
```
Va to'ldiring:
- `TOKEN` — @BotFather'dan olingan token
- `ADMIN_ID` — sizning Telegram user ID'ingiz (superadmin)
- `DB_CHAT_ID` — pastga qarang
- `WORD_BASE` — croco/gallows uchun rus so'zlar bazasi fayli yo'li

## 2. DB_CHAT_ID uchun supergroup yaratish
1. Yopiq (private) **supergroup** yarating (oddiy guruh emas)
2. Botni o'sha guruhga qo'shing va **admin** qiling (pin, edit, delete, invite huquqlari bilan)
3. Guruh ID'sini oling (masalan @getidsbot yordamida yoki botga biror xabar yozib, `update.message.chat.id` orqali) — odatda `-100` bilan boshlanadi
4. Shu ID'ni `config.py`dagi `DB_CHAT_ID`ga yozing

Bu guruhda pul/olmos/statistika/shop/til/premium ma'lumotlari bitta JSON fayl (document) sifatida saqlanadi va pin qilinadi. Diskni istalgancha tozalasangiz ham (masalan Render qayta deploy qilganda) — bot shu pin qilingan fayldan avtomatik tiklanadi.

## 3. O'rnatish
```bash
pip install -r requirements.txt --break-system-packages
python -m src
```

**MongoDB kerak emas** — barcha ma'lumotlar yo tepadagi Telegram guruhida (doimiy), yo dastur xotirasida (vaqtinchalik: faol o'yinlar) saqlanadi.

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
`/til <ru|uz|tr|en|kk>` — asosiy o'yin (mafia/croco/gallows) shu 5 tilda. Yangi economy/shop/premium buyruqlari hozircha faqat o'zbekcha.

## Ma'lum cheklovlar
- Croco/Gallows so'z bazasi va harf tekshiruvi faqat rus tilida (alohida so'z bazalari kerak boshqa tillar uchun)
- Shop itemlari (Hujjatlar/Ximoya/Faol rol/2x ovoz) o'yin mexanikasiga ulangan, lekin ularning aniq ma'nosi (masalan "Hujjatlar" = kunduzi qamoqdan qutqaradi) mening taxminim - agar boshqacha bo'lishi kerak bo'lsa, `stages.py`dagi `last_words_criminal`/`last_words_victim` va `handlers.py`dagi `start_game`/`vote` funksiyalarini o'zgartirish kerak bo'ladi
