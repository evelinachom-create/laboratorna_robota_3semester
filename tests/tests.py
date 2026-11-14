import pytest
from main import (tokenize_text, check_text, lemmatize_text, analyzer)

def test_tokenize_text_basic():
    text = "Дощ періщив всі дні безперервно."
    assert tokenize_text(text) == ["Дощ", "періщив", "всі", "дні", "безперервно"]


def test_tokenize_text_special_chars():
    text = "На ґанку об'єднані друзі збирали соковиту м'яту."
    assert tokenize_text(text) == ["На", "ґанку", "об'єднані", "друзі", "збирали", "соковиту", "м'яту"]


def test_analyze_word_interjection():
    res = analyzer.analyze_word("ой")
    assert res["Слово"] == "ой"
    assert res["Лема"] == "ой"
    assert res["Частина мови"] == "вигук"
    assert res["Відмінок"] == "—"


def test_analyze_word_predicative():
    res = analyzer.analyze_word("треба")
    assert res["Слово"] == "треба"
    assert res["Лема"] == "треба"
    assert res["Частина мови"] == "предикатив(станівник)"
    assert res["Рід"] == "—"


def test_analyze_word_standard_noun():
    res = analyzer.analyze_word("крига")
    assert res["Слово"] == "крига"
    assert res["Лема"] == "крига"
    assert res["Частина мови"] == "іменник"
    assert res["Відмінок"] == "називний"
    assert res["Рід"] == "жіночий рід"
    assert res["Число"] == "однина"


def test_analyze_text_valid():
    results = analyze_text("Дощ падає.")
    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]["Слово"] == "Дощ"
    assert results[1]["Частина мови"] == "дієслово"


def test_analyze_text_empty_raises_error():
    with pytest.raises(ValueError, match="Введення початкового тексту є обов'язковим."):
        analyze_text("")


def test_analyze_text_no_tokens_raises_error():
    with pytest.raises(ValueError, match="У введеному тексті не знайдено слів для аналізу."):
        analyze_text("12345 67890")


def test_lemmatize_text():
    result = lemmatize_text("Сонячні промені розливалися кімнатою.")
    assert result == "сонячний промінь розливатися кімната"