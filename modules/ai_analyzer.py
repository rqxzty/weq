"""Общение с нейросетью и разбор её ответа."""
import json
import logging
import re
import time
from functools import lru_cache

import config
from prompts import REVIEW_PROMPT

logger = logging.getLogger(__name__)

VALID_SENTIMENTS = {"positive", "negative", "neutral"}


def error_result() -> dict:
    """Результат-заглушка: скрипт не падает, а идёт к следующему отзыву."""
    return {"sentiment": "error", "main_problem": None, "urgency": None}


def extract_json(raw: str) -> dict:
    """Вырезает JSON из ответа ИИ (убирает ```json ... ``` и лишний текст) и возвращает dict.

    Бросает ValueError, если JSON найти или разобрать не удалось.
    """
    if not raw or not raw.strip():
        raise ValueError("Пустой ответ от ИИ")
    cleaned = re.sub(r"```(?:json)?", "", raw)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("В ответе нет JSON-объекта")
    data = json.loads(cleaned[start:end + 1])  # JSONDecodeError — подкласс ValueError
    if not isinstance(data, dict):
        raise ValueError("JSON не является объектом")
    return data


def normalize(data: dict) -> dict:
    """Приводит ответ ИИ к ожидаемому виду; при мусоре бросает ValueError."""
    sentiment = str(data.get("sentiment", "")).strip().lower()
    if sentiment not in VALID_SENTIMENTS:
        raise ValueError(f"Недопустимая тональность: {sentiment!r}")

    problem = data.get("main_problem")
    if problem in (None, "", "null"):
        problem = None

    try:
        urgency = max(1, min(5, int(data.get("urgency"))))
    except (TypeError, ValueError):
        raise ValueError(f"Недопустимая срочность: {data.get('urgency')!r}")

    return {"sentiment": sentiment, "main_problem": problem, "urgency": urgency}


@lru_cache(maxsize=1)
def _gemini_client():
    from google import genai  # импорт здесь, чтобы тесты работали без ключей и сети
    return genai.Client(api_key=config.GEMINI_API_KEY)


@lru_cache(maxsize=1)
def _groq_client():
    from groq import Groq
    return Groq(api_key=config.GROQ_API_KEY)


def _call_model(prompt: str) -> str:
    """Отправляет промпт выбранному провайдеру и возвращает сырой текст ответа."""
    if config.AI_PROVIDER == "gemini":
        response = _gemini_client().models.generate_content(
            model=config.GEMINI_MODEL, contents=prompt
        )
        return response.text
    if config.AI_PROVIDER == "groq":
        response = _groq_client().chat.completions.create(
            model=config.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return response.choices[0].message.content
    raise ValueError(f"Неизвестный AI_PROVIDER: {config.AI_PROVIDER!r}")


def analyze_review(text: str) -> dict:
    """Анализирует один отзыв. Никогда не бросает исключение: при сбое вернёт error_result()."""
    prompt = REVIEW_PROMPT.format(text=text)
    for attempt in range(1, config.MAX_ATTEMPTS + 1):
        try:
            return normalize(extract_json(_call_model(prompt)))
        except Exception as exc:  # сеть, лимиты, мусор от ИИ — всё обрабатываем одинаково
            logger.error("Попытка %d/%d не удалась: %s", attempt, config.MAX_ATTEMPTS, exc)
            if attempt < config.MAX_ATTEMPTS:
                time.sleep(config.RETRY_DELAY)
    return error_result()
