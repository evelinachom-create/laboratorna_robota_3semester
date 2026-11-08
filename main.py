import re
import pymorphy3

max_chars = 4000
max_words = 1000

VALIDATION_RULES = {
    "cyrillic": re.compile(r"[а-яіїєґ]", re.IGNORECASE),
    "non_ukr_letters": re.compile(r"[a-zA-Z]", re.IGNORECASE),
}

MESSAGES = {
    "uk": {
        "not_ukrainian": "Введено текст не українською мовою або в ньому немає жодного читабельного елемента.",
        "non_ukr_warning": "У тексті виявлено літери не українського алфавіту. Результат сумнівний."
    }
}

def validate_text(text) -> str:
    if not isinstance(text, str):
        raise ValueError("Введіть текст для аналізу.")
 
    cleaned_text = text.strip()
    if not cleaned_text:
        raise ValueError("Поле порожнє. Введіть текст українською мовою.")
 
    if len(cleaned_text) > max_chars:
        raise ValueError(
            f"Текст занадто довгий ({len(cleaned_text)} символів). Максимум — {max_chars}."
        )
 
    if not VALIDATION_RULES["cyrillic"].search(cleaned_text):
        raise ValueError(MESSAGES["uk"]["not_ukrainian"])
 
    return cleaned_text


def get_input_warnings(text: str) -> list[str]:
    warnings = []
    
    if VALIDATION_RULES["non_ukr_letters"].search(text):
        warnings.append(MESSAGES["uk"]["non_ukr_warning"])
    return warnings


def analyze_text(text: str) -> list[dict]:
    validated_text = validate_text(text)

    tokens = tokenize_text(validated_text)
    if not tokens:
        raise ValueError(MESSAGES["uk"]["not_ukrainian"])
    if len(tokens) > max_words:
        raise ValueError(f"Забагато слів ({len(tokens)}). Максимум — {max_words}.")

    return [analyzer.analyze_word(token) for token in tokens]


