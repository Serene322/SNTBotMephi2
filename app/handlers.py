from datetime import datetime
from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
import app.database.requests as rq

router = Router()


class Reg(StatesGroup):
    email = State()
    password = State()


class CreateVote(StatesGroup):
    topic = State()
    description = State()
    start_time = State()
    end_time = State()
    is_in_person = State()
    is_closed = State()
    is_visible_in_progress = State()
    add_point = State()
    add_option = State()
    finalize = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Reg.email)
    await message.answer('Здравствуйте! Для начала работы вам необходимо авторизоваться.')
    await message.answer('Укажите ваш email')


@router.message(Reg.email)
async def reg_first_step(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await state.set_state(Reg.password)
    await message.answer('Введите пароль')


@router.message(Reg.password)
async def reg_check_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    email = data['email']
    password = data['password']
    answer = await rq.registration(email, password)
    if answer:
        await rq.set_telegram_id(email, message.from_user.id)
        await message.answer('Авторизация прошла успешно', reply_markup=kb.main_menu)
        await state.clear()
    else:
        await message.answer('Ошибка во время авторизации. Попробуйте снова.')
        await state.set_state(Reg.email)
        await message.answer('Укажите ваш email')


async def clear_and_prompt(state, message, prompt_text, reply_markup):
    # Проверяем, является ли сообщение CallbackQuery
    if isinstance(message, types.CallbackQuery):
        # Получаем идентификатор чата и сообщения
        chat_id = message.message.chat.id
        message_id = message.message.message_id
        # Удаляем предыдущее сообщение с меню
        await message.message.bot.delete_message(chat_id, message_id)
        # Отправляем новое сообщение с меню
        await message.message.answer(prompt_text, reply_markup=reply_markup)
    # Проверяем, является ли сообщение Message
    elif isinstance(message, types.Message):
        # Удаляем предыдущее сообщение с меню
        await message.delete_reply_markup()
        # Отправляем новое сообщение с меню
        await message.answer(prompt_text, reply_markup=reply_markup)


@router.message(F.text == "Создать голосование")
@router.callback_query(lambda c: c.data == "create_vote_start")
async def create_vote_start_handler(event, state: FSMContext):
    await clear_and_prompt(state, event.message if isinstance(event, CallbackQuery) else event,
                           'Введите тему голосования:', kb.stop_vote_keyboard)
    await state.set_state(CreateVote.topic)
    await state.update_data(description=None, is_in_person=0, is_closed=0, is_visible_in_progress=0, start_time=None,
                            end_time=None, is_finished=False, points=[])


@router.callback_query(lambda c: c.data == "create_vote_save")
async def create_vote_save(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await rq.save_incomplete_vote(data, callback_query.from_user.id)
    # Удаляем предыдущее сообщение с меню
    await callback_query.message.delete()
    await state.clear()
    await callback_query.message.answer("Черновик сохранен.", reply_markup=kb.inline_main_menu)


@router.callback_query(lambda c: c.data == "create_vote_cancel")
async def cancel_create_vote(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer('')
    # Удаляем предыдущее сообщение с меню
    await callback_query.message.delete()
    await state.clear()
    await callback_query.message.answer("Создание голосования отменено.", reply_markup=kb.inline_main_menu)


@router.message(CreateVote.topic)
async def set_vote_topic(message: Message, state: FSMContext):
    data = await state.get_data()
    is_editing = data.get('is_editing', False)

    if is_editing:
        await rq.update_vote_topic(data.get('edit_vote_id'), message.text)
        await state.clear()
        await message.answer("Тема голосования успешно обновлена.", reply_markup=kb.inline_main_menu)
    else:
        await state.update_data(topic=message.text)
        await state.set_state(CreateVote.description)
        await message.answer("Введите описание голосования:", reply_markup=kb.stop_vote_keyboard)


@router.message(CreateVote.description)
async def set_vote_description(message: Message, state: FSMContext):
    data = await state.get_data()
    is_editing = data.get('is_editing', False)

    if is_editing:
        await rq.update_vote_description(data.get('edit_vote_id'), message.text)
        await state.clear()
        await message.answer("Описание голосования успешно обновлено.", reply_markup=kb.inline_main_menu)
    else:
        await state.update_data(description=message.text)
        await state.set_state(CreateVote.start_time)
        await message.answer("Введите дату начала голосования (ГГГГ-ММ-ДД):", reply_markup=kb.stop_vote_keyboard)


@router.message(CreateVote.start_time)
async def set_start_time(message: Message, state: FSMContext):
    date_text = message.text
    try:
        start_time = datetime.strptime(date_text, '%Y-%m-%d').replace(hour=0, minute=0)
    except ValueError:
        await message.answer("Неправильный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД.")
        return
    await state.update_data(start_time=start_time)
    await state.set_state(CreateVote.end_time)
    await message.answer("Введите дату окончания голосования (в формате ГГГГ-ММ-ДД):",
                         reply_markup=kb.stop_vote_keyboard)


@router.message(CreateVote.end_time)
async def set_end_time(message: Message, state: FSMContext):
    date_text = message.text
    try:
        end_time = datetime.strptime(date_text, '%Y-%m-%d').replace(hour=23, minute=59)
    except ValueError:
        await message.answer("Неправильный формат даты. Пожалуйста, введите дату в формате ГГГГ-ММ-ДД.")
        return
    await state.update_data(end_time=end_time)
    await state.set_state(CreateVote.is_in_person)
    await message.answer("Голосование очное? (да/нет):", reply_markup=kb.yes_no_keyboard)


@router.callback_query(lambda c: c.data in ["yes", "no"])
async def handle_yes_no(callback_query: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    value = callback_query.data == "yes"
    data = await state.get_data()

    if current_state == CreateVote.is_in_person:
        current_value = data.get('is_in_person')
        # Если значение в БД отличается от введённого пользователем, то мы делаем апдейт
        if current_value != value:
            await state.update_data(is_in_person=value)
        await state.set_state(CreateVote.is_closed)
        await callback_query.message.edit_text("Голосование закрытое? (да/нет):", reply_markup=kb.yes_no_keyboard)
    elif current_state == CreateVote.is_closed:
        current_value = data.get('is_closed')
        # Если значение в БД отличается от введённого пользователем, то мы делаем апдейт
        if current_value != value:
            await state.update_data(is_closed=value)
        await state.set_state(CreateVote.is_visible_in_progress)
        await callback_query.message.edit_text("Информация видна в процессе? (да/нет):",
                                               reply_markup=kb.yes_no_keyboard)
    elif current_state == CreateVote.is_visible_in_progress:
        current_value = data.get('is_visible_in_progress')
        # Если значение в БД отличается от введённого пользователем, то мы делаем апдейт
        if current_value != value:
            await state.update_data(is_visible_in_progress=value)
        await state.set_state(CreateVote.add_point)
        await callback_query.message.edit_text("Введите первый пункт голосования:", reply_markup=kb.stop_vote_keyboard)


@router.message(CreateVote.add_point)
async def add_vote_point(message: Message, state: FSMContext):
    data = await state.get_data()
    vote_id = data.get('vote_id')
    if not vote_id:
        vote_id = await rq.create_vote(data, message.from_user.id)
        await state.update_data(vote_id=vote_id)

    point_body = message.text

    # Проверяем, существует ли уже пункт с таким текстом в базе данных
    existing_points = data.get('points', [])
    existing_point_bodies = [point['body'] for point in existing_points]
    if point_body in existing_point_bodies:
        await message.answer("Этот пункт уже существует.")
        return

    # Если пункта нет в базе данных, добавляем его
    point_id = await rq.add_point(vote_id, point_body)

    # Добавляем новый пункт в список points в состоянии и инициализируем пустой список options
    points = data.get('points', [])
    points.append({'point_id': point_id, 'body': point_body, 'options': []})
    await state.update_data(points=points)

    await state.set_state(CreateVote.add_option)
    await message.answer("Выберите действие:", reply_markup=kb.point_option_keyboard)


@router.message(CreateVote.add_option)
async def add_vote_option(message: Message, state: FSMContext):
    pass


@router.callback_query(lambda c: c.data == "add_option")
async def add_another_option(callback_query: CallbackQuery):
    await callback_query.message.edit_text("Введите следующий вариант ответа:", reply_markup=kb.point_option_keyboard)


@router.callback_query(lambda c: c.data == "add_point")
async def add_another_point(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(CreateVote.add_point)
    await callback_query.message.edit_text("Введите следующий пункт голосования:", reply_markup=kb.stop_vote_keyboard)


@router.callback_query(lambda c: c.data == "finalize_vote")
async def finalize_vote(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data['is_finished'] = True
    await rq.save_vote(data, callback_query.from_user.id)
    await state.clear()
    await callback_query.message.edit_text("Голосование завершено и сохранено.", reply_markup=kb.inline_main_menu)


# Обработка кнопки "Проголосовать"
@router.message(F.text == "Изменить голосование")
@router.callback_query(lambda c: c.data == "change")
async def change_vote_start(event):
    votes = await rq.get_unfinished_votes(event.from_user.id if isinstance(event, Message) else event.from_user.id)
    if not votes:
        await (event.answer if isinstance(event, CallbackQuery) else event.message.answer)(
            'Нет доступных голосований для изменения.')
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=vote['topic'], callback_data=f"edit_vote_{vote['id']}")] for vote in votes
    ])
    await (event.message.edit_text if isinstance(event, CallbackQuery) else event.answer)(
        'Выберите голосование для изменения:', reply_markup=keyboard)


@router.message(lambda message: message.text == "vo")
async def vote_start(message: Message):
    await message.answer('Выберите голосование из списка:', reply_markup=kb.vote_menu)


# Кнопка изменить для ИНЛАЙН-клавиатуры
@router.callback_query(lambda c: c.data == "change")
async def inline_change_vote_start(callback_query: CallbackQuery):
    votes = await rq.get_unfinished_votes(callback_query.from_user.id)
    if not votes:
        await callback_query.answer('Нет доступных голосований для изменения.')
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=vote['topic'], callback_data=f"edit_vote_{vote['id']}")] for vote in votes
    ] )
    await callback_query.message.edit_text('Выберите голосование для изменения:', reply_markup=keyboard)


