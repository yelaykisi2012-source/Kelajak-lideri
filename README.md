# KELAJAK LIDERI — 20-MAKTAB

Flask asosidagi o‘quvchilar tashabbusi va g‘oyalar platformasi.

## Internetga joylash

GitHub repozitoriyasini qo‘llaydigan Python hosting xizmatida web service yarating va quyidagilarni kiriting:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn wsgi:app --bind 0.0.0.0:$PORT`
- `KELAJAK_SECRET_KEY`: tasodifiy, maxfiy, kamida 32 belgili qiymat.
- `KELAJAK_ADMIN_PASSWORD`: kamida 12 belgili, noyob administrator paroli; standart sinov parolini ishlatmang.
- `KELAJAK_ADMIN_USERNAME`: ixtiyoriy; belgilanmasa `maslahatchi` ishlatiladi.
- `KELAJAK_DB_PATH`: ixtiyoriy; doimiy diskdagi `kelajak_lideri.db` fayli yo‘li.

`wsgi.py` xavfsiz production maxfiy kalitlari/paroli sozlanganini tekshiradi, so‘ng SQLite jadvallarini yaratib boshlang‘ich tadbirlarni qo‘shadi. Ma’lumotlar bazasi va maxfiy kalitlar GitHub’ga joylanmaydi. Hostingdagi yangi nusxa bo‘sh bazadan boshlanadi; mavjud bazadagi ma’lumotlarni ko‘chirish kerak bo‘lsa, bazani alohida va xavfsiz migratsiya qiling. Hosting diski vaqtinchalik bo‘lishi mumkin. Haqiqiy foydalanuvchilar ma’lumotlarini saqlash uchun hostingda doimiy diskni yoqing va `KELAJAK_DB_PATH` ni unga sozlang.

GitHub’ga push qilish saytni avtomatik ishga tushirmaydi; hosting xizmatida web service’ni alohida sozlang.

## Mahalliy ishga tushirish

```bash
pip install -r requirements.txt
python app.py
```

Mahalliy manzil: `http://127.0.0.1:5000`
