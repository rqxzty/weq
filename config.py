"""Настройки проекта: пути, кодировка CSV, параметры ИИ."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Пути
DATA_PATH = BASE_DIR / "data" / "reviews.csv"
OUTPUT_PATH = BASE_DIR / "output" / "reviews_analyzed.xlsx"
LOG_PATH = BASE_DIR / "app.log"

# Формат входного CSV («как в русском Excel»)
CSV_ENCODING = "cp1251"
CSV_SEP = ";"

# ИИ: "gemini" или "groq"
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Названия моделей меняются — при ошибке 404 проверьте актуальное имя в документации
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

# Надёжность
REQUEST_DELAY = 2   # пауза между отзывами (сек), защита от 429
MAX_ATTEMPTS = 2    # сколько раз пробовать один отзыв
RETRY_DELAY = 5     # пауза перед повторной попыткой (сек)
