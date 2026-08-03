import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
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


async def list_freezer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    with connect(DB_PATH) as conn:
        items = crud.freezer.get_all(conn)

    msg = "\n".join(x.data["name"] for x in items)

    await query.answer()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
    )


async def add_freezer_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Lisää juttuja, yksi per rivi"
    )


async def freezer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("Sisälmys", callback_data="list_freezer"),
            InlineKeyboardButton("Lisää", callback_data="add_freezer_item"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Pakastin", reply_markup=reply_markup)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("pakastin", freezer))
app.add_handler(
    CallbackQueryHandler(list_freezer, pattern="^list_freezer$")
)  # TODO: use constants for this, now magic "number"
app.add_handler(CallbackQueryHandler(add_freezer_item, pattern="^add_freezer_item$"))

app.run_polling()
