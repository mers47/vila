"""Commerce Agent OS — Litestar + HTMX Dashboard
Stack 2026: Litestar 2.24 replaces FastAPI/SQLAdmin.
msgspec replaces Pydantic (10x faster). HTMX replaces React.
"""
from __future__ import annotations

import os, logging
from datetime import datetime
from pathlib import Path

from litestar import Litestar, get, Request
from litestar.contrib.htmx.response import HTMXTemplate
from litestar.template.config import TemplateConfig
from litestar.di import Provide
from litestar.config.cors import CORSConfig

import msgspec
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.main import Database
from bot.database.models.main import User, Product, Order

logger = logging.getLogger(__name__)


class DashboardStats(msgspec.Struct):
    total_users: int = 0
    total_products: int = 0
    total_orders: int = 0
    total_revenue: int = 0
    orders_today: int = 0
    revenue_today: int = 0


async def provide_db_session() -> AsyncSession:
    async with Database().session() as session:
        yield session


@get("/")
async def dashboard(request: Request, db: AsyncSession) -> HTMXTemplate:
    total_users = (await db.execute(select(func.count(User.telegram_id)))).scalar() or 0
    total_products = (await db.execute(select(func.count(Product.id)))).scalar() or 0
    total_orders = (await db.execute(select(func.count(Order.id)))).scalar() or 0

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    orders_today = (await db.execute(
        select(func.count(Order.id)).where(Order.created_at >= today)
    )).scalar() or 0

    revenue = (await db.execute(
        select(func.coalesce(func.sum(Order.total_rial), 0))
        .where(Order.order_status.in_(['confirmed', 'delivered', 'shipped']))
    )).scalar() or 0

    stats = DashboardStats(
        total_users=total_users,
        total_products=total_products,
        total_orders=total_orders,
        orders_today=orders_today,
        total_revenue=int(revenue),
        revenue_today=0,
    )

    raw = (await db.execute(
        select(Order).order_by(desc(Order.created_at)).limit(10)
    )).scalars().all()

    return HTMXTemplate(
        template_name="dashboard.html",
        context={"stats": stats, "recent_orders": raw},
    )


@get("/products")
async def list_products(request: Request, db: AsyncSession) -> HTMXTemplate:
    page = max(1, int(request.query_params.get("page", 1)))
    per_page, offset = 20, (page - 1) * 20
    total = (await db.execute(select(func.count(Product.id)))).scalar() or 0
    raw = (await db.execute(
        select(Product).order_by(desc(Product.updated_at)).limit(per_page).offset(offset)
    )).scalars().all()
    return HTMXTemplate(
        template_name="products.html",
        context={"products": raw, "page": page, "total": total,
                 "total_pages": (total + 19) // 20},
    )


@get("/orders")
async def list_orders(request: Request, db: AsyncSession) -> HTMXTemplate:
    page = max(1, int(request.query_params.get("page", 1)))
    per_page, offset = 20, (page - 1) * 20
    status = request.query_params.get("status")
    q = select(Order).order_by(desc(Order.created_at))
    if status:
        q = q.where(Order.order_status == status)
    total = (await db.execute(select(func.count(Order.id)))).scalar() or 0
    raw = (await db.execute(q.limit(per_page).offset(offset))).scalars().all()
    return HTMXTemplate(
        template_name="orders.html",
        context={"orders": raw, "page": page, "total": total,
                 "total_pages": (total + 19) // 20, "status_filter": status},
    )


@get("/users")
async def list_users(request: Request, db: AsyncSession) -> HTMXTemplate:
    page = max(1, int(request.query_params.get("page", 1)))
    per_page, offset = 20, (page - 1) * 20
    total = (await db.execute(select(func.count(User.telegram_id)))).scalar() or 0
    raw = (await db.execute(
        select(User).order_by(desc(User.registration_date)).limit(per_page).offset(offset)
    )).scalars().all()
    return HTMXTemplate(
        template_name="users.html",
        context={"users": raw, "page": page, "total": total,
                 "total_pages": (total + 19) // 20},
    )


def create_litestar_app(bot=None) -> Litestar:
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(exist_ok=True)

    from litestar.contrib.jinja2 import Jinja2TemplateEngine
    return Litestar(
        route_handlers=[dashboard, list_products, list_orders, list_users],
        template_config=TemplateConfig(
            directory=templates_dir,
            engine=Jinja2TemplateEngine,
        ),
        dependencies={"db": Provide(provide_db_session)},
        cors_config=CORSConfig(allow_origins=["*"]),
        debug=os.getenv("DEBUG") == "1",
    )
