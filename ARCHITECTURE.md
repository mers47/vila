# Commerce Agent OS — Architecture Decision Record

## انتخاب‌های کلیدی

| انتخاب | رد شده | دلیل |
|--------|--------|------|
| Litestar 2.24 | FastAPI | 2.x stable, DTO system, msgspec native, 2x throughput |
| msgspec | Pydantic v2 | 10x faster serialization, zero-copy |
| HTMX 2.0 | React/Vue | Zero build step, 100KB, HTML-native |
| Typesense | Meilisearch | Better Persian tokenizer, ONNX runtime |
| SQLAlchemy 2.0 | Piccolo/Tortoise | Complex query capability unmatched |
| aiogram 3.22 | python-telegram-bot | FSM, middleware, routers, mature v3 |
| PostgreSQL 16 | SQLite | pgvector + JSONB + asyncpg |
| Redis 7 | Memcached | Pub/Sub + FSM storage |
| aiohttp | httpx | Fastest async HTTP for 30 req/s |

## اشتباهات رایج که مرتکب نشدیم
1. React dashboard → HTMX (۶ خط JS)
2. FastAPI (7 سال 0.x) → Litestar (2.x stable)
3. Pydantic → msgspec (10x faster)
4. Meilisearch (RAM-bound) → Typesense (C++)
5. Fork per platform → Provider Pattern
6. تاریخ شمسی در DB → UTC + display
7. float برای قیمت → Integer ریال

## Docker Stack (۶ کانتینر)
```yaml
services:
  postgres:16-pgvector
  redis:7
  typesense:27
  commerce-agent (Litestar + aiogram)
  worker-eitaa
  worker-rubika
```
