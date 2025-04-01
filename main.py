import os
import asyncio
import logging
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import nest_asyncio
from dotenv import load_dotenv
from command import start, handle_message, button

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
# Costruisci il webhook URL con endpoint fisso /webhook
base_url = os.getenv("WEBHOOK_URL", "https://lucalupspieg.onrender.com").strip()
WEBHOOK_URL = f"{base_url}/webhook"
PORT = int(os.getenv("PORT", 8000))

# Funzione di health check per Uptime Robot
async def health_handler(request: web.Request) -> web.Response:
    return web.Response(text="Bot lupus attivo!")

async def main() -> None:
    logger.info("Configurazione del bot...")
    application = ApplicationBuilder().token(token).build()

    # Registrazione degli handler: comandi, callback e messaggi
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Impostazione del webhook...")
    # Imposta il webhook: Telegram invierà gli aggiornamenti a WEBHOOK_URL
    await application.bot.set_webhook(url=WEBHOOK_URL)
    logger.info(f"Webhook impostato su {WEBHOOK_URL}")

    # Definizione di un handler personalizzato per il webhook (gestisce solo POST):
    async def handle_webhook(request: web.Request) -> web.Response:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return web.Response(text="OK")

    # Crea l'app aiohttp e aggiungi le route:
    app = web.Application()
    # Route POST per gestire gli aggiornamenti
    app.router.add_post("/webhook", handle_webhook)
    # Route GET per fornire una risposta informativa sull'endpoint webhook
    app.router.add_get("/webhook", lambda request: web.Response(text="Endpoint webhook: usa il metodo POST."))
    # Route per l'health check
    app.router.add_get('/health', health_handler)
    app.router.add_get('/', health_handler)

    # Inizializza e avvia il bot
    await application.initialize()
    await application.start()

    # Avvia il server aiohttp sulla porta specificata
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logger.info("Server web attivo sulla porta %d", PORT)

    # Mantieni il processo attivo (fino a interruzione)
    try:
        await asyncio.Event().wait()
    finally:
        logger.info("Terminazione dell'applicazione...")
        await application.stop()
        await application.shutdown()

if __name__ == "__main__":
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except Exception as e:
        logger.error(f"Si è verificato un errore: {e}")
    finally:
        loop.close()

