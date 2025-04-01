from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
import logging
import nest_asyncio
import asyncio
from command import start, handle_message, button

# Configurazione del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

token = "7900232403:AAHV9uiPNAj0ZYQ_E2WxImQ2eSIYrHZogF8"

async def main() -> None:
    logger.info("Configurazione del bot...")
    application = ApplicationBuilder().token(token).build()

    # Aggiunta degli handler
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("Avvio del bot...")
    await application.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    # Avvia il bot
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except Exception as e:
        logger.error(f"Si è verificato un errore: {e}")
    finally:
        loop.close()
