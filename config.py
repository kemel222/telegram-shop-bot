from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Telegram Bots
    SHOP_BOT_TOKEN: str = "8457344552:AAFQ7eYowuE1JNwh5j5sWUfaOlYqZxyiQoU"
    ADMIN_BOT_TOKEN: str = "8156129677:AAGFRN8ZgCuZYmueNM1q7Mh_IHKtV4oFZRg"
    ADMIN_IDS: str = "6114889085,820140184"
    
    # Manager
    MANAGER_USERNAME: str = "x32asm"
    MANAGER_ID: str = ""  # Опционально
    
    # Database (MySQL)
    DATABASE_URL: str = "mysql+aiomysql://shop_user:password@localhost:3306/shop_db"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    SECRET_KEY: str
    
    # Payment
    SBP_PHONE: str = "+79991234567"
    SBP_BANK_NAME: str = "Сбербанк"
    
    # Cashback System
    CASHBACK_PODS_PERCENT: float = 2.5  # Кешбек на поды
    CASHBACK_DEFAULT_PERCENT: float = 3.5  # Кешбек на все остальное
    
    # Developer
    DEVELOPER_USERNAME: str = "x32asm"
    DEVELOPER_LINK: str = "https://t.me/x32asm"
    
    # Delivery
    DELIVERY_PRICE: int = 300
    
    # WebApp
    WEBAPP_URL: str = "https://your-webapp-url.com"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
    @property
    def admin_ids_list(self) -> List[int]:
        return [int(admin_id.strip()) for admin_id in self.ADMIN_IDS.split(",")]
    
    @property
    def manager_id_int(self) -> int | None:
        if self.MANAGER_ID and self.MANAGER_ID.strip():
            return int(self.MANAGER_ID.strip())
        return None


settings = Settings()