# Обработчик для выбора голосования и отображения его данных
# Добавим функцию для обработки редактирования голосования
@router.callback_query(lambda c: c.data.startswith("edit_vote_"))
async def edit_vote(callback_query: CallbackQuery, state: FSMContext):
    vote_id = int(callback_query.data.split("_")[2])
    vote_data = await rq.get_vote_details(vote_id)

    if not vote_data:
        await callback_query.message.edit_text("Голосование не найдено.")
        return

    # Сохраняем информацию о том, что пользователь редактирует голосование
    await state.update_data(is_editing=True, edit_vote_id=vote_id, vote_data=vote_data)

    details = f"Тема: {vote_data['topic']}\n" \
              f"Описание: {vote_data['description']}\n" \
              f"Дата начала: {vote_data['start_time']}\n" \
              f"Дата окончания: {vote_data['end_time']}\n" \
              f"Очное голосование: {'Да' if vote_data['is_in_person'] else 'Нет'}\n" \
              f"Закрытое голосование: {'Да' if vote_data['is_closed'] else 'Нет'}\n" \
              f"Видимость в процессе: {'Да' if vote_data['is_visible_in_progress'] else 'Нет'}\n"

    await callback_query.message.edit_text(details, reply_markup=kb.edit_vote_keyboard)


