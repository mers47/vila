# Commerce Agent OS

فروشگاه هوشمند چندکاناله — تلگرام، ایتا، روبیکا

## استک ۲۰۲۶
- **API**: Litestar 2.24 + HTMX (بدون React)
- **ORM**: SQLAlchemy 2.0 async + PostgreSQL 16 + pgvector
- **Serialization**: msgspec (10x سریع‌تر از Pydantic)
- **Search**: Typesense (توکنایزر فارسی)
- **Cache**: Redis 7
- **Telegram**: aiogram 3.22
- **Eitaa**: REST API (eitaayar.ir)
- **Rubika**: rubpy 7.3.5

## ویژگی‌ها
- ✅ کاملاً فارسی — صفر کاراکتر روسی
- ✅ کالای دیجیتال + فیزیکی
- ✅ سگمنت‌بندی مشتریان
- ✅ ارسال گروهی هدفمند
- ✅ کیف پول داخلی
- ✅ پنل مدیریت با HTMX
- ✅ معماری Multi-Provider (یک کد، سه پلتفرم)

## راه‌اندازی
```bash
pip install -r requirements.txt
cp .env.example .env  # تنظیم متغیرها
python run.py
```

## معماری

```
┌──────────────────────────────────────┐
│         Litestar Dashboard           │
│      (HTMX + msgspec + Chart.js)     │
├──────────────────────────────────────┤
│         Aiogram Dispatcher           │
│  (handlers, middleware, FSM, i18n)   │
├──────────────────────────────────────┤
│       Multi-Channel Gateway          │
├──────────┬──────────┬───────────────┤
│ Telegram │  Eitaa   │    Rubika     │
│(aiogram) │ (REST)   │   (rubpy)     │
└──────────┴──────────┴───────────────┘
```

## لایسنس
MIT — برگرفته از interlumpen/Telegram-shop
