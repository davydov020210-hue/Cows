import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, User
from aiogram.filters.command import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from func import *

class Cows(StatesGroup):
    name = State()
    income = State()
    price = State()
    code = State()

admin_router = Router()

@admin_router.message(Command("add_cow"))
async def add_cow(message: types.Message, state: FSMContext):
    await message.answer("Введите навание коровы")
    await state.set_state(Cows.name)

@admin_router.message(Cows.name)
async def set_name(message: types.Message, state: FSMContext):
    await state.update_data(name = message.text)
    await message.answer("Введите доход коровы")
    await state.set_state(Cows.income)

@admin_router.message(Cows.income)
async def set_income(message: types.Message, state: FSMContext):
    await state.update_data(income = int(message.text))
    await message.answer("Введите цену коровы")
    await state.set_state(Cows.price)

@admin_router.message(Cows.price)
async def set_price(message: types.Message, state: FSMContext):
    await state.update_data(price = int(message.text))
    await message.answer("Введите код коровы на английском")
    await state.set_state(Cows.code)

@admin_router.message(Cows.code)
async def set_code(message: types.Message, state: FSMContext):
    await state.update_data(code = message.text)
    new_cow = await state.get_data()
    await state.clear()
    register_new_cow(new_cow["name"], new_cow["income"], new_cow["price"], new_cow["code"])