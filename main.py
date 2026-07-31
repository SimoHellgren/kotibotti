import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logging.getLogger("httpx").setLevel(logging.WARNING)


class FreezerItem(BaseModel):
    name: str


class Freezer:
    def __init__(self, path: Path):
        self.path = path

        if not self.path.exists():
            self.path.write_text(json.dumps([]), encoding="utf-8")

    def ls(self):
        contents = json.load(self.path.open(encoding="utf-8"))

        items = [FreezerItem(name=x) for x in contents]

        return items


def get_freezer():
    return Freezer(path=Path("./data/freezer.json"))


async def list_freezer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    freezer = get_freezer()

    msg = "\n".join(x.name for x in freezer.ls())

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
