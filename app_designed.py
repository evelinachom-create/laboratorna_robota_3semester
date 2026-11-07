import gradio as gr
import pandas as pd

from main import max_chars, check_text, get_input_warnings

THEME = gr.themes.Soft(primary_hue="pink", secondary_hue="rose", font=[gr.themes.GoogleFont("Roboto"), "sans-serif"]).set(

    #аналізувати кнопка
    button_primary_background_fill="#ddd6fe",
    button_primary_background_fill_hover="#c4b5fd",
    button_primary_text_color="#3e1679",
    button_primary_border_color="#c4b5fd",

    #скинути кнопка
    button_secondary_background_fill="#f3f4f6",
    button_secondary_background_fill_hover="#e5e7eb",
    button_secondary_text_color="#374151",
    button_secondary_border_color="#d1d5db",
)

# Режими виводу
MODE_LEMMAS = "Леми"
MODE_FULL = "Проаналізовані леми"
MODE_COLORS = "Частини мови"
MODE_ALL = "Багатокомпонентний аналіз"

COLORS = {
    "іменник": "#e52929c9",
    "прикметник": "#2fd03cd7",
    "дієслово": "#2588f9d2",
    "дієприкметник": "#2d55b1d7",
    "дієприслівник": "#7f4df5d4",
    "числівник": "#f9bd82c9",
    "прислівник": "#ff7b00d1",
    "займенник": "#f145b8cf",
    "предикатив(станівник)": "#d8fcf6c3",
    "частка": "#6d6969bf",
    "прийменник": "#5E0050BC",
    "сполучник": "#ffee00e6",
    "вигук": "#f77e41c1",
}

FEATURES = ["Частина мови", "Відмінок", "Рід", "Число", "Особа", "Час", "Вид"]
COLUMNS = ["Слово", "Лема"] + FEATURES

CUSTOM_CSS = """
.custom-lemmas textarea {
    background-color: #E7DCFC !important;
}
.gradio-container {
    background-color: #F5A9CB !important;
}
"""

def build_table(results):
    rows = [{col: r[col] for col in COLUMNS} for r in results]
    return pd.DataFrame(rows, columns=COLUMNS)


def format_colored(results):
    colored = []
    for i, r in enumerate(results):
        if i > 0:
            colored.append((" ", None))
        colored.append((r["Слово"], r["Частина мови"]))
    return colored

def run_analysis(text, mode):
    try:
        results = check_text(text)
    except ValueError as e:
        gr.Warning(str(e))
        return reset_outputs()

    show_all = mode == MODE_ALL
    sentence = " ".join(r["Слово"] for r in results)
    lemmas_line = " ".join(r["Лема"] for r in results)

    # Таблицю видно лише у "проаналізовані леми" та "багатокомпонентний аналіз"
    show_table = show_all or mode == MODE_FULL

    return (
        sentence,
        gr.update(value=lemmas_line, visible=(show_all or mode == MODE_LEMMAS)),
        gr.update(value=build_table(results), visible=show_table),
        gr.update(value=format_colored(results), visible=(show_all or mode == MODE_COLORS)),
    )


def reset_outputs():
  return (
      gr.update(value="", visible=False),
      gr.update(value="", visible=False),
      gr.update(value=pd.DataFrame(columns=COLUMNS), visible=False),
      gr.update(value=[], visible=False),
  )


def reset_all():
  return ("", MODE_FULL) + reset_outputs()


with gr.Blocks(title="Морфологічний аналізатор") as demo:
    gr.Markdown("# Морфологічний аналізатор української мови")
    gr.Markdown("Застосунок для морфологічного аналізу тексту українською мовою з метою отримання лем та граматичних характеристик кожного слова.")

    with gr.Row():
        # Ліва колонка
        with gr.Column(scale=1, min_width=300):
            text_input = gr.Textbox(
                label="Вхідний текст",
                info=f"Введіть або вставте текст (до {max_chars} символів)",
                max_length=max_chars,
                placeholder="Наприклад: Ех! На вулиці дуже затишно.",
                lines=12,
            )
            mode = gr.Radio(
                choices=[MODE_LEMMAS, MODE_FULL, MODE_COLORS, MODE_ALL],
                value=MODE_FULL,
                label="Режим аналізу",
                info="Оберіть, наскільки деталізованою має бути відповідь",
            )
            with gr.Row():
                analyze_btn = gr.Button("Аналізувати", variant="primary")
                reset_btn = gr.Button("Скинути")

        # Права колонка
        with gr.Column(scale=2, min_width=300):
            sentence_out = gr.Textbox(label="Введене речення", interactive=False, visible=True)
            lemmas_out = gr.Textbox(label="Леми", interactive=False, visible=False, elem_classes=["custom-lemmas"])
            table_out = gr.Dataframe(
                value=pd.DataFrame(columns=COLUMNS),
                headers=COLUMNS,
                label="Граматичні характеристики",
                interactive=False,
                wrap=True,
                visible=False,
            )
            colored_out = gr.HighlightedText(   #підсвічування частин мови
                label="Частини мови",
                color_map=COLORS,
                show_legend=True,
                combine_adjacent=False,
                visible=False,
            )

    outputs = [sentence_out, lemmas_out, table_out, colored_out]

    analyze_btn.click(run_analysis, [text_input, mode], outputs)
    reset_btn.click(reset_all, None, [text_input, mode] + outputs)


if __name__ == "__main__":
    demo.launch(theme=THEME, css=CUSTOM_CSS, share=True)