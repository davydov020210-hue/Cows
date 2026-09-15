import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, User
from aiogram.filters.command import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from func import *

logging.basicConfig(level=logging.INFO)

bot = Bot(token="8769780535:AAGa3m15uSR7IYa_U74OLVUHUNjKZabGUiM")
dp = Dispatcher()

class Milk(StatesGroup):
    wait_milk_count_for_sale = State()

class Cows(StatesGroup):
    name = State()
    income = State()
    price = State()
    code = State()

@dp.message(Command("start"))
async def start(message: types.Message):
    print(message.from_user.id)
    print(message.chat.id)
    user_in_base = get_user(message.from_user.id)
    if not user_in_base:
        reg(message.from_user.id)

    update(user_id=message.from_user.id)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Мои коровы", callback_data="my_cows"), InlineKeyboardButton(text="Купить коров", callback_data="buy_cows"), InlineKeyboardButton(text="Продать молоко", callback_data="sell_milk")], [InlineKeyboardButton(text="Обновить", callback_data="back_to_main_menu")]])
    await message.answer(f"{stat(user_id=message.from_user.id)}", reply_markup=keyboard)

@dp.callback_query(F.data.startswith("my_cows"))
async def my_cows(callback: types.CallbackQuery):
    cows = my_cows_func(callback.message.chat.id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")]])
    await callback.message.edit_text(cows, reply_markup=keyboard)

@dp.callback_query(F.data == "back_to_main_menu")
async def back_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    update(user_id=callback.message.chat.id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Мои коровы", callback_data="my_cows"), InlineKeyboardButton(text="Купить коров", callback_data="buy_cows"), InlineKeyboardButton(text="Продать молоко", callback_data="sell_milk")], [InlineKeyboardButton(text="Обновить", callback_data="back_to_main_menu")]])
    await callback.message.edit_text(f"{stat(user_id=callback.message.chat.id)}", reply_markup=keyboard)
    await state.clear()

@dp.message(Command("add_cow"))
async def add_cow(message: types.Message, state: FSMContext):
    await message.answer("Введите навание коровы")
    await state.set_state(Cows.name)

@dp.message(Cows.name)
async def set_name(message: types.Message, state: FSMContext):
    await state.update_data(name = message.text)
    await message.answer("Введите доход коровы")
    await state.set_state(Cows.income)

@dp.message(Cows.income)
async def set_income(message: types.Message, state: FSMContext):
    await state.update_data(income = int(message.text))
    await message.answer("Введите цену коровы")
    await state.set_state(Cows.price)

@dp.message(Cows.price)
async def set_price(message: types.Message, state: FSMContext):
    await state.update_data(price = int(message.text))
    await message.answer("Введите код коровы на английском")
    await state.set_state(Cows.code)

@dp.message(Cows.code)
async def set_code(message: types.Message, state: FSMContext):
    await state.update_data(code = message.text)
    new_cow = await state.get_data()
    await state.clear()
    register_new_cow(new_cow["name"], new_cow["income"], new_cow["price"], new_cow["code"])

async def periodic_task():
    while True:
        now = time.time()

        seconds_passed_this_hour = now % 3600
        seconds_to_wait = 3600 - seconds_passed_this_hour

        await asyncio.sleep(seconds_to_wait)

        change_milk_price()

@dp.callback_query(F.data == "sell_milk")
async def sell_milk_amount(callback: types.CallbackQuery, state: FSMContext):
    milk = get_user(callback.message.chat.id)[1]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="25%", callback_data="sell_25"), InlineKeyboardButton(text="50%", callback_data="sell_50"), InlineKeyboardButton(text="75%", callback_data="sell_75"), InlineKeyboardButton(text="100%", callback_data="sell_100")], [InlineKeyboardButton(text="Назад", callback_data="back_to_main_menu")]])
    await callback.message.edit_text( f"У вас молока: {milk}\n" f"Молоко стоит: {get_milk_price()} руб\n" f"Сколько молока продать?", reply_markup=keyboard )
    await state.set_state(Milk.wait_milk_count_for_sale)

@dp.callback_query(F.data.startswith("sell_"))
async def sell_milk_percent(callback: types.CallbackQuery):
    percent = int(callback.data.replace("sell_", ""))

    milk = get_user(callback.from_user.id)[1]

    amount = int(milk * percent / 100)

    result = sell_milk_func(user_id=callback.from_user.id, user_milk_sell=amount)

    await callback.message.edit_text(f"Продано молока: {amount}\n Получено: {amount * MILK_PRICE} руб\n {result}", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Продать ещё",callback_data="sell_milk")],[InlineKeyboardButton(text="Назад",callback_data="back_to_main_menu")]]))

#@dp.callback_query(F.data == "update")
#async def update

@dp.callback_query(F.data.startswith("buy_cows"))
async def choose_cow(callback: types.CallbackQuery):

    choose_keyboard = InlineKeyboardMarkup(inline_keyboard=cow_keyboard())
    await callback.message.edit_text("Выберите корову:", reply_markup=choose_keyboard)

def cow_keyboard():
    buttons = []
    
    for cow in get_cows():
        buttons.append([InlineKeyboardButton(text=f"{cow[1]}, {cow[3]}руб.", callback_data=f"buy-ask_{cow[0]}")])
    buttons.append([InlineKeyboardButton(text="Главное меню", callback_data="back_to_main_menu")])
    return buttons

@dp.callback_query(F.data.startswith("buy-ask"))
async def buy_normal__cow(callback: types.CallbackQuery):
    cow_id = callback.data.replace("buy-ask_", "")
    cow = get_cow(cow_id)
    if cow:
        buy_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Да", callback_data=f"buy_{cow_id}"), InlineKeyboardButton(text="Нет", callback_data="no_buy")]])
        await callback.message.edit_text(f"Цена коровы: {cow[3]}", reply_markup=buy_keyboard)
    else:
        await callback.answer("Корова не найдена")

@dp.callback_query(F.data.startswith("buy_"))
async def buy_cow(callback: types.CallbackQuery):
    cow_id = callback.data.replace("buy_", "")

    result = buy_cow_func(user_id=callback.from_user.id, cow_id=cow_id)

    if result:
        await callback.answer("Корова приобретена")
        await choose_cow(callback)
    else:
        await callback.answer("Ошибка при покупке")
        await choose_cow(callback)

@dp.callback_query(F.data.startswith("reg"))
async def register(callback: types.CallbackQuery):
    reg(callback.from_user.id)
    await callback.message.answer("Пользователь добвлен")
    await callback.message.answer(text=my_cows_func(callback.from_user.id))

@dp.message(Milk.wait_milk_count_for_sale)
async def sell_milk(message: types.Message):
    try:
        amount = int(message.text)
    except ValueError:
        await message.answer("Введите число")
        return
    result = sell_milk_func(user_id=message.from_user.id, user_milk_sell=amount)
    await message.answer(result)

async def main():
    asyncio.create_task(periodic_task())
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())