from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='создать голосование')],
    [KeyboardButton(text='Личный кабинет')]
])

inline_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='создать голосование', callback_data='1')],
    [InlineKeyboardButton(text='Личный кабинет', callback_data='2')]
])


test_list = []


async def reply_something():
    keyboard = ReplyKeyboardBuilder()
    for element in test_list:
        keyboard.add(KeyboardButton(text=element))
    return keyboard.adjust(2).as_markup()