
from datetime import datetime
from aiogram import Router, F
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

@router.message(F.text == "Создать голосование")
async def create_vote_start(message: Message):
    await message.answer('Вы находитесь в меню создания голосования.', reply_markup=kb.create_vote_menu)

@router.callback_query(lambda c: c.data == "create_vote_start")
async def create_vote_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(CreateVote.topic)
    await state.update_data(description=None, is_in_person=0, is_closed=0, is_visible_in_progress=0, start_time=None, end_time=None, is_finished=False, points=[])
    await callback_query.message.edit_text("Введите тему голосования:", reply_markup=kb.stop_vote_keyboard)

@router.callback_query(lambda c: c.data == "create_vote_save")
async def create_vote_save(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await rq.save_incomplete_vote(data, callback_query.from_user.id)
    await state.clear()
    await callback_query.message.edit_text("Черновик сохранен.", reply_markup=kb.inline_main_menu)

@router.callback_query(lambda c: c.data == "create_vote_cancel")
async def cancel_create_vote(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer('')
    await callback_query.message.edit_text("Создание голосования отменено.", reply_markup=kb.inline_main_menu)
    await state.clear()


@router.message(CreateVote.topic)
async def set_vote_topic(message: Message, state: FSMContext):
    data = await state.get_data()
    is_editing = data.get('is_editing', False)

    if is_editing:
        # В случае редактирования голосования вызываем соответствующую функцию для обновления темы
        vote_id = data.get('edit_vote_id')
        await rq.update_vote_topic(vote_id, message.text)
        await state.clear()
        await message.answer("Тема голосования успешно обновлена.", reply_markup=kb.inline_main_menu)
    else:
        # В противном случае, продолжаем процесс создания нового голосования
        await state.update_data(topic=message.text)
        await state.set_state(CreateVote.description)
        await message.answer("Введите описание голосования:", reply_markup=kb.stop_vote_keyboard)


@router.message(CreateVote.description)
async def set_vote_description(message: Message, state: FSMContext):
    data = await state.get_data()
    is_editing = data.get('is_editing', False)

    if is_editing:
        # В случае редактирования голосования вызываем соответствующую функцию для обновления описания
        vote_id = data.get('edit_vote_id')
        await rq.update_vote_description(vote_id, message.text)
        await state.clear()
        await message.answer("Описание голосования успешно обновлено.", reply_markup=kb.inline_main_menu)
    else:
        # В противном случае, продолжаем процесс создания нового голосования
        await state.update_data(description=message.text)
        await state.set_state(CreateVote.start_time)
        await message.answer("Введите дату начала голосования (в формате ГГГГ-ММ-ДД):", reply_markup=kb.stop_vote_keyboard)



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
    await message.answer("Введите дату окончания голосования (в формате ГГГГ-ММ-ДД):", reply_markup=kb.stop_vote_keyboard)


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
        #Если значение в БД отличается от введённого пользователем, то мы делаем апдейт
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
@router.message(lambda message: message.text == "vo")
async def vote_start(message: Message):
    await message.answer('Выберите голосование из списка:', reply_markup=kb.vote_menu)

'''
 Обработка кнопки "Личный кабинет"
@router.message(lambda c: c.data == "lc")
async def personal_account(message: Message):
    await message.answer('Это ваш личный кабинет.')
'''

#Дальше всё для Редактирования черновиков
#Кнопка изменить для РЕПЛАЙ-клавиатуры
@router.message(F.text == "Изменить голосование")
async def change_vote_start(message: Message):
    votes = await rq.get_unfinished_votes(message.from_user.id)
    if not votes:
        await message.answer('Нет доступных голосований для изменения.')
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=vote['topic'], callback_data=f"edit_vote_{vote['id']}")] for vote in votes
    ])
    await message.answer('Выберите голосование для изменения:', reply_markup=keyboard)

