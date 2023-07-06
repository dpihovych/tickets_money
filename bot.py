import asyncio
import mysql.connector
import hashlib
from datetime import datetime
from typing import Any, Dict

import pytz
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder

confirmation_id = -1001940203308  # ТУТ_ІД_ЧАТУ_В_ЯКИЙ_ТРЕБА_ПЕРЕСИЛАТИ_З_КНОПКОЮ_ПІДТВЕРДИТИ
send_to_id = -1001911886415  # ТУТ_ІД_ГРУПИ_КУДИ_МАЄ_НАДСИЛАТИСЯ_ВЖЕ_ПОГОДЖЕНЕ

base = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Qwerty12345",
    port="3320",
    database="tickets_money"
)

# print(mydb)
cursor = base.cursor()
cursor.execute(
    "CREATE TABLE IF NOT EXISTS money (""id INT AUTO_INCREMENT PRIMARY KEY, "
                                        "direction VARCHAR(255), "
                                        "sum INT UNSIGNED, currency "
                                        "VARCHAR(255), "
                                        "method VARCHAR(255), "
                                        "city VARCHAR(255), "
                                        "info VARCHAR(255), "
                                        "recipient VARCHAR(255), "
                                        "date DATE )")

router = Router()

BOT_TOKEN = "5992895337:AAGs4f43YVZRftOf_Aa75nzATebQRN6uUQg"
bot = Bot(BOT_TOKEN, parse_mode="HTML")


class Form(StatesGroup):
    direction = State()
    sum = State()
    currency = State()
    info = State()
    method = State()
    city = State()
    recipient = State()


@router.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    kb = [
        [
            types.KeyboardButton(text="Добавити заявку 🤝"),
        ]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True
    )
    await message.answer(f"Привіт, <b>{message.from_user.full_name}!</b>", reply_markup=keyboard)


@router.message(Text("Добавити заявку 🤝"))
async def send_random_value(message: Message, state: FSMContext):
    await state.set_state(Form.direction)
    await message.answer("Введіть номер напрямку")


@router.message(Form.direction)
async def direction(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(direction=message.text)
        await state.set_state(Form.sum)
        await message.answer("Введіть суму")
    else:
        await message.answer("Введіть число, а не букву/букви")


@router.message(Form.sum)
async def direction(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(sum=message.text)
        await state.set_state(Form.currency)
        await message.answer(
            f"Виберіть валюту",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="Долар"),
                        KeyboardButton(text="Євро"),
                        KeyboardButton(text="Гривня")
                    ]
                ],
                resize_keyboard=True,
            ),
        )
    else:
        await message.answer("Введіть число, а не букву/букви")


@router.message(Form.currency)
async def direction(message: Message, state: FSMContext):
    if message.text == "Долар" or message.text == "Євро" or message.text == "Гривня":
        await state.update_data(currency=message.text)
        await state.set_state(Form.info)
        await message.answer(f"Введіть опис", reply_markup=ReplyKeyboardRemove())
    else:
        await message.answer(f"Виберіть валюту натиснувши на кнопку")


@router.message(Form.info)
async def direction(message: Message, state: FSMContext):
    await state.update_data(info=message.text)
    await state.set_state(Form.method)
    await message.answer(
        f"Виберіть метод оплати",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Готівка"),
                    KeyboardButton(text="Перерахунок")
                ]
            ],
            resize_keyboard=True,
        ),
    )


@router.message(Form.method)
async def direction(message: Message, state: FSMContext):
    if message.text == "Готівка" or message.text == "Перерахунок":
        await state.update_data(method=message.text)
        await state.set_state(Form.city)
        await message.answer(f"Введіть місто отримувача")
    else:
        await message.answer("Виберіть метод оплати натиснувши на кнопку")


@router.message(Form.city)
async def direction(message: Message, state: FSMContext):
    if message.text.isalpha():
        await state.update_data(city=message.text)
        await state.set_state(Form.recipient)
        await message.answer(f"Введіть отримувача типу <b>@username</b>")
    else:
        await message.answer("Введіть місто, а не цифри/цифру")


