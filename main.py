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
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://tuo-dominio.onrender.com/webhook").strip()
PORT = int(os.getenv("PORT", 8000))

# Funzione di health check per Uptime Robot
async def health_handler(request: web.Request) -> web.Response:
    return web.Response(text="Bot Tombola2_Bot attivo!")

# Server web per l'health check
async def start_health_server() -> None:
    app = web.Application()
    app.router.add_get('/health', health_handler)
    app.router.add_get('/', health_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    logger.info(f"Server health attivo sulla porta {PORT}")
    while True:
        await asyncio.sleep(3600)

# Funzione principale per il bot
async def main() -> None:
    logger.info("Configurazione del bot...")
    application = ApplicationBuilder().token(token).build()

    # Registrazione degli handler (ordini logici: prima i comandi, poi gli altri)
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Impostazione del webhook...")
    # Imposta il webhook: Telegram invierà gli aggiornamenti a WEBHOOK_URL
    await application.bot.set_webhook(url=WEBHOOK_URL)
    logger.info(f"Webhook impostato su {WEBHOOK_URL}")
    
    # Avvia in parallelo il webhook del bot e il server web per l'health check
    await asyncio.gather(
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=token,
            webhook_url=WEBHOOK_URL
        ),
        start_health_server()
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
