from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


# Reply Keyboard для главного меню
main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Личный кабинет")],
    [KeyboardButton(text="Создать голосование")],
    [KeyboardButton(text="Проголосовать")]
], resize_keyboard=True)

# Inline клавиатура для создания голосования
create_vote_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Начать создание голосования", callback_data="create_vote_start")],
    [InlineKeyboardButton(text="Отмена", callback_data="create_vote_cancel")]
])

# Inline клавиатура для голосования
vote_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="На главную", callback_data="main_menu")],
    [InlineKeyboardButton(text="След. страница", callback_data="next_page")],
    [InlineKeyboardButton(text="Пред. страница", callback_data="prev_page")]
])

# Inline клавиатура для да/нет и другие действия
yes_no_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Да", callback_data="yes")],
    [InlineKeyboardButton(text="Нет", callback_data="no")],
    [InlineKeyboardButton(text="Отмена", callback_data="create_vote_cancel")],
    [InlineKeyboardButton(text="Сохранить", callback_data="create_vote_save")]
])

# Inline клавиатура для добавления пунктов и опций
point_option_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Добавить ещё один вариант ответа", callback_data="add_option")],
    [InlineKeyboardButton(text="Добавить ещё один пункт голосования", callback_data="add_point")],
    [InlineKeyboardButton(text="Завершить создание голосования", callback_data="finalize_vote")]
])

# Пример использования билдера для создания динамической Reply Keyboard
# async def dynamic_reply_keyboard(elements: list[str]) -> ReplyKeyboardMarkup:
#     keyboard = ReplyKeyboardBuilder()
#     for element in elements:
#         keyboard.add(KeyboardButton(text=element))
#     return keyboard.adjust(2).as_markup()


# main = ReplyKeyboardMarkup(keyboard=[
#     [KeyboardButton(text='создать голосование')],
#     [KeyboardButton(text='Личный кабинет')]
# ])
#
# inline_main = InlineKeyboardMarkup(inline_keyboard=[
#     [InlineKeyboardButton(text='создать голосование', callback_data='1')],
#     [InlineKeyboardButton(text='Личный кабинет', callback_data='2')]
# ])
#
#
# test_list = []
#
#
# async def reply_something():
#     keyboard = ReplyKeyboardBuilder()
#     for element in test_list:
#         keyboard.add(KeyboardButton(text=element))
#     return keyboard.adjust(2).as_markup()