@router.message(Form.recipient)
async def direction(message: Message, state: FSMContext):
    if message.text.startswith("@"):
        data = await state.update_data(recipient=message.text)
        kb = [
            [types.KeyboardButton(text="Добавити заявку 🤝")]
        ]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True
        )

        await message.answer(f"Заявка відправлена", reply_markup=keyboard)
        await show_summary(message=message, data=data)
    else:
        await message.answer("Ви ввели не <b>@username</b>")


async def show_summary(message: Message, data: Dict[str, Any]):
    cursor.execute("SELECT id FROM money")
    _ = cursor.fetchall()  # Очищення результату запиту

    cursor.execute("SELECT MAX(id) FROM money")
    result = cursor.fetchone()
    if result and result[0]:
        id_str = result[0] + 1
    else:
        id_str = 1

    id = str(id_str).zfill(4)  # Додаємо передні нулі до id
    # print("id ", id)
    direction = data["direction"]
    sum = data["sum"]
    currency = data["currency"]
    info = data["info"]
    method = data["method"]
    city = data["city"]
    recipient = data["recipient"]
    date = datetime.now(pytz.timezone('Europe/Kiev'))
    text = f'<b>Номер заявки</b> - {id}\n' \
           f'<b>Номер напрямку</b> - {direction}\n' \
           f'<b>Сума</b> - {sum}\n' \
           f'<b>Валюта</b> - {currency}\n' \
           f'<b>Опис</b> - {info}\n' \
           f'<b>Отримувач</b> - {recipient}'

    # insert_info = "INSERT INTO money (id, direction, sum, currency, info, method, city, recipient, date)" \
    #               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    # value = (id_str, direction, sum, currency, info, method, city, recipient, date)
    # cursor.execute(insert_info, value)
    # base.commit()

    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(
        text=f"Погодити заявку ✅", callback_data=f"1")
    )

    await bot.send_message(confirmation_id, text=text, reply_markup=builder.as_markup())

    # await message.answer(text=text, reply_markup=ReplyKeyboardRemove())


async def add_to_db(data: Dict[str, Any]):
    cursor.execute("SELECT id FROM money")
    _ = cursor.fetchall()
    cursor.execute("SELECT MAX(id) FROM money")
    result = cursor.fetchone()
    if result and result[0]:
        id_str = result[0] + 1
    else:
        id_str = 1
    id = str(id_str).zfill(4)
    # print("id ", id)
    direction = data["direction"]
    sum = data["sum"]
    currency = data["currency"]
    info = data["info"]
    method = data["method"]
    city = data["city"]
    recipient = data["recipient"]
    date = datetime.now(pytz.timezone('Europe/Kiev'))
    insert_info = "INSERT INTO money (id, direction, sum, currency, info, method, city, recipient, date)" \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    value = (id_str, direction, sum, currency, info, method, city, recipient, date)
    cursor.execute(insert_info, value)
    base.commit()


@router.callback_query((Text(startswith="1")))
async def callback(callback_query: types.CallbackQuery):
    await callback_query.message.delete()
    cursor = base.cursor(buffered=True)
    cursor.execute(
        'SELECT id, direction, sum, currency, info,  method, city, recipient, date FROM money ORDER BY id DESC LIMIT 1')
    r = cursor.fetchone()
    # print(r)

    await bot.send_message(send_to_id, f"<b>Номер заявки</b> - {r[0]}\n"
                                       f"<b>Номер напрямку</b> - {r[1]}\n"
                                       f"<b>Сума</b> - {r[2]}\n"
                                       f"<b>Валюта</b> - {r[3]}\n"
                                       f"<b>Опис</b> - {r[4]}\n"
                                       f"<b>Метод оплати</b> - {r[5]}\n"
                                       f"<b>Місто отримувача</b> - {r[6]}\n"
                                       f"<b>Отримувач</b> - {r[7]}\n"
                                       f"<b>Статус</b> - Підтвердженно✅ @{callback_query.from_user.username}")
    await add_to_db()


# @router.message()
# async def echo_handler(message: types.Message) -> None:
#     await message.send_copy(chat_id=message.chat.id)


async def main() -> None:
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Bot was started successfully")
    asyncio.run(main())