# Обработчики для изменения  данных голосования
@router.callback_query(lambda c: c.data == "edit_topic")
async def edit_topic_start(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(CreateVote.topic)
    await callback_query.message.edit_text("Введите новую тему голосования:", reply_markup=kb.stop_vote_keyboard)


@router.callback_query(lambda c: c.data == "edit_description")
async def edit_description_start(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(CreateVote.description)
    await callback_query.message.edit_text("Введите новое описание голосования:", reply_markup=kb.stop_vote_keyboard)
    # FROM HERE


@router.callback_query(lambda c: c.data.startswith("edit_is_in_person_"))
async def edit_is_in_person(callback_query: CallbackQuery, state: FSMContext):
    vote_id = int(callback_query.data.split("_")[-1])
    await state.update_data(edit_vote_id=vote_id)
    await edit_is_in_person_start(callback_query, state)


@router.callback_query(lambda c: c.data == "edit_is_in_person")
async def edit_is_in_person_start(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    vote_id = data.get('edit_vote_id')
    vote_data = await rq.get_vote_details(vote_id)

    if not vote_data:
        await callback_query.message.edit_text("Голосование не найдено.")
        return

    current_value = vote_data.get('is_in_person')
    if current_value is None:
        await callback_query.message.edit_text("Информация о голосовании неполная.")
        return

    new_value = not current_value

    # Update the value in the database
    await rq.update_vote_is_in_person(vote_id, new_value)

    # Inform the user about the change
    message_text = "Тип голосования изменен на очное." if new_value else "Тип голосования изменен на неочное."
    await callback_query.message.edit_text(message_text)
    await callback_query.message.edit_reply_markup(reply_markup=kb.inline_main_menu)

    # Clear the state data related to the edit
    await state.clear()


@router.callback_query(lambda c: c.data.startswith("edit_is_closed_"))
async def edit_is_closed(callback_query: CallbackQuery, state: FSMContext):
    vote_id = int(callback_query.data.split("_")[-1])
    await state.update_data(edit_vote_id=vote_id)
    await edit_is_closed_start(callback_query, state)


@router.callback_query(lambda c: c.data == "edit_is_closed")
async def edit_is_closed_start(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    vote_id = data.get('edit_vote_id')
    vote_data = await rq.get_vote_details(vote_id)

    if not vote_data:
        await callback_query.message.edit_text("Голосование не найдено.")
        return

    current_value = vote_data.get('is_closed')
    if current_value is None:
        await callback_query.message.edit_text("Информация о голосовании неполная.")
        return

    new_value = not current_value

    # Update the value in the database
    await rq.update_vote_is_closed(vote_id, new_value)

    # Inform the user about the change
    message_text = "Тип голосования изменен на закрытое." if new_value else "Тип голосования изменен на открытое."
    await callback_query.message.edit_text(message_text)
    await callback_query.message.edit_reply_markup(reply_markup=kb.inline_main_menu)

    # Clear the state data related to the edit
    await state.clear()


@router.callback_query(lambda c: c.data.startswith("edit_is_visible_in_progress_"))
async def edit_is_visible_in_progress(callback_query: CallbackQuery, state: FSMContext):
    vote_id = int(callback_query.data.split("_")[-1])
    await state.update_data(edit_vote_id=vote_id)
    await edit_is_visible_in_progress_start(callback_query, state)


@router.callback_query(lambda c: c.data == "edit_is_visible_in_progress")
async def edit_is_visible_in_progress_start(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    vote_id = data.get('edit_vote_id')
    vote_data = await rq.get_vote_details(vote_id)

    if not vote_data:
        await callback_query.message.edit_text("Голосование не найдено.")
        return

    current_value = vote_data.get('is_visible_in_progress')
    if current_value is None:
        await callback_query.message.edit_text("Информация о голосовании неполная.")
        return

    new_value = not current_value

    # Update the value in the database
    await rq.update_vote_visibility(vote_id, new_value)

    # Inform the user about the change
    message_text = "Голосование стало видимым в процессе." if new_value else "Голосование скрыто в процессе."
    await callback_query.message.edit_text(message_text)
    await callback_query.message.edit_reply_markup(reply_markup=kb.inline_main_menu)

    # Clear the state data related to the edit
    await state.clear()

@router.callback_query(lambda c: c.data.startswith("edit_is_finished_"))
async def edit_is_finished(callback_query: CallbackQuery, state: FSMContext):
    vote_id = int(callback_query.data.split("_")[-1])
    await state.update_data(edit_vote_id=vote_id)
    await edit_is_finished_start(callback_query, state)


@router.callback_query(lambda c: c.data == "edit_is_finished")
async def edit_is_finished_start(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    vote_id = data.get('edit_vote_id')
    vote_data = await rq.get_vote_details(vote_id)

    if not vote_data:
        await callback_query.message.edit_text("Голосование не найдено.")
        return

    current_value = vote_data.get('is_finished')
    if current_value is None:
        await callback_query.message.edit_text("Информация о голосовании неполная.")
        return

    new_value = not current_value

    # Update the value in the database
    await rq.update_vote_is_finished(vote_id, new_value)

    # Inform the user about the change
    message_text = "Голосование завершено." if new_value else "Голосование возобновлено."
    await callback_query.message.edit_text(message_text)
    await callback_query.message.edit_reply_markup(reply_markup=kb.inline_main_menu)

    # Clear the state data related to the edit
    await state.clear()


@router.callback_query(lambda c: c.data == "to_inline_main_menu")
async def to_inline_main_menu(callback_query: CallbackQuery, state: FSMContext):
    await edit_vote(callback_query, state)  # Запуск хэндлера edit_vote с текущими аргументами


# Обработка кнопки "Проголосовать"
@router.callback_query(lambda c: c.data == 'vote')
async def show_votes(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    votes = await rq.get_active_votes(user_id)

    if not votes:
        new_text = 'Нет доступных голосований.'
        if callback_query.message.text != new_text:
            await callback_query.message.edit_text(new_text, reply_markup=kb.inline_main_menu)
        else:
            await callback_query.answer('Нет доступных голосований.', show_alert=True)
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=vote['topic'], callback_data=f"vote_{vote['id']}")] for vote in votes
    ] + [
        [InlineKeyboardButton(text="Выход", callback_data='to_inline_menu')]
    ])
    new_text = 'Выберите голосование из списка:'
    if callback_query.message.text != new_text or callback_query.message.reply_markup != keyboard:
        await callback_query.message.edit_text(new_text, reply_markup=keyboard)

# Обработка выбора голосования
@router.callback_query(lambda c: c.data.startswith('vote_'))
async def show_vote_details(callback_query: CallbackQuery, state: FSMContext):
    vote_id = int(callback_query.data.split('_')[1])
    vote_data, points = await rq.get_vote_details_with_points(vote_id)

    if not vote_data:
        await callback_query.message.edit_text('Голосование не найдено.', reply_markup=kb.inline_main_menu)
        return

    vote = vote_data[0]
    points = [point[0] for point in points]

    details = (f"Тема: {vote.topic}\n"
               f"Описание: {vote.description}\n"
               f"Дата начала: {vote.start_time}\n"
               f"Дата окончания: {vote.end_time}\n"
               f"Очное голосование: {'Да' if vote.is_in_person else 'Нет'}\n"
               f"Закрытое голосование: {'Да' if vote.is_closed else 'Нет'}\n"
               f"Видимость в процессе: {'Да' if vote.is_visible_in_progress else 'Нет'}\n")

    # Сохраняем данные о голосовании и пунктах в состояние
    await state.update_data(vote=vote, points=points)

    # Выводим сообщение с деталями голосования и кнопкой "Продолжить"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Продолжить", callback_data='next_point')]
    ])
    await callback_query.message.edit_text(details, reply_markup=keyboard)


# Функция для отображения деталей голосования по его идентификатору
async def show_vote_details_by_id(callback_query: CallbackQuery, vote_id: int, state: FSMContext):
    vote_data, points = await rq.get_vote_details_with_points(vote_id)
    if not vote_data:
        await callback_query.message.edit_text('Голосование не найдено.', reply_markup=kb.inline_main_menu)
        return
    vote = vote_data[0]
    points = [point[0] for point in points]
    # Создаем данные о голосовании и связанных с ним точках
    await state.update_data(vote=vote, points=points)
    # Отображаем первый пункт голосования
    await show_next_point(callback_query.message, state)


# Функция для отображения следующего пункта голосования
# Обработчик для вывода деталей голосования
@router.callback_query(lambda c: c.data == 'show_details')
async def show_vote_details_message(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    vote = data['vote']

    details = (f"Тема: {vote.topic}\n"
               f"Описание: {vote.description}\n"
               f"Дата начала: {vote.start_time}\n"
               f"Дата окончания: {vote.end_time}\n"
               f"Очное голосование: {'Да' if vote.is_in_person else 'Нет'}\n"
               f"Закрытое голосование: {'Да' if vote.is_closed else 'Нет'}\n"
               f"Видимость в процессе: {'Да' if vote.is_visible_in_progress else 'Нет'}\n")

    await callback_query.message.edit_text(details)


# Функция для отображения следующего пункта голосования
@router.callback_query(lambda c: c.data == 'next_point')
async def show_next_point(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    points = data['points']

    # Проверяем, есть ли еще точки для отображения
    if not points:
        await callback_query.message.edit_text('Все пункты голосования показаны.', reply_markup=kb.inline_main_menu)
        return

    # Получаем текущий пункт голосования
    point = points[0]

    # Формируем текст сообщения для текущего пункта с выделением жирным шрифтом
    text = f"Вопрос:\n<b>{point.body}</b>\n\n"

    # Отправляем сообщение с текущим пунктом и кнопками для голосования
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data='answer_yes')],
        [InlineKeyboardButton(text="Нет", callback_data='answer_no')],
        [InlineKeyboardButton(text="Затрудняюсь ответить", callback_data='answer_uncertain')]
    ])
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode="html")

    # Обновляем состояние
    await state.update_data(points=points)


