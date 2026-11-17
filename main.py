"""Точка входа: python main.py --analyze | --stats"""
import argparse
import logging
import sys
import time

import config
from modules import ai_analyzer, data_loader, exporter

logger = logging.getLogger("main")


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s",
        handlers=[
            logging.FileHandler(config.LOG_PATH, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def run_analyze() -> int:
    try:
        df = data_loader.load_reviews()
    except Exception:
        logger.error("Не удалось загрузить данные, анализ остановлен")
        return 1

    results = []
    total = len(df)
    for i, row in enumerate(df.itertuples(index=False), start=1):
        preview = row.text[:50].replace("\n", " ")
        logger.info("Обработка отзыва %d/%d (id=%s): %s", i, total, row.id, preview)
        results.append(ai_analyzer.analyze_review(row.text))
        if i < total:
            time.sleep(config.REQUEST_DELAY)

    out = df.copy()
    for key in ("sentiment", "main_problem", "urgency"):
        out[key] = [r[key] for r in results]

    failed = sum(r["sentiment"] == "error" for r in results)
    if failed:
        logger.warning("Не удалось проанализировать отзывов: %d из %d", failed, total)

    exporter.save_to_excel(out)
    return 0


def run_stats() -> int:
    try:
        stats = exporter.calc_stats(exporter.read_report())
    except FileNotFoundError:
        return 1
    print(
        f"Всего отзывов: {stats['total']}. "
        f"Негативных: {stats['negative']}. "
        f"Средняя срочность: {stats['avg_urgency']}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="AI-сортировщик отзывов")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--analyze", action="store_true", help="чтение -> ИИ -> Excel")
    mode.add_argument("--stats", action="store_true", help="статистика по готовому Excel")
    args = parser.parse_args()

    setup_logging()
    return run_analyze() if args.analyze else run_stats()


if __name__ == "__main__":
    sys.exit(main())
