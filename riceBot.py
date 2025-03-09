import logging
from dataclasses import dataclass

from pydantic import BaseModel, field_validator
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

@dataclass
class Recipe:
    rice: float
    water: float

class RiceInput(BaseModel):
    rice: float

    @field_validator('rice')
    def check_rice_value(cls, v: float) -> float:
        valid_values = {0.5, 1, 1.5, 2, 2.5}
        if v not in valid_values:
            raise ValueError(f'Rice amount must be one of {valid_values}')
        return v

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            InlineKeyboardButton("0.5 стакана", callback_data='0.5'),
            InlineKeyboardButton("1 стакан", callback_data='1'),
        ],
        [
            InlineKeyboardButton("1.5 стакана", callback_data='1.5'),
            InlineKeyboardButton("2 стакана", callback_data='2'),
        ],
        [
            InlineKeyboardButton("2.5 стаканов", callback_data='2.5'),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text('Выберите количество риса:', reply_markup=reply_markup)
    else:
        await update.message.reply_text('Выберите количество риса:', reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    await query.answer()

    if query.data == 'back':
        await start(update, context)
        return

    try:
        rice_input = RiceInput(rice=float(query.data))
    except ValueError as e:
        await query.edit_message_text(text=f'Ошибка: {e}')
        return

    recipe = Recipe(rice=rice_input.rice, water=rice_input.rice * 1.5)
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data='back')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f'Для {recipe.rice} стакан(а) риса нужно {recipe.water} стакан(а) воды 🍚💧',
        reply_markup=reply_markup
    )

def main() -> None:
    application = ApplicationBuilder().token("token_api_tg").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()

if __name__ == '__main__':
    main()