# Получаем ID пользователя
async def get_user_id(callback_query: CallbackQuery) -> int:
    # Реализуйте получение ID пользователя
    user_id = callback_query.from_user.id
    return user_id


# Обработка ответа "Да"
@router.callback_query(lambda c: c.data == 'answer_yes')
async def handle_answer_yes(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    points = data['points']
    if not points:
        await callback_query.message.edit_text('Все пункты голосования показаны.', reply_markup=kb.inline_main_menu)
        return
    # Получаем текущий пункт голосования
    point = points.pop(0)
    # Сохраняем результат в базу данных
    user_id = await get_user_id(callback_query)
    await rq.save_result(client_id=user_id, point_id=point.id, option_id=1)
    # Обновляем состояние
    await state.update_data(points=points)
    # Переходим к следующему пункту голосования
    await show_next_point(callback_query, state)


# Обработка ответа "Нет"
@router.callback_query(lambda c: c.data == 'answer_no')
async def handle_answer_no(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    points = data['points']
    if not points:
        await callback_query.message.edit_text('Все пункты голосования показаны.', reply_markup=kb.inline_main_menu)
        return
    # Получаем текущий пункт голосования
    point = points.pop(0)
    # Сохраняем результат в базу данных
    user_id = await get_user_id(callback_query)
    await rq.save_result(client_id=user_id, point_id=point.id, option_id=0)
    # Обновляем состояние
    await state.update_data(points=points)
    # Переходим к следующему пункту голосования
    await show_next_point(callback_query, state)


# Обработка ответа "Затрудняюсь ответить"
@router.callback_query(lambda c: c.data == 'answer_uncertain')
async def handle_answer_uncertain(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    points = data['points']
    if not points:
        await callback_query.message.edit_text('Все пункты голосования показаны.', reply_markup=kb.inline_main_menu)
        return
    # Получаем текущий пункт голосования
    point = points.pop(0)
    # Сохраняем результат в базу данных
    user_id = await get_user_id(callback_query)
    await rq.save_result(client_id=user_id, point_id=point.id, option_id=2)
    # Обновляем состояние
    await state.update_data(points=points)
    # Переходим к следующему пункту голосования
    await show_next_point(callback_query, state)


# Обработка кнопки "Продолжить"
@router.callback_query(lambda c: c.data == 'next_point')
async def continue_showing_points(callback_query: CallbackQuery, state: FSMContext):
    # Получаем текущее сообщение и отображаем следующий пункт голосования
    await show_next_point(callback_query.message, state)


@router.callback_query(lambda c: c.data == "to_inline_menu")
async def to_inline_menu(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer('')
    await callback_query.message.edit_text("Возврат  в меню.", reply_markup=kb.inline_main_menu)


# Для reply-кнопки
@router.message(F.text == 'Проголосовать')
async def show_votes(message: Message):
    user_id = message.from_user.id
    votes = await rq.get_active_votes(user_id)
    if not votes:
        await message.answer('Нет доступных голосований.', reply_markup=kb.inline_main_menu)
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=vote['topic'], callback_data=f"vote_{vote['id']}")] for vote in votes
    ] + [
        [InlineKeyboardButton(text="Выход", callback_data='to_inline_menu')]
    ])
    await message.answer('Выберите голосование:', reply_markup=keyboard)


