from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from ruoli import ruoli
from indice import indice_ruoli_buoni, indice_ruoli_cattivi, indice_ruoli_lupi, indice_ruoli_soli, spiegazione_text, welcome_message, torneo_text
import re

async def start(update: Update, context):
    new_keyboard = [
            [InlineKeyboardButton("📒 Indice", callback_data='indice'), InlineKeyboardButton("📖 Guida", callback_data='guida')],
            [InlineKeyboardButton("🏆 Torneo", callback_data='torneo')]
    ]
    new_reply_markup = InlineKeyboardMarkup(new_keyboard)
    # Invia il messaggio di benvenuto
    await update.message.reply_text(text=welcome_message, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=new_reply_markup)


# Funzione per rimuovere emoji e caratteri speciali
def clean_text(text):
    # Rimuove tutto tranne lettere, numeri e spazi
    return re.sub(r'[^a-zA-Z0-9\s]', '', text).strip().lower()

async def handle_message(update: Update, context):
    # Ottieni il testo del messaggio dell'utente
    user_message = update.message.text.lower() if update.message.text else ''

    # Puliamo il messaggio dell'utente per rimuovere eventuali emoji o caratteri speciali
    clean_user_message = clean_text(user_message)

    found_role = None

    # Crea una lista di ruoli ordinata per lunghezza decrescente (per dare priorità ai ruoli più specifici)
    sorted_roles = sorted(ruoli.keys(), key=lambda x: len(clean_text(x)), reverse=True)

    # Cerca una corrispondenza esatta nel dizionario 'ruoli', pulendo anche i nomi dei ruoli
    for role in sorted_roles:
        clean_role = clean_text(role)  # Puliamo anche il nome del ruolo rimuovendo le emoji
        if clean_role == clean_user_message:  # Confrontiamo il ruolo "pulito" con il messaggio dell'utente
            found_role = role
            break

    # Se è stato trovato un ruolo, restituisci la spiegazione corrispondente
    if found_role:
        response_message = ruoli[found_role]
    else:
        # Risposta di default se il ruolo non è riconosciuto
        response_message = "Controlla di aver scritto correttamente il ruolo 🤔"

    # Invia la risposta
    await update.message.reply_text(response_message, parse_mode=ParseMode.MARKDOWN_V2)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Rispondi subito alla query per evitare timeout
    option_selected = query.data
    if option_selected == 'indice':
        # Crea i bottoni per Buoni, Cattivi, e Da soli
        keyboard = [
            [InlineKeyboardButton("😇 Buoni", callback_data='buoni'), InlineKeyboardButton("👿 Cattivi", callback_data='cattivi')],
            [InlineKeyboardButton("🤫 Solitari", callback_data='da_soli')],
            [InlineKeyboardButton("🏠 Home", callback_data='home')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Modifica il messaggio con i nuovi bottoni
        await query.edit_message_text(
            text="Scegli la fazione della quale fai parte:",
            reply_markup=reply_markup
        )

    elif option_selected == 'buoni':
        # Crea i bottoni per ogni ruolo buono, 3 per riga
        keyboard = [indice_ruoli_buoni[i:i + 3] for i in range(0, len(indice_ruoli_buoni), 3)]
        keyboard = [[InlineKeyboardButton(role, callback_data=role) for role in row] for row in keyboard]

        # Aggiungi il pulsante "Indietro" alla fine
        indietro_keyboard = [[InlineKeyboardButton("🔙 Indietro", callback_data='indietro'), InlineKeyboardButton("🏠 Home", callback_data='home')]]
        keyboard += indietro_keyboard

        # Crea il markup per la tastiera
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Modifica il messaggio con i nuovi bottoni
        await query.edit_message_text(text="Ecco la lista di tutti i ruoli buoni, o che lo sono solo inizialmente, seleziona quello di cui ti interessa avere maggiori informazioni:", reply_markup=reply_markup)

    elif option_selected == 'cattivi':
        # Crea i bottoni per "Lupi e Alleati" e "Altro"
        keyboard = [
            [InlineKeyboardButton("🐺 Lupi e Alleati", callback_data='lupi'), InlineKeyboardButton("💀 Altri cattivi", callback_data='altro')],
            [InlineKeyboardButton("🔙 Indietro", callback_data='indietro')],
            [InlineKeyboardButton("🏠 Home", callback_data='home')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Modifica il messaggio con i nuovi bottoni
        await query.edit_message_text(
            text="Esistono vari tipi di cattivi, lupi e i loro alleati oppure altre fazioni che sono comunque in conflitto tra loro, da quali cominciamo?",
            reply_markup=reply_markup
        )

    elif option_selected == 'lupi':
        # Crea i bottoni per i ruoli dei lupi, 3 per riga
        keyboard = [indice_ruoli_lupi[i:i + 3] for i in range(0, len(indice_ruoli_lupi), 3)]
        keyboard = [[InlineKeyboardButton(role, callback_data=role) for role in row] for row in keyboard]

        # Aggiungi il pulsante "Indietro" alla fine
        indietro_keyboard = [[InlineKeyboardButton("🔙 Indietro", callback_data='cattivi'), InlineKeyboardButton("🏠 Home", callback_data='home')]]
        keyboard += indietro_keyboard

        # Crea il markup per la tastiera
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Modifica il messaggio con i nuovi bottoni
        await query.edit_message_text(text="Ecco la lista di tutti i ruoli alleati con i Lupi o che potrebbero diventarlo, seleziona quello di cui vuoi ottenere maggiori informazioni:", reply_markup=reply_markup)

    elif option_selected == 'altro':
        # Crea i bottoni per gli altri cattivi, 3 per riga
        keyboard = [indice_ruoli_cattivi[i:i + 3] for i in range(0, len(indice_ruoli_cattivi), 3)]
        keyboard = [[InlineKeyboardButton(role, callback_data=role) for role in row] for row in keyboard]

        # Aggiungi il pulsante "Indietro" alla fine
        indietro_keyboard = [[InlineKeyboardButton("🔙 Indietro", callback_data='cattivi'), InlineKeyboardButton("🏠 Home", callback_data='home')]]
        keyboard += indietro_keyboard

        # Crea il markup per la tastiera
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Modifica il messaggio con i nuovi bottoni
        await query.edit_message_text(text="Ecco una lista di tutti i ruoli cattivi che sono in conflitto tra loro, alcuni di questi potrebbero avere un compagno, seleziona quello di cui vuoi ottenere maggiori informazioni:", reply_markup=reply_markup)

    elif option_selected == 'da_soli':
        # Crea i bottoni per i ruoli solitari, 3 per riga
        keyboard = [indice_ruoli_soli[i:i + 3] for i in range(0, len(indice_ruoli_soli), 3)]
        keyboard = [[InlineKeyboardButton(role, callback_data=role) for role in row] for row in keyboard]

        # Aggiungi il pulsante "Indietro" alla fine
        indietro_keyboard = [[InlineKeyboardButton("🔙 Indietro", callback_data='indietro'), InlineKeyboardButton("🏠 Home", callback_data='home')]]
        keyboard += indietro_keyboard

        # Crea il markup per la tastiera
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Modifica il messaggio con i nuovi bottoni
        await query.edit_message_text(text="Ecco una lista di tutti i ruoli che inizialmente giocano per se stessi e non appartengono a nessuna fazione, seleziona quello di cui vuoi ottenere maggiori informazioni:", reply_markup=reply_markup)

    elif option_selected in ruoli:
        # Recupera il messaggio del ruolo specifico selezionato
        role_message = ruoli.get(option_selected, "Ruolo non trovato. 🤔")

        # Invia un nuovo messaggio con il testo del ruolo selezionato
        await query.message.reply_text(role_message, parse_mode=ParseMode.MARKDOWN_V2)

        # Invia un messaggio separato con il pulsante per tornare all'indietro
        indietro_keyboard = [[InlineKeyboardButton("🔙 Indietro", callback_data='indietro'), InlineKeyboardButton("🏠 Home", callback_data='home')]]
        reply_markup = InlineKeyboardMarkup(indietro_keyboard)

        await query.message.reply_text(
            "Seleziona 'Indietro' per tornare al menu precedente.",
            reply_markup=reply_markup
        )

    elif option_selected == 'indietro':
        keyboard = [
            [InlineKeyboardButton("😇 Buoni", callback_data='buoni'), InlineKeyboardButton("👿 Cattivi", callback_data='cattivi')],
            [InlineKeyboardButton("🤫 Solitari", callback_data='da_soli')],
            [InlineKeyboardButton("🏠 Home", callback_data='home')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Modifica il messaggio con i nuovi bottoni
        await query.edit_message_text(
            text="Scegli la fazione della quale fai parte:",
            reply_markup=reply_markup
        )

    elif option_selected == 'guida':
        new_keyboard = [
            [InlineKeyboardButton("📒 Indice", callback_data='indice'), InlineKeyboardButton("🏆 Torneo", callback_data='torneo')],
            [InlineKeyboardButton("🏠 Home", callback_data='home')]
            ]
        reply_markup = InlineKeyboardMarkup(new_keyboard)

        # Modifica il messaggio con i nuovi bottoni
        await query.edit_message_text(
            text=spiegazione_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2
        )

    elif option_selected == 'torneo':
        new_keyboard = [
            [InlineKeyboardButton("📒 Indice", callback_data='indice'), InlineKeyboardButton("📖 Guida", callback_data='guida')],
            [InlineKeyboardButton("🏠 Home", callback_data='home')]
            ]
        reply_markup = InlineKeyboardMarkup(new_keyboard)

        # Modifica il messaggio con i nuovi bottoni
        await query.edit_message_text(
            text=torneo_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2
        )

    elif option_selected == 'home':
        new_keyboard = [
            [InlineKeyboardButton("📒 Indice", callback_data='indice'), InlineKeyboardButton("📖 Guida", callback_data='guida')],
            [InlineKeyboardButton("🏆 Torneo", callback_data='torneo')]
        ]
        new_reply_markup = InlineKeyboardMarkup(new_keyboard)
        await query.edit_message_text(
            text=welcome_message,
            reply_markup=new_reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2
        )
