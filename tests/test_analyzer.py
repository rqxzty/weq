import pytest

from modules import ai_analyzer
from modules.ai_analyzer import extract_json, normalize


def test_extract_json_from_markdown_with_extra_text():
    raw = (
        "Конечно! Вот результат анализа:\n"
        "```json\n"
        '{"sentiment": "negative", "main_problem": "Долгая доставка", "urgency": 4}\n'
        "```\n"
        "Надеюсь, это поможет!"
    )
    assert extract_json(raw) == {
        "sentiment": "negative",
        "main_problem": "Долгая доставка",
        "urgency": 4,
    }


def test_extract_json_plain():
    assert extract_json('{"sentiment": "positive"}') == {"sentiment": "positive"}


@pytest.mark.parametrize("raw", ["", "   ", "никакого json тут нет", "{сломанный json"])
def test_extract_json_raises_on_garbage(raw):
    with pytest.raises(ValueError):
        extract_json(raw)


def test_normalize_clamps_urgency_and_handles_null():
    result = normalize({"sentiment": "Positive", "main_problem": "null", "urgency": "9"})
    assert result == {"sentiment": "positive", "main_problem": None, "urgency": 5}


def test_normalize_rejects_unknown_sentiment():
    with pytest.raises(ValueError):
        normalize({"sentiment": "angry", "urgency": 3})


def test_analyze_review_returns_error_dict_instead_of_crashing(monkeypatch):
    def boom(prompt):
        raise ConnectionError("нет сети")

    monkeypatch.setattr(ai_analyzer, "_call_model", boom)
    monkeypatch.setattr(ai_analyzer.time, "sleep", lambda s: None)
    assert ai_analyzer.analyze_review("любой отзыв")["sentiment"] == "error"
