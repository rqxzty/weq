"""Чтение и очистка CSV с отзывами."""
import logging
from pathlib import Path

import pandas as pd

import config

logger = logging.getLogger(__name__)


def read_reviews(path: Path = config.DATA_PATH) -> pd.DataFrame:
    """Читает CSV (cp1251, разделитель ';'). Ошибки чтения логирует и пробрасывает дальше."""
    try:
        return pd.read_csv(path, sep=config.CSV_SEP, encoding=config.CSV_ENCODING)
    except FileNotFoundError:
        logger.error("Файл не найден: %s", path)
        raise
    except (UnicodeDecodeError, pd.errors.ParserError) as exc:
        logger.error("Не удалось прочитать %s (проверьте cp1251 и ';'): %s", path, exc)
        raise


def clean_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """Удаляет отзывы с пустым текстом, приводит текст к str."""
    before = len(df)
    df = df.dropna(subset=["text"]).copy()
    df["text"] = df["text"].astype(str).str.strip()
    df = df[df["text"] != ""].reset_index(drop=True)
    removed = before - len(df)
    if removed:
        logger.warning("Удалено пустых отзывов: %d", removed)
    return df


def load_reviews(path: Path = config.DATA_PATH) -> pd.DataFrame:
    """Читает и чистит CSV. Возвращает готовый DataFrame."""
    df = clean_reviews(read_reviews(path))
    logger.info("Успешно загружено %d отзывов", len(df))
    return df
