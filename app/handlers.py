from aiogram import F, Router
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from db.models import get_user_data, save_user_data

user_data = {}

router = Router()


class Reg(StatesGroup):
    id_user = State()
    vin = State()
    year = State()


@router.message(Command('start'))
async def start_command(message: Message, state: FSMContext):
    await state.set_state(Reg.vin)
    await message.answer(f'Привет 👋, {message.from_user.full_name}!\n'
                         f'Я бот, который поможет тебе найти нужные запчасти быстро и без лишних хлопот.'
                         f'🔍 Введи VIN и год автомобиля🚗 по форме ниже👇 — и я подберу для тебя подходящие детали.\n\n'
                         f'Ваш VIN: ')


@router.message(Command("reply"))
async def reply_to_user(message: Message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("⚠ Используйте: /reply ID текст")
        return

    user_id, text = args[1], args[2]

    try:
        chat = await message.bot.get_chat(user_id)
        await message.bot.send_message(chat.id, text)
        await message.answer(f"✅ Сообщение отправлено пользователю {chat.id}!")
    except Exception as e:
        await message.answer(f"⚠ Ошибка: {e}")


@router.message(Reg.vin)
async def reg_vin(message: Message, state: FSMContext):
    await state.update_data(vin=message.text)
    await state.set_state(Reg.year)
    await message.answer('Введите год автомобиля: ')


@router.message(Reg.year)
async def reg_number(message: Message, state: FSMContext):
    await state.update_data(year=message.text)
    await state.set_state(Reg.id_user)
    await message.answer("И марку вашего авто: ")


@router.message(Reg.id_user)
async def finish_reg(message: Message, state: FSMContext):
    await state.update_data(id_user=message.from_user.id)
    data = await state.get_data()
    user_data[message.from_user.id] = {
        "vin": data["vin"],
        "year": data["year"]
    }
    await save_user_data(str(message.from_user.id), data["vin"], data["year"])

    await message.answer('Введите что нужно подобрать: ')
    await message.bot.send_message(-1002200498147, f'🔹 Новый пользователь зарегистрирован:\n'
                                                   f'👤 ID: {message.from_user.id}\n'
                                                   f'🚗 VIN: {data["vin"]}\n'
                                                   f'📅 Год: {data["year"]}')
    await state.clear()


@router.message()
async def forward_to_group(message: Message):
    user_id = str(message.from_user.id)
    user_info = await get_user_data(user_id)

    if user_info:
        vin, year = user_info
    else:
        vin, year = "Неизвестен", "Неизвестен"

    text = f'📩 Сообщение от {message.from_user.full_name}:\n' \
           f'👤 ID: {user_id}\n' \
           f'🚗 VIN: `{vin}`\n' \
           f'📅 Год: {year}\n' \
           f'💬 Сообщение: {message.text}'

    await message.bot.send_message(-1002200498147, text, parse_mode="MARKDOWN")
