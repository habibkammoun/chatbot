import json
import re
import random_responses
from transformers import BertTokenizer, BertModel
import torch
from spellchecker import SpellChecker
from tkinter import *

# Créer une instance du correcteur d'orthographe
spell = SpellChecker()

# Charger le modèle pré-entraîné BERT et le tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Charger les données JSON
def load_json(file):
    with open(file) as bot_responses:
        print(f"Chargé '{file}' avec succès !")
        return json.load(bot_responses)

response_data = load_json("bot.json")

# Fonction pour effectuer la correction orthographique
def correct_spelling(text):
    # Séparer le texte en mots
    words = text.split()

    # Correction orthographique pour chaque mot
    corrected_words = [spell.correction(word) for word in words]

    # Supprimer les éléments vides de la liste
    corrected_words = [word for word in corrected_words if word is not None and word != ""]

    # Rejoindre les mots corrigés pour former le texte corrigé
    corrected_text = " ".join(corrected_words)
    return corrected_text

# Fonction pour obtenir les résultats similaires en utilisant BERT
def get_similar_responses(query, choices, threshold=0.8):
    query_tokens = tokenizer.tokenize(query)
    query_inputs = tokenizer.encode_plus(query, return_tensors='pt', padding=True, truncation=True)

    results = []

    for choice in choices:
        choice_tokens = tokenizer.tokenize(choice)
        choice_inputs = tokenizer.encode_plus(choice, return_tensors='pt', padding=True, truncation=True)

        with torch.no_grad():
            query_outputs = model(**query_inputs)
            choice_outputs = model(**choice_inputs)

        encoded_query = query_outputs.last_hidden_state[0][0]
        encoded_choice = choice_outputs.last_hidden_state[0][0]

        similarity_score = torch.cosine_similarity(encoded_query, encoded_choice, dim=0)

        if similarity_score.item() >= threshold:
            results.append(choice)

    return results

# Fonction pour obtenir la réponse
def get_response(input_string, response_data):
    corrected_input = correct_spelling(input_string)
    split_message = re.split(r'\s+|[,;?!.-]\s*', input_string.lower())

    score_list = []

    for response in response_data:
        response_score = 0
        required_score = 0
        required_words = response["required_words"]
        correct_responses = response["user_input"]

        if required_words:
            for word in split_message:
                results = get_similar_responses(input_string, correct_responses, threshold=0.8)

                if results:
                    phrase = " ".join(results)

                if word in required_words:
                    required_score += 1

        if required_score == len(required_words):
            for word in split_message:
                if word in correct_responses:
                    response_score += 1
        score_list.append(response_score)

    best_response = max(score_list)
    response_index = score_list.index(best_response)

    if input_string == "":
        return "Veuillez écrire quelque chose pour que nous puissions discuter :("

    if best_response != 0:
        if corrected_input != input_string:
            correct_response = response_data[response_index]["bot_response"]
            return f"Did you mean: '{corrected_input}'? {correct_response}"
        else:
            return response_data[response_index]["bot_response"]

    return random_responses.random_string()

context = {}  # Dictionary to store context

def get_response_for_gui(input_string):
    corrected_input = correct_spelling(input_string)

    response_generated = False
    bot_response = "I'm sorry, I don't have a suitable response for that."

    for response in response_data:
        if any(word in corrected_input for word in response["user_input"]):
            if all(word in corrected_input for word in response["required_words"]):
                response_generated = True
                bot_response = response["bot_response"]
                break

    if not response_generated:
        bot_response = "I'm sorry, I don't have a suitable response for that."

    return bot_response

class ChatApplication:
    def __init__(self):
        self.window = Tk()
        self._setup_main_window()
        self.bot = "mybot"

    def run(self):
        self.window.mainloop()

    def _setup_main_window(self):
        self.window.title("****chat with me!****")
        self.window.resizable(width=False, height=False)
        self.window.configure(width=470, height=550, bg=BG_COLOR)

        head_label = Label(self.window, bg=BG_COLOR, fg=TEXT_COLOR, text="WELCOME!", font=FONT_BOLD, pady=10)
        head_label.place(relwidth=1)

        line = Label(self.window, width=450, bg=BG_GRAY)
        line.place(relwidth=1, rely=0.07, relheight=0.012)

        self.text_Widget = Text(self.window, width=20, height=2, bg=BG_COLOR, fg=TEXT_COLOR, font=FONT, padx=5, pady=5)
        self.text_Widget.place(relheight=0.745, relwidth=1, rely=0.08)
        self.text_Widget.configure(cursor="arrow", state=DISABLED)

        scrollbar = Scrollbar(self.text_Widget)
        scrollbar.place(relheight=1, relx=0.974)
        scrollbar.configure(command=self.text_Widget.yview)

        BOTTOM_label = Label(self.window, bg=BG_GRAY, height=80)
        BOTTOM_label.place(relwidth=1, rely=0.825)

        self.msg_entry = Entry(BOTTOM_label, bg="#2C3E50", fg=TEXT_COLOR, font=FONT)
        self.msg_entry.place(relwidth=0.74, relheight=0.06, rely=0.008, relx=0.011)
        self.msg_entry.focus()
        self.msg_entry.bind("<Return>", self._on_enter_pressed)

        send_button = Button(BOTTOM_label, text="Send", font=FONT_BOLD, width=20, bg=BG_GRAY,
                             command=lambda: self._on_enter_pressed(None))
        send_button.place(relx=0.77, rely=0.008, relheight=0.06, relwidth=0.22)

    def _on_enter_pressed(self, event):
        msg = self.msg_entry.get()
        self._insert_message(msg, "you")

    def _insert_message(self, msg, sender):
        if not msg:
            return

        self.msg_entry.delete(0, END)
        msg1 = f"{sender}: {msg}\n\n"
        self.text_Widget.configure(state=NORMAL)
        self.text_Widget.insert(END, msg1)
        self.text_Widget.configure(state=DISABLED)
        msg2 = f"{self.bot}: {get_response_for_gui(msg)}\n\n"
        self.text_Widget.configure(state=NORMAL)
        self.text_Widget.insert(END, msg2)
        self.text_Widget.configure(state=DISABLED)
        self.text_Widget.see(END)

if __name__ == "__main__":
    app = ChatApplication()
    app.run()
