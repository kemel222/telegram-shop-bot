#!/usr/bin/env python3
"""
Скрипт для запуска API сервера
"""

import uvicorn
import os
import sys

# Добавляем корневую директорию проекта в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Запуск API сервера...")
    print("📡 Адрес: http://0.0.0.0:8000")
    print("📚 Документация: http://0.0.0.0:8000/docs")
    print("🔍 Health check: http://0.0.0.0:8000/health")
    print("=" * 50)
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )