import os
import asyncio
import logging
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Configurazione del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Leggi le variabili d'ambiente
token = os.getenv("TOKEN", "").strip()
base_url = os.getenv("WEBHOOK_URL", "https://lucalupspieg.onrender.com").strip()
WEBHOOK_URL = f"{base_url}/webhook"
PORT = int(os.getenv("PORT", 8000))

# Importa i moduli per i comandi (assicurati che i file siano corretti)
from command import start, handle_message, button

# Handler per il check di salute (health check)
async def health_handler(request: web.Request) -> web.Response:
    return web.Response(text="Bot lupus attivo!")

# Handler per il webhook che processa gli update di Telegram
async def webhook_handler(request: web.Request) -> web.Response:
    try:
        data = await request.json()
    except Exception as e:
        logger.error("Errore nella lettura del JSON: %s", e)
        return web.Response(text="Errore nei dati inviati", status=400)
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return web.Response(text="OK")

# Setup dell'applicazione web con aiohttp
async def setup_webapp() -> web.Application:
    app = web.Application()
    app.router.add_post("/webhook", webhook_handler)
    app.router.add_get("/webhook", lambda request: web.Response(text="Endpoint webhook: usa il metodo POST."))
    app.router.add_get("/health", health_handler)
    app.router.add_get("/", health_handler)
    return app

# Funzione principale
async def main() -> None:
    global application

    logger.info("Configurazione del bot...")
    application = ApplicationBuilder().token(token).build()

    # Registrazione degli handler per i comandi e i messaggi
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Imposta il webhook: Telegram invierà gli aggiornamenti a WEBHOOK_URL
    await application.bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook impostato su {WEBHOOK_URL}")

    # Inizializza e avvia il bot
    await application.initialize()
    await application.start()

    # Configura e avvia il server web per gestire il webhook
    app = await setup_webapp()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logger.info("Server web attivo sulla porta %d", PORT)

    # Mantieni il processo attivo 24/7 (ciclo continuo)
    logger.info("Bot avviato, in attesa di aggiornamenti...")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error("Si è verificato un errore: %s", e)


