import pytest
from main import analyze_text

def test_text1_detailed():
    file_path = "text1.txt"

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
        
    results = analyze_text(text)
    
    for row in results:
        assert "Слово" in row
        assert "Лема" in row
        assert "Частина мови" in row

        assert row["Слово"].strip() != ""
        assert row["Лема"].strip() != ""


    greece_entries = [r for r in results if r["Слово"].lower() == "греції"]
    
    assert len(greece_entries) > 0, "Слово 'Греції' мало б бути знайдене в тексті!"
    
    word_info = greece_entries[0]
    assert word_info["Лема"] == "греція"
    assert word_info["Частина мови"] == "іменник"

def test_empty_file_raises_error():
    empty_file_path = "text_empty.txt"
    
    with open(empty_file_path, "r", encoding="utf-8") as f:
        empty_text = f.read()
        
    with pytest.raises(ValueError, match="Поле порожнє. Введіть текст українською мовою."):
        analyze_text(empty_text)