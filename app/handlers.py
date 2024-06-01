import asyncio

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb

router = Router()

class Test(StatesGroup):
    name = State()
    number = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.reply('sadasdsa',
                        reply_markup=kb.main)


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