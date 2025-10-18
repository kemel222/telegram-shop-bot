from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text, Enum, BigInteger
)
from sqlalchemy.orm import relationship
from database.database import Base
import enum


class DeliveryType(str, enum.Enum):
    PICKUP_CENTER = "pickup_center"  # Самовывоз из Центра
    PICKUP_TC = "pickup_tc"  # Самовывоз из ТЦ
    DELIVERY = "delivery"  # Доставка


class PaymentMethod(str, enum.Enum):
    SBP_ONLINE = "sbp_online"  # СБП онлайн
    SBP_ON_RECEIPT = "sbp_on_receipt"  # СБП при получении
    CASH = "cash"  # Наличными
    BALANCE = "balance"  # Баланс сайта


class OrderStatus(str, enum.Enum):
    PENDING = "pending"  # Ожидает подтверждения
    PAYMENT_PENDING = "payment_pending"  # Ожидает оплаты
    PAID = "paid"  # Оплачен
    PROCESSING = "processing"  # В обработке
    READY = "ready"  # Готов к выдаче
    COMPLETED = "completed"  # Завершен
    CANCELLED = "cancelled"  # Отменен


class PromoCodeType(str, enum.Enum):
    PERCENT = "percent"  # Скидка в процентах
    FIXED = "fixed"  # Скидка фиксированная в рублях
    BALANCE = "balance"  # Пополнение баланса


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    balance = Column(Float, default=0.0)
    cashback_balance = Column(Float, default=0.0)  # Кешбек баланс отдельно
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cart = relationship("Cart", back_populates="user", uselist=False)
    orders = relationship("Order", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")
    cashback_transactions = relationship("CashbackTransaction", back_populates="user")


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    cashback_percent = Column(Float, default=3.5)  # Процент кешбека по категории (по умолчанию 3.5%)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    image_url = Column(String(500), nullable=True)
    quantity = Column(Integer, default=0)  # Количество на складе
    is_available = Column(Boolean, default=True)
    has_variants = Column(Boolean, default=False)  # Есть ли варианты (вкусы)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("Category", back_populates="products")
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
    favorites = relationship("Favorite", back_populates="product")
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")


class ProductVariant(Base):
    __tablename__ = "product_variants"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    name = Column(String(255), nullable=False)  # Название вкуса/варианта
    price = Column(Float, nullable=True)  # Цена варианта (если отличается от основной)
    quantity = Column(Integer, default=0)  # Количество конкретного варианта
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="variants")
    cart_items = relationship("CartItem", back_populates="variant")
    order_items = relationship("OrderItem", back_populates="variant")


class Cart(Base):
    __tablename__ = "carts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="cart")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)  # Вариант товара
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")
    variant = relationship("ProductVariant", back_populates="cart_items")


class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Delivery info
    delivery_type = Column(Enum(DeliveryType), nullable=False)
    delivery_address = Column(String(500), nullable=True)
    delivery_time_slot = Column(String(50), nullable=True)  # Временной слот для самовывоза
    
    # Contact info
    customer_name = Column(String(255), nullable=False)
    customer_phone = Column(String(50), nullable=False)
    
    # Payment info
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_status = Column(String(50), default="pending")
    
    # Pricing
    subtotal = Column(Float, nullable=False)  # Сумма без доставки
    delivery_cost = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)  # Скидка от промокода
    total = Column(Float, nullable=False)
    
    # Promo code
    promo_code_used = Column(String(50), nullable=True)
    
    # Status
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment_screenshots = relationship("PaymentScreenshot", back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    variant_id = Column(Integer, ForeignKey("product_variants.id"), nullable=True)  # Вариант товара
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)  # Цена на момент заказа
    variant_name = Column(String(255), nullable=True)  # Название варианта на момент заказа
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
    variant = relationship("ProductVariant", back_populates="order_items")


class PromoCode(Base):
    __tablename__ = "promo_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    type = Column(Enum(PromoCodeType), nullable=False)
    value = Column(Float, nullable=False)  # Процент или сумма
    is_active = Column(Boolean, default=True)
    usage_limit = Column(Integer, nullable=True)  # Лимит использований (None = безлимитный)
    usage_count = Column(Integer, default=0)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CashbackTransaction(Base):
    __tablename__ = "cashback_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(Float, nullable=False)  # Сумма кешбека
    cashback_percent = Column(Float, nullable=False)  # Процент кешбека на момент начисления
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="cashback_transactions")
    order = relationship("Order")


class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="favorites")
    product = relationship("Product", back_populates="favorites")


class PaymentScreenshot(Base):
    __tablename__ = "payment_screenshots"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    file_id = Column(String(255), nullable=False)  # Telegram file_id
    file_path = Column(String(500), nullable=True)  # Путь к сохраненному файлу
    is_verified = Column(Boolean, default=False)
    verified_by_admin_id = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)
    
    # Relationships
    order = relationship("Order", back_populates="payment_screenshots")

