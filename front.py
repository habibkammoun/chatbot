import tkinter as tk
import json
import random

# Charger les réponses depuis le fichier JSON
with open('bot.json', 'r', encoding='utf-8') as file:
    responses = json.load(file)

# Fonction pour obtenir la réponse du chatbot
def get_response(user_input):
    for response in responses:
        if any(word in user_input.lower() for word in response['user_input']):
            return response['bot_response']
    return "Je ne comprends pas. Pouvez-vous reformuler votre question ?"

# Fonction pour gérer l'interaction avec le chatbot
def send_message():
    user_input = entry.get()
    if user_input:
        chat_log.config(state=tk.NORMAL)
        chat_log.insert(tk.END, "Vous : " + user_input + "\n", "user")
        chat_log.insert(tk.END, "Chatbot : " + get_response(user_input) + "\n", "bot")
        chat_log.config(state=tk.DISABLED)
        entry.delete(0, tk.END)

# Créer la fenêtre de l'interface graphique
root = tk.Tk()
root.title("Chatbot")

# Créer une zone de texte pour afficher la conversation
chat_log = tk.Text(root, height=20, width=50)
chat_log.config(state=tk.DISABLED)
chat_log.tag_configure("user", justify='right', foreground='blue')
chat_log.tag_configure("bot", justify='left', foreground='green')
chat_log.pack()

# Créer une zone de saisie pour l'utilisateur
entry = tk.Entry(root, width=50)
entry.bind("<Return>", lambda event=None: send_message())
entry.pack()

# Créer un bouton pour envoyer le message
send_button = tk.Button(root, text="Envoyer", command=send_message)
send_button.pack()

root.mainloop()
