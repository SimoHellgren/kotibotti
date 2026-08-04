import logging
import os
from enum import Enum, auto
from pathlib import Path

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import crud
from db import connect

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = Path(os.getenv("", "./db.sqlite"))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class ConversationState(Enum):
    freezer_input = auto()


async def list_freezer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    with connect(DB_PATH) as conn:
        items = crud.freezer.get_all(conn)

    msg = "\n".join(x.data.name for x in items)

    await query.answer()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
    )


async def add_freezer_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    await query.answer()
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Lisää juttuja, yksi per rivi"
    )

    return ConversationState.freezer_input


async def handle_freezer_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items = update.message.text.split("\n")
    logger.info(f"Adding {items} to freezer")

    await update.message.reply_text(f"Added: {items}")

    with connect(DB_PATH) as conn:
        for item in filter(None, items):
            crud.freezer.create(conn, {"name": item})

    return ConversationHandler.END


async def freezer_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Sisälmys", callback_data="list_freezer"),
            InlineKeyboardButton("Lisää", callback_data="add_freezer_item"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Pakastin", reply_markup=reply_markup)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text("Peruutus")

    return ConversationHandler.END


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("pakastin", freezer_menu))
app.add_handler(
    CallbackQueryHandler(list_freezer, pattern="^list_freezer$")
)  # TODO: use constants for this, now magic "number"

app.add_handler(
    ConversationHandler(
        entry_points=[
            CallbackQueryHandler(add_freezer_item, pattern="^add_freezer_item$")
        ],
        states={
            ConversationState.freezer_input: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_freezer_input)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
)
app.run_polling()