class UkrMorphologicalAnalyzer:
    def __init__(self):
        self.morph = pymorphy3.MorphAnalyzer(lang='uk')

        self.pos_tags = {            #словник тегів частин мови
            'NOUN': {'uk': 'іменник'},
            'ADJF': {'uk': 'прикметник'},
            'VERB': {'uk': 'дієслово'},
            'PRTF': {'uk': 'дієприкметник'},
            'GRND': {'uk': 'дієприслівник'},
            'NUMR': {'uk': 'числівник'},
            'ADVB': {'uk': 'прислівник'},
            'NPRO': {'uk': 'займенник'},
            'PRED': {'uk': 'предикатив(станівник)'}, #додано список
            'PRCL': {'uk': 'частка'},
            'PREP': {'uk': 'прийменник'},
            'CONJ': {'uk': 'сполучник'},
            'INTJ': {'uk': 'вигук'}, #додано список
        }

        self.custom_interjections = [
            "агов", "ой", "ах", "ох", "ех", "гей", "ура", "ай", "овва","еге", "ну",
            "мда", "ого", "тьху", "гаразд", "бац", "бух", "плюх", "оп",
        ]

        self.custom_predicatives = [
            "треба", "можна", "варто", "необхідно", "доцільно", 
            "можливо", "не можна",
            "весело", "сумно", "боляче", "холодно", "тепло", "гаряче", "соромно", 
            "лячно", "страшно", "нудно", "прикро", "радісно", "тяжко", "важко", 
            "легко", "приємно", "байдуже", "любо", "прикро", "смачно", "неприємно",
            "цікаво", "незручно", "зручно",
            "тихо", "темно", "світло", "хмарно", "сонячно", "вітряно", "душно", 
            "прохолодно", "пусто", "людно", "безлюдно", "чисто", "брудно", "затишно",
            "видно", "чутно", "поночі", "далеко", "близько"
        ]

        # Словник грамем (одиниць із значенням граматичних категорій)
        self.grammeme_tags = {
            'nomn': {'uk': 'називний'},  #відмінки
            'gent': {'uk': 'родовий'},
            'datv': {'uk': 'давальний'},
            'accs': {'uk': 'знахідний'},
            'ablt': {'uk': 'орудний'},
            'loct': {'uk': 'місцевий'},
            'voct': {'uk': 'кличний'},

            'masc': {'uk': 'чоловічий рід'},  #роди
            'femn': {'uk': 'жіночий рід'},
            'neut': {'uk': 'середній рід'},
             
            'sing': {'uk': 'однина'},  #число
            'plur': {'uk': 'множина'},

            '1per': {'uk': '1-ша особа'},  #особи
            '2per': {'uk': '2-га особа'},
            '3per': {'uk': '3-тя особа'},

            'pres': {'uk': 'теперішній час'},  #час
            'past': {'uk': 'минулий час'},
            'futr': {'uk': 'майбутній час'},

            'perf': {'uk': 'доконаний вид'},  #вид
            'impf': {'uk': 'недоконаний вид'},
        }

    def analyze_word(self, word: str) -> dict:
        clean_word = word.lower().strip()

        #Перевірка на вигук
        if clean_word in self.custom_interjections:
         return {
          "Слово": word,
          "Лема": clean_word,
          "Частина мови": self.pos_tags["INTJ"]["uk"],
          "Відмінок": "—",
          "Рід": "—",
          "Число": "—",
          "Особа": "—",
          "Час": "—",
          "Вид": "—",
        }

        #Перевірка на предикатив (станівник)
        if clean_word in self.custom_predicatives:
            parsed_temp = self.morph.parse(clean_word)[0]
            return {
                "Слово": word,
                "Лема": parsed_temp.normal_form,
                "Частина мови": self.pos_tags["PRED"]["uk"],
                "Відмінок": "—",
                "Рід": "—",
                "Число": "—",
                "Особа": "—",
                "Час": "—",
                "Вид": "—",
      }
        
        parsed = self.morph.parse(clean_word)[0]
        tag = parsed.tag

        # Перевірка на дієприкметник
        pos_key = tag.POS
        if pos_key == 'ADJF' and ('perf' in tag.grammemes or 'impf' in tag.grammemes):
            pos_key = 'PRTF'

        pos = self.pos_tags.get(pos_key, {}).get(
            'uk', str(pos_key) if pos_key else "Не визначено"
        )

        case_val = "—"
        gender_val = "—"
        number_val = "—"
        person_val = "—"
        tense_val = "—"
        aspect_val = "—"

        for g in tag.grammemes: #g - грамема
            if g in self.grammeme_tags:
                g_uk = self.grammeme_tags[g]['uk']
                
                if g in ['nomn', 'gent', 'datv', 'accs', 'ablt', 'loct', 'voct']:
                    case_val = g_uk
                elif g in ['masc', 'femn', 'neut']:
                    gender_val = g_uk
                elif g in ['sing', 'plur']:
                    number_val = g_uk
                elif g in ['1per', '2per', '3per']:
                    person_val = g_uk
                elif g in ['pres', 'past', 'futr']:
                    tense_val = g_uk
                elif g in ['perf', 'impf']:
                    aspect_val = g_uk

        if number_val == "—":   # У словнику pymorphy (uk) однина часто не позначена явно: якщо є рід, але немає 'plur', слово вважається одниною
            if 'plur' in tag.grammemes:
                number_val = self.grammeme_tags['plur']['uk']
            elif any(g in tag.grammemes for g in ['masc', 'femn', 'neut']):
                number_val = self.grammeme_tags['sing']['uk']
 
        return {
            "Слово": word,
            "Лема": parsed.normal_form,
            "Частина мови": pos,
            "Відмінок": case_val,
            "Рід": gender_val,
            "Число": number_val,
            "Особа": person_val,
            "Час": tense_val,
            "Вид": aspect_val,
        }
 
analyzer = UkrMorphologicalAnalyzer()
 
def tokenize_text(text: str) -> list[str]: 
    if not text or not text.strip():
        return []
    pattern = r"[а-яА-ЯіІїЇєЄґҐ]+(?:['’ʼ-][а-яА-ЯіІїЇєЄґҐ]+)*"
    return re.findall(pattern, text)

 
def check_text(text: str) -> list[dict]:
    if not text or not text.strip():
        raise ValueError("Введення початкового тексту є обов'язковим.")
 
    tokens = tokenize_text(text)
    if not tokens:
        raise ValueError("У введеному тексті не знайдено слів для аналізу.")
 
    return [analyzer.analyze_word(token) for token in tokens]

 
def lemmatize_text(text: str) -> str: #Повертає текст, де кожне слово замінене лемою
    return " ".join(r["Лема"] for r in analyze_text(text))
 
 
if __name__ == "__main__":
    sample = "Дощ періщив всі дні безперервно."   #в разі омонімії відмінкових форм можливі помилки
    for row in analyze_text(sample):
        print(row)
    print("Леми:", lemmatize_text(sample))

