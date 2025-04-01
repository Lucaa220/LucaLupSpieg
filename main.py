import os
import sys
import asyncio
import logging
from aiohttp import web
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import nest_asyncio
from dotenv import load_dotenv
from command import start, handle_message, button

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Configurazione del logging (su stdout)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Leggi le variabili d'ambiente
token = os.getenv("TOKEN", "").strip()
# Costruisci il webhook URL in modo che punti al percorso /<token>
base_url = os.getenv("WEBHOOK_URL", "https://lucalupspieg.onrender.com").strip()
WEBHOOK_URL = f"{base_url}/{token}"
PORT = int(os.getenv("PORT", 8000))

# Funzione di health check per Uptime Robot
async def health_handler(request: web.Request) -> web.Response:
    return web.Response(text="Bot Tombola2_Bot attivo!")

# Funzione principale per il bot
async def main() -> None:
    logger.info("Configurazione del bot...")
    application = ApplicationBuilder().token(token).build()

    # Registrazione degli handler (prima i comandi, poi gli altri)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Impostazione del webhook...")
    await application.bot.set_webhook(url=WEBHOOK_URL)
    logger.info(f"Webhook impostato su {WEBHOOK_URL}")

    # Crea un'unica applicazione aiohttp che gestisce sia il webhook sia l'health check
    app = web.Application()
    # Aggiungi la route per l'health check
    app.router.add_get('/health', health_handler)
    app.router.add_get('/', health_handler)
    
    # Avvia il server in modalità webhook usando l'applicazione integrata
    await application.run_webhook(
         listen="0.0.0.0",
         port=PORT,
         url_path=token,
         webhook_url=WEBHOOK_URL,
         app=app
    )

if __name__ == "__main__":
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except Exception as e:
        logger.error(f"Si è verificato un errore: {e}")
    finally:
        loop.close()
