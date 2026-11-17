# AI-Сортировщик отзывов

Консольное приложение: берёт CSV с клиентскими отзывами, прогоняет каждый через нейросеть
(тональность, главная проблема, срочность) и сохраняет Excel-отчёт с цветовой подсветкой.

**Схема:** `CSV (cp1251, ;) → очистка → ИИ → JSON → Excel → CLI`

## Возможности
- Чтение «грязного» CSV (кодировка `cp1251`, разделитель `;`), удаление пустых отзывов
- Анализ через Gemini (по умолчанию) или Groq
- Устойчивый разбор ответа ИИ: вырезает JSON из ```` ```json ... ``` ````, при сбое пишет `ERROR` в лог и идёт дальше
- Excel-отчёт: колонка `sentiment` — зелёная / красная / жёлтая (серая — если анализ не удался)
- Логи в консоль и в `app.log`
- Режим `--stats`: статистика по готовому отчёту без запросов к ИИ

## Установка
```bash
git clone <ссылка-на-ваш-репозиторий>
cd ai-review-sorter
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Настройка `.env`
1. Получите бесплатный ключ: [Google AI Studio](https://aistudio.google.com) (Gemini) или [Groq Console](https://console.groq.com).
2. Скопируйте `.env.example` в `.env` и вставьте ключ:
```
AI_PROVIDER=gemini
GEMINI_API_KEY=ваш_ключ
```
Для Groq: `AI_PROVIDER=groq` и `GROQ_API_KEY=ваш_ключ`.

> Названия моделей у провайдеров меняются. Если получаете ошибку «model not found»,
> задайте актуальное имя в `.env` через `GEMINI_MODEL` или `GROQ_MODEL`.

## Запуск
```bash
python make_sample_csv.py     # создать data/reviews.csv (cp1251, ';') — один раз
python main.py --analyze      # чтение -> ИИ -> output/reviews_analyzed.xlsx
python main.py --stats        # статистика по готовому Excel
pytest                        # тесты
```
Пример вывода `--stats`: `Всего отзывов: 12. Негативных: 4. Средняя срочность: 2.67`

## Структура
```
ai-review-sorter/
├── main.py              # CLI (argparse)
├── config.py            # пути, кодировка, настройки ИИ
├── prompts.py           # промпт для нейросети
├── make_sample_csv.py   # генератор тестового CSV
├── modules/
│   ├── data_loader.py   # чтение и очистка CSV
│   ├── ai_analyzer.py   # запрос к ИИ, разбор JSON
│   └── exporter.py      # Excel, раскраска, статистика
├── data/reviews.csv     # входные данные
├── output/              # результаты
└── tests/test_analyzer.py
```

## Заметки
- Эмодзи нельзя сохранить в `cp1251`, поэтому в тестовых данных используются смайлики `:)` и `:(`.
- Между запросами пауза 2 секунды (защита от `429 Too Many Requests`), настраивается в `config.py`.
- Файл `.env` с ключом не коммитить.