#Личный кабинет
@router.message(lambda message: message.text == "Личный кабинет")
async def handle_reply_button(message: Message):
    user_info, areas = await rq.fetch_user_info_and_areas(message.from_user.id)

    if user_info:
        user_info_text = (
            f"Имя: {user_info['first_name']}\n"
            f"Фамилия: {user_info['second_name']}\n"
            f"Отчество: {user_info['patronymic']}\n"
            f"Телефон: {user_info['phone_number']}\n"
            f"Email: {user_info['email']}\n"
            f"Уровень доступа: {'Админ' if user_info['access_level'] else 'Пользователь'}\n"
        )
        if areas:
            areas_info = "\n".join(
                [f"Адрес: {area['address']}\nКадастровый номер: {area['cadastral_number']}\n" for area in areas])
        else:
            areas_info = None

        await rq.send_user_info(message, user_info_text, areas_info)
    else:
        await message.answer("Пользователь не найден.")


# Обработчик для inline-кнопки "Личный кабинет"
@router.callback_query(lambda c: c.data == 'lc')
async def handle_inline_button(callback_query: CallbackQuery):
    user_info, areas = await rq.fetch_user_info_and_areas(callback_query.from_user.id)

    if user_info:
        user_info_text = (
            f"Имя: {user_info['first_name']}\n"
            f"Фамилия: {user_info['second_name']}\n"
            f"Отчество: {user_info['patronymic']}\n"
            f"Телефон: {user_info['phone_number']}\n"
            f"Email: {user_info['email']}\n"
            f"Уровень доступа: {'Админ' if user_info['access_level'] else 'Пользователь'}\n"
        )
        if areas:
            areas_info = "\n".join(
                [f"Адрес: {area['address']}\nКадастровый номер: {area['cadastral_number']}\n" for area in areas])
        else:
            areas_info = None

        await rq.send_user_info(callback_query, user_info_text, areas_info)
        await callback_query.answer()  # Закрываем inline-кнопку без всплывающего сообщения
    else:
        await callback_query.message.answer("Пользователь не найден.")
