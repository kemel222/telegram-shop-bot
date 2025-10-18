from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import products, cart, orders, promo, users, admin
from database.database import init_db

app = FastAPI(
    title="Telegram Shop API",
    description="API для телеграм-магазина с мини-приложением",
    version="1.0.0"
)

# Настройка CORS для веб-приложения
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(cart.router, prefix="/api/cart", tags=["Cart"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(promo.router, prefix="/api/promo", tags=["Promo Codes"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


@app.on_event("startup")
async def startup():
    """Инициализация при запуске"""
    await init_db()
    print("✅ Database initialized")


@app.get("/")
async def root():
    return {
        "message": "Telegram Shop API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

