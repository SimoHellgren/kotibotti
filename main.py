import logging
import os
import re
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

    msg = "\n".join(x.data.name for x in sorted(items, key=lambda x: x.data.name))

    await query.answer()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
    )


async def add_freezer_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    await query.answer()
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Lisää juttuja, yksi per rivi"
    )

    return ConversationState.freezer_input


async def handle_freezer_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    items = update.message.text.split("\n")
    non_empty = list(filter(None, items))
    logger.info(f"Adding {non_empty} to freezer")

    added = []
    with connect(DB_PATH) as conn:
        for item in non_empty:
            logger.info(f"Adding {item} to freezer")
            result = crud.freezer.add(conn, {"name": item})
            added.append(result.data.name)

    await update.message.reply_text(f"Added: {added}")

    return ConversationHandler.END


async def edit_freezer_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    with connect(DB_PATH) as conn:
        items = sorted(crud.freezer.get_all(conn), key=lambda x: x.data.name)

    item_keys = [
        [
            InlineKeyboardButton(item.data.name, callback_data=f"edit_item:{item.id}"),
            InlineKeyboardButton("🗑️", callback_data=f"delete_item:{item.id}"),
        ]
        for item in items
    ]

    keyboard = [
        *item_keys,
        [InlineKeyboardButton("Sulje", callback_data="finish_editing")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.answer()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Muokkaa/poista:",
        reply_markup=reply_markup,
    )


async def edit_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    await query.answer(text="Tämä ei vielä tee mitään :3")


async def delete_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    _, item_id = query.data.split(":")

    # remove from db
    with connect(DB_PATH) as conn:
        db_item = crud.freezer.delete(conn, item_id)

        logger.info(f"Deleted item {db_item.id}")

        # TODO: should probably handle the case where the item doesn't exist

    # filter out the item from the reply keyboard.
    # some funky unpacking since the rows of the keyboard
    # contain a varying number of buttons
    old_kb = query.message.reply_markup.inline_keyboard
    new_kb = [(*a, b) for *a, b in old_kb if b.callback_data != query.data]

    await query.edit_message_reply_markup(InlineKeyboardMarkup(new_kb))

    await query.answer(text=f"Deleted '{db_item.data.name}'")


async def finish_editing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    await query.edit_message_reply_markup(None)
    await query.edit_message_text("Muokkaukset tehty!")


async def freezer_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("Sisälmys", callback_data="list_freezer")],
        [
            InlineKeyboardButton("Lisää", callback_data="add_freezer_item"),
            InlineKeyboardButton("Muokkaa", callback_data="edit_freezer_item"),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Pakastin", reply_markup=reply_markup)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the operation.", user.first_name)
    await update.message.reply_text("Peruutus")

    return ConversationHandler.END


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("pakastin", freezer_menu))
app.add_handler(
    CallbackQueryHandler(list_freezer, pattern="^list_freezer$")
)  # TODO: use constants for this, now magic "number"
app.add_handler(CallbackQueryHandler(edit_freezer_menu, pattern="^edit_freezer_item$"))
app.add_handler(CallbackQueryHandler(edit_item, pattern=re.compile(r"^edit_item:\d+$")))
app.add_handler(
    CallbackQueryHandler(delete_item, pattern=re.compile(r"^delete_item:\d+$"))
)
app.add_handler(CallbackQueryHandler(finish_editing, pattern="^finish_editing$"))
app.add_handler(
    ConversationHandler(
        entry_points=[
            CallbackQueryHandler(add_freezer_items, pattern="^add_freezer_item$")
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
