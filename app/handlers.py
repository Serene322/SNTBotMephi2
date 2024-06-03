import asyncio
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
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


# Обработка кнопки "Создать голосование"
@router.message(F.text == "Создать голосование")
async def create_vote_start(message: Message):
    await message.answer('Вы находитесь в меню создания голосования.', reply_markup=kb.create_vote_menu)


# Обработка callback от кнопки "Начать создание голосования"
@router.callback_query(lambda c: c.data == "create_vote_start")
async def create_vote_callback(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(CreateVote.topic)
    await callback_query.message.edit_text("Введите тему голосования:")


@router.callback_query(lambda c: c.data == "create_vote_cancel")
async def cancel_create_vote(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer('')
    await callback_query.message.edit_text("Создание голосования отменено.")
    await state.clear()


# Пошаговая обработка создания голосования
@router.message(CreateVote.topic)
async def set_vote_topic(message: Message, state: FSMContext):
    await state.update_data(topic=message.text)
    await state.set_state(CreateVote.description)
    await message.answer("Введите описание голосования:")


# Обработка ввода описания голосования
@router.message(CreateVote.description)
async def set_vote_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(CreateVote.start_time)
    await message.answer("Введите дату начала голосования (в формате ГГГГ-ММ-ДД):")


# Обработка ввода даты начала голосования
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
    await message.answer("Введите дату окончания голосования (в формате ГГГГ-ММ-ДД):")


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
    if current_state == CreateVote.is_in_person:
        await state.update_data(is_in_person=value)
        await state.set_state(CreateVote.is_closed)
        await callback_query.message.edit_text("Голосование закрытое? (да/нет):", reply_markup=kb.yes_no_keyboard)
    elif current_state == CreateVote.is_closed:
        await state.update_data(is_closed=value)
        await state.set_state(CreateVote.is_visible_in_progress)
        await callback_query.message.edit_text("Информация видна в процессе? (да/нет):", reply_markup=kb.yes_no_keyboard)
    elif current_state == CreateVote.is_visible_in_progress:
        await state.update_data(is_visible_in_progress=value)
        await state.set_state(CreateVote.add_point)
        await callback_query.message.edit_text("Введите первый пункт голосования:")


@router.message(CreateVote.add_point)
async def add_vote_point(message: Message, state: FSMContext):
    data = await state.get_data()
    vote_id = data.get('vote_id')
    if not vote_id:
        vote_id = await rq.create_vote(data)
        await state.update_data(vote_id=vote_id)

    point_body = message.text
    point_id = await rq.add_point(vote_id, point_body)
    await state.update_data(point_id=point_id)
    await state.set_state(CreateVote.add_option)
    await message.answer("Введите первый вариант ответа для данного пункта:", reply_markup=kb.point_option_keyboard)


@router.message(CreateVote.add_option)
async def add_vote_option(message: Message, state: FSMContext):
    data = await state.get_data()
    point_id = data['point_id']
    option_body = message.text
    await rq.add_option(point_id, option_body)
    await message.answer("Введите следующий вариант ответа или выберите действие:", reply_markup=kb.point_option_keyboard)


@router.callback_query(lambda c: c.data == "add_option")
async def add_another_option(callback_query: CallbackQuery):
    await callback_query.message.edit_text("Введите следующий вариант ответа:", reply_markup=kb.point_option_keyboard)


@router.callback_query(lambda c: c.data == "add_point")
async def add_another_point(callback_query: CallbackQuery, state: FSMContext):
    await state.set_state(CreateVote.add_point)
    await callback_query.message.edit_text("Введите следующий пункт голосования:")


@router.callback_query(lambda c: c.data == "finalize_vote")
async def finalize_vote(callback_query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    data['is_finished'] = True
    await rq.save_vote(data)
    await state.clear()
    await callback_query.message.edit_text("Голосование завершено и сохранено.", reply_markup=None)


# # Обработка ответа на вопрос о типе голосования
# @router.message(CreateVote.is_in_person)
# async def set_is_in_person(message: Message, state: FSMContext):
#     is_in_person = message.text.lower() in ['да', 'yes']
#     await state.update_data(is_in_person=is_in_person)
#     await state.set_state(CreateVote.is_closed)
#     await message.answer("Голосование закрытое? (да/нет):")
#
#
# # Обработка ответа на вопрос о закрытости голосования
# @router.message(CreateVote.is_closed)
# async def set_is_closed(message: Message, state: FSMContext):
#     # Ваша логика для обработки ответа на вопрос о закрытости голосования
#     is_closed = message.text.lower() in ['да', 'yes']
#     await state.update_data(is_closed=is_closed)
#     await state.set_state(CreateVote.is_visible_in_progress)
#     await message.answer("Информация видна в процессе? (да/нет):")
#
#
# # Обработка ответа на вопрос об отображении информации в процессе голосования
# @router.message(CreateVote.is_visible_in_progress)
# async def set_is_visible_in_progress(message: Message, state: FSMContext):
#     # Ваша логика для обработки ответа на вопрос об отображении информации в процессе голосования
#     is_visible_in_progress = message.text.lower() in ['да', 'yes']
#     await state.update_data(is_visible_in_progress=is_visible_in_progress)
#
#     data = await state.get_data()
#     vote_data = {
#         'creator_id': message.from_user.id,
#         'topic': data['topic'],
#         'description': data['description'],
#         'is_in_person': data['is_in_person'],
#         'is_closed': data['is_closed'],
#         'is_visible_in_progress': is_visible_in_progress,
#         'is_finished': False,
#         'start_time': data['start_time'],
#         'end_time': data['end_time']
#     }
#
#     vote_id = await rq.create_vote(vote_data)
#     await state.update_data(vote_id=vote_id)
#     await state.set_state(CreateVote.add_point)
#     await message.answer("Введите первый пункт голосования:")


# Обработка добавления пункта голосования
# @router.message(CreateVote.add_point)
# async def add_vote_point(message: Message, state: FSMContext):
#     data = await state.get_data()
#     vote_id = data['vote_id']
#     point_body = message.text
#     point_id = await rq.add_point(vote_id, point_body)
#     await state.update_data(point_id=point_id)
#     await state.set_state(CreateVote.add_option)
#     await message.answer("Введите первый вариант ответа для данного пункта:")
#
#
# # Обработка добавления варианта ответа
# @router.message(CreateVote.add_option)
# async def add_vote_option(message: Message, state: FSMContext):
#     data = await state.get_data()
#     point_id = data['point_id']
#     option_body = message.text
#     await rq.add_option(point_id, option_body)
#     await message.answer("Введите следующий вариант ответа или завершите добавление пунктов.")


# Обработка кнопки "Проголосовать"
@router.message(lambda message: message.text == "Проголосовать")
async def vote_start(message: Message):
    await message.answer('Выберите голосование из списка:', reply_markup=kb.vote_menu)


# Обработка кнопки "Личный кабинет"
@router.message(lambda message: message.text == "Личный кабинет")
async def personal_account(message: Message):
    await message.answer('Это ваш личный кабинет.')
