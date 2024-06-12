from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Reply Keyboard для главного меню
main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Личный кабинет")],
    [KeyboardButton(text="Создать голосование")],
    [KeyboardButton(text="Проголосовать")],
    [KeyboardButton(text="Изменить голосование")]
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
    [InlineKeyboardButton(text="Добавить ещё один пункт голосования", callback_data="add_point")],
    [InlineKeyboardButton(text="Завершить создание голосования", callback_data="finalize_vote")],
    [InlineKeyboardButton(text="Отмена", callback_data="create_vote_cancel")],
    [InlineKeyboardButton(text="Сохранить", callback_data="create_vote_save")]
])

# Клавиатура, отображающая кнопки "Отмена" и "Сохранить" при создании голосования
stop_vote_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Отмена", callback_data="create_vote_cancel")],
    [InlineKeyboardButton(text="Сохранить", callback_data="create_vote_save")]
])

# Инлайн-клавиатура для меню, потому что не знаю как с кодом связать реплай-клавиатуру
inline_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Личный кабинет", callback_data='lc')],
    [InlineKeyboardButton(text="Создать голосование", callback_data='create_vote_start')],
    [InlineKeyboardButton(text="Проголосовать", callback_data='vote')],
    [InlineKeyboardButton(text="Изменить голосование", callback_data='change')]
])

add_another_point_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Добавить ещё пункт", callback_data="add_point")],
    [InlineKeyboardButton(text="Завершить голосование", callback_data="finalize_vote")]
])


# Динамическая клавиатура, отображающая кнопки-голосования
# async def create_vote_keyboard(votes: list) -> InlineKeyboardMarkup:
#     keyboard = InlineKeyboardBuilder()
#     for vote in votes:
#         keyboard.add(InlineKeyboardButton(text=vote.topic, callback_data=f"{vote.id}. {vote.topic}"))
#     return keyboard.adjust(1).as_markup()


edit_vote_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Изменить тему", callback_data="edit_topic")],
    [InlineKeyboardButton(text="Изменить описание", callback_data="edit_description")],
    [InlineKeyboardButton(text="Изменить тип голосования", callback_data="edit_is_in_person")],
    [InlineKeyboardButton(text="Изменить закрытость голосования", callback_data="edit_is_closed")],
    [InlineKeyboardButton(text="Изменить видимость в процессе", callback_data=f"edit_is_visible_in_progress")],
    [InlineKeyboardButton(text="Добавить пункты", callback_data="edit_points")],
    [InlineKeyboardButton(text="Сделать голосование готовым", callback_data="edit_is_finished")],
    [InlineKeyboardButton(text="Выход", callback_data="create_vote_cancel")]
])


def create_keyboard_for_change(votes, page):
    votes_per_page = 5
    start_idx = page * votes_per_page
    end_idx = start_idx + votes_per_page
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{vote['topic']}"
                if 'start_time' in vote and 'end_time' in vote
                else vote['topic'],
                callback_data=f"edit_vote_{vote['id']}"
            )
        ]
        for vote in votes[start_idx:end_idx]
    ]
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"prev_page_{page - 1}"))
    if end_idx < len(votes):
        navigation_buttons.append(InlineKeyboardButton(text="➡️ Вперед", callback_data=f"next_page_{page + 1}"))
    if navigation_buttons:
        buttons.append(navigation_buttons)
    # Добавляем кнопку возврата в главное меню
    buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="to_inline_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_vote_keyboard(votes, page):
    votes_per_page = 5
    start_idx = page * votes_per_page
    end_idx = start_idx + votes_per_page
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{vote['topic']} ({vote['start_time'].strftime('%Y-%m-%d')} - {vote['end_time'].strftime('%Y-%m-%d')})",
                callback_data=f"vote_{vote['id']}"
            )
        ]
        for vote in votes[start_idx:end_idx]
    ]
    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"vote_prev_page_{page - 1}"))
    if end_idx < len(votes):
        navigation_buttons.append(InlineKeyboardButton(text="➡️ Вперед", callback_data=f"vote_next_page_{page + 1}"))
    if navigation_buttons:
        buttons.append(navigation_buttons)
    # Добавляем кнопку возврата в главное меню
    buttons.append([InlineKeyboardButton(text="🏠 Главное меню", callback_data="to_inline_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)