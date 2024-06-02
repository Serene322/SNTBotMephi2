import asyncio

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


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Reg.email)
    await message.answer('Здравствуйте!')
    await message.answer('Для начала работы вам необходимо зарегистрироваться.')
    # await rq.set_user(message.from_user.id)
    # await message.reply('sadasdsa',
    #                     reply_markup=kb.main)

@router.message(Reg.email)
async def reg_first_step(message: Message, state: FSMContext):
    await message.answer('Укажите ваш email')
    await state.update_data(name=message.text)
    await state.set_state(Reg.password)
    await message.answer('Введите пароль')

@round.message(Reg.password)
async def reg_check_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    answer = await rq.registration(data['email'], data['password'])
    if answer == True:
        await rq.set_user(message.from_user.id)
        await message.answer('Авторизация прошла успешно')
        state.clear()
    else:
        await message.answer('Ошибка во время автоматизации')
        await state.set_state(Reg.email)


@router.callback_query(F.data == '1')
async def inline_test(callback: CallbackQuery):
    await callback.answer('sdgfdgd')
    await callback.message.answer('sadasd')

@router.message(Command('help'))
async def get_help(message: Message):
    await message.answer('sadasdsa')


@router.message(Command('show_client_info'))
async def get_info(message: Message):
    await message.answer('sadasdsa')


@router.message(Command('show_client_area'))
async def show_area(message: Message):
    await message.answer('sadasdsa')

@router.message(Command('add_vote'))
async def add_vote(message: Message):
    await message.answer('sadasdsa')

@router.message(Command('show_vote'))
async def show_vote(message: Message):
    await message.answer('sadasdsa')


@router.message(Command('show_points'))
async def show_points(message: Message):
    await message.answer('sadasdsa')


@router.message(Command('show_options'))
async def show_options(message: Message):
    await message.answer('sadasdsa')


@router.message(Command('add_points'))
async def add_points(message: Message):
    await message.answer('sadasdsa')


@router.message(Command('add_options'))
async def add_options(message: Message):
    await message.answer('sadasdsa')