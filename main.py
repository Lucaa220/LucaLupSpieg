from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import logging
import nest_asyncio
import asyncio
from aiohttp import web
from command import start, handle_message, button

# Configurazione del logging (su stdout)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Pulizia del token
token = "7900232403:AAHV9uiPNAj0ZYQ_E2WxImQ2eSIYrHZogF8".strip()

# Funzione di health check per Uptime Robot
async def health_handler(request: web.Request) -> web.Response:
    return web.Response(text="Bot per la spiegazione di Lupus attivo!")

# Funzione per avviare il server web per l'health check
async def start_health_server() -> None:
    app = web.Application()
    # Aggiungi la route per il health check
    app.router.add_get('/health', health_handler)
    app.router.add_get('/', health_handler)  # Puoi usare anche la root
    runner = web.AppRunner(app)
    await runner.setup()
    # Imposta la porta in cui il server web ascolterà (ad es. 8000)
    site = web.TCPSite(runner, '0.0.0.0', 8000)
    await site.start()
    logger.info("Server health attivo sulla porta 8000")
    # Mantieni il server in esecuzione
    while True:
        await asyncio.sleep(3600)

# Funzione principale per il bot
async def main() -> None:
    logger.info("Configurazione del bot...")
    application = ApplicationBuilder().token(token).build()

    # Registrazione degli handler
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Avvio del bot in modalità polling...")

    # Avvia sia il bot in polling che il server web per l'health check in parallelo
    await asyncio.gather(
        application.run_polling(),  # Avvia il polling per ricevere aggiornamenti
        start_health_server()       # Avvia il server web per rispondere a /health e /
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