#Кнопка изменить для ИНЛАЙН-клавиатуры
@router.callback_query(lambda c: c.data == "change")
async def inline_change_vote_start(callback_query: CallbackQuery):
    votes = await rq.get_unfinished_votes(callback_query.from_user.id)
    if not votes:
        await callback_query.answer('Нет доступных голосований для изменения.')
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=vote['topic'], callback_data=f"edit_vote_{vote['id']}")] for vote in votes
    ])
    await callback_query.message.edit_text('Выберите голосование для изменения:', reply_markup=keyboard)


#Обработчик для выбора голосования и отображения его данных
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

#Обработчики для изменения  данных голосования
@router.callback_query(lambda c: c.data == "edit_topic")
async def edit_topic_start(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(CreateVote.topic)
    await callback_query.message.edit_text("Введите новую тему голосования:", reply_markup=kb.stop_vote_keyboard)

@router.callback_query(lambda c: c.data == "edit_description")
async def edit_description_start(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(CreateVote.description)
    await callback_query.message.edit_text("Введите новое описание голосования:", reply_markup=kb.stop_vote_keyboard)
    #FROM HERE
@router.callback_query(lambda c: c.data == "edit_is_in_person")
async def edit_is_in_person_start(callback_query: CallbackQuery, state: FSMContext):
    # Получаем текущее значение переменной
    data = await state.get_data()
    current_value = data.get('is_in_person', False)  # Устанавливаем значение по умолчанию в False
    new_value = not current_value  # Инвертируем текущее значение
    # Сохраняем новое значение переменной в контексте состояния
    await state.update_data(is_in_person=new_value)
    # Определяем текст сообщения в зависимости от нового значения переменной
    message_text = "Вы изменили тип голосования на очное." if new_value else "Вы изменили тип голосования на неочное."
    await callback_query.message.edit_text(message_text)
    # Изменяем клавиатуру в сообщении
    await callback_query.message.edit_reply_markup(reply_markup=kb.inline_main_menu)


@router.callback_query(lambda c: c.data == "edit_is_closed")
async def edit_is_closed(callback_query: CallbackQuery, state: FSMContext):
    # Получаем текущее значение переменной
    data = await state.get_data()
    current_value = data.get('is_closed', False)  # Устанавливаем значение по умолчанию в False
    new_value = not current_value  # Инвертируем текущее значение
    # Сохраняем новое значение переменной в контексте состояния
    await state.update_data(is_closed=new_value)
    # Определяем текст сообщения в зависимости от нового значения переменной
    message_text = "Вы изменили тип голосования на закрытое." if new_value else "Вы изменили тип голосования на открытое."
    await callback_query.message.edit_text(message_text)
    # Изменяем клавиатуру в сообщении
    await callback_query.message.edit_reply_markup(reply_markup=kb.inline_main_menu)


@router.callback_query(lambda c: c.data == "edit_is_visible_in_progress")
async def edit_is_visible_in_progress(callback_query: CallbackQuery, state: FSMContext):
    # Получаем текущее значение переменной
    data = await state.get_data()
    current_value = data.get('is_visible_in_progress', False)  # Устанавливаем значение по умолчанию в False
    new_value = not current_value  # Инвертируем текущее значение
    # Сохраняем новое значение переменной в контексте состояния
    await state.update_data(is_visible_in_progress=new_value)
    # Определяем текст сообщения в зависимости от нового значения переменной
    message_text = "Вы изменили тип голосования на видимый в процессе." if new_value else "Вы изменили тип голосования на скрытый в процессе."
    await callback_query.message.edit_text(message_text)
    # Изменяем клавиатуру в сообщении
    await callback_query.message.edit_reply_markup(reply_markup=kb.inline_main_menu)



@router.callback_query(lambda c: c.data == "to_inline_main_menu")
async def to_inline_main_menu(callback_query: CallbackQuery, state: FSMContext):
    await edit_vote(callback_query, state)  # Запуск хэндлера edit_vote с текущими аргументами