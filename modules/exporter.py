"""Сохранение результатов в Excel, раскраска и статистика."""
import logging
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill

import config

logger = logging.getLogger(__name__)


def _fill(color: str) -> PatternFill:
    return PatternFill(start_color=color, end_color=color, fill_type="solid")


SENTIMENT_FILLS = {
    "positive": _fill("C6EFCE"),  # зелёный
    "negative": _fill("FFC7CE"),  # красный
    "neutral": _fill("FFEB9C"),   # жёлтый
    "error": _fill("D9D9D9"),     # серый — сбой анализа
}


def save_to_excel(df: pd.DataFrame, path: Path = config.OUTPUT_PATH) -> None:
    """Сохраняет DataFrame в xlsx и красит колонку sentiment."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(path, index=False)

    wb = load_workbook(path)
    ws = wb.active

    header = [cell.value for cell in ws[1]]
    sentiment_col = header.index("sentiment") + 1
    for row in range(2, ws.max_row + 1):
        cell = ws.cell(row=row, column=sentiment_col)
        fill = SENTIMENT_FILLS.get(cell.value)
        if fill:
            cell.fill = fill

    # Оформление: жирные заголовки, ширина колонок, перенос текста
    widths = {"id": 6, "date": 12, "text": 60, "sentiment": 12, "main_problem": 40, "urgency": 10}
    for idx, name in enumerate(header, start=1):
        ws.cell(row=1, column=idx).font = Font(bold=True)
        letter = ws.cell(row=1, column=idx).column_letter
        ws.column_dimensions[letter].width = widths.get(name, 15)
        if name in ("text", "main_problem"):
            for row in range(2, ws.max_row + 1):
                ws.cell(row=row, column=idx).alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"

    wb.save(path)
    logger.info("Отчёт сохранён: %s", path)


def calc_stats(df: pd.DataFrame) -> dict:
    """Считает статистику по готовому отчёту."""
    urgency = pd.to_numeric(df["urgency"], errors="coerce").dropna()
    return {
        "total": len(df),
        "negative": int((df["sentiment"] == "negative").sum()),
        "avg_urgency": round(float(urgency.mean()), 2) if len(urgency) else 0.0,
    }


def read_report(path: Path = config.OUTPUT_PATH) -> pd.DataFrame:
    """Читает готовый Excel-отчёт."""
    try:
        return pd.read_excel(path)
    except FileNotFoundError:
        logger.error("Отчёт не найден: %s. Сначала запустите --analyze", path)
        raise
