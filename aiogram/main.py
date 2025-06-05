# Импорты
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.chat_member import *
from aiogram import *
from aiogram.types import *
from aiogram.filters import *
import asyncio
import config
import sqlite3
import quiz
import random

# Переменные
bot = Bot(token=config.token)  # Бот
dp = Dispatcher()  # Диспетчер

m = 0
conn = sqlite3.connect("Users.db", check_same_thread=False)  # Подключение к базе данных
cur = conn.cursor()  # Курсор


# start
@dp.message(CommandStart())
async def start(mes: Message):
    await mes.answer('Пока ничего интересного здесь нет.')


# help
@dp.message(Command('help'))
async def help_mes(mes: Message):
    await mes.answer('Пока ничего интересного здесь нет.')


# Принятие пользователя
@dp.chat_join_request()
async def requests(request: ChatJoinRequest):
    global m
    try:
        cur.execute("SELECT id FROM Users")
        n = cur.fetchall()
        for i in n:
            if request.from_user.id == i[0]:
                m = 1
                break
    except sqlite3.ProgrammingError:
        m = 0
    if m != 1:
        cur.execute("""INSERT INTO Users (id, name, asset, ban, unban) VALUES (?, ?, ?, ?, ?)""",
                    (request.from_user.id, f"{request.from_user.first_name}", False, False, "n"))
        conn.commit()
    cur.execute(f"SELECT ban FROM Users WHERE id={request.from_user.id}")
    ban = cur.fetchall()[0][0]
    cur.execute(f"SELECT asset FROM Users WHERE id={request.from_user.id}")
    ass = cur.fetchall()[0][0]
    if ban:
        await request.decline()
        await bot.send_message(request.from_user.id, f"Увы, {request.from_user.first_name}.\
                         Вам отказано так как Вы забанены.")
    elif ass:
        await request.approve()
        await bot.send_message(request.from_user.id, f"Добро пожаловать в {request.chat.title}!")
    elif request.from_user.id <= 5400000000:
        await request.approve()
        await bot.send_message(request.from_user.id, f"Поздравляю, {request.from_user.first_name}!\
                 Вы были приняты!")
        await bot.send_message(request.from_user.id, f"Добро пожаловать в {request.chat.title}!")
        cur.execute(f"UPDATE asset={True} FROM Users WHERE id={request.from_user.id}")

        conn.commit()
    elif request.from_user.id > 5400000000:

        m = InlineKeyboardBuilder()
        ques = random.randint(1, 8)
        q = quiz.quiz(ques)
        t = q[0]
        q.remove(t)
        for j in range(4):
            s = random.choice(q)
            m.row(InlineKeyboardButton(text=s[0], callback_data=f'{s[1]}'))
            q.remove(s)

        await bot.send_message(request.from_user.id, t, reply_markup=m.as_markup())


# locate
@dp.message(Command('locate'))
async def locate(mes: Message):
    if isinstance(await bot.get_chat_member(mes.chat.id, mes.from_user.id), ADMINS):
        await mes.answer(f"""ID: {mes.chat.id}
First name: {mes.chat.first_name}
Title: {mes.chat.title}
""")
    else:
        await mes.answer(f"""Вы не админ.
        """)


# ban Здесь скоро что-то будет
@dp.message(Command('ban'))
async def ban(mes: Message):
    await mes.answer('ban')


# unban Здесь скоро что-то будет
@dp.message(Command('unban'))
async def unban(mes: Message):
    await mes.answer('unban')


# test
@dp.message(Command('test'))
async def quiz_test(mes: Message):
    ma = InlineKeyboardBuilder()
    ques = random.randint(1, 8)
    q = quiz.quiz(ques)
    t = q[0]
    q.remove(t)
    for j in range(4):
        s = random.choice(q)
        ma.row(InlineKeyboardButton(text=s[0], callback_data=f'{s[1]}'))
        q.remove(s)

    await bot.send_message(mes.from_user.id, t, reply_markup=ma.as_markup())


# Callback
@dp.callback_query()
async def call(call: CallbackQuery):
    if call.data == "1":
        await bot.send_message(call.from_user.id, quiz.quiz(call="yes"))
        if quiz.q < 5:
            ma = InlineKeyboardBuilder()
            ques = random.randint(1, 8)
            q = quiz.quiz(ques)
            t = q[0]
            q.remove(t)
            for j in range(4):
                s = random.choice(q)
                ma.row(InlineKeyboardButton(text=s[0], callback_data=f'{s[1]}'))
                q.remove(s)

            await bot.send_message(call.from_user.id, t, reply_markup=ma.as_markup())
        else:
            await bot.send_message(call.from_user.id, quiz.quiz(call=""))
            if quiz.t >= 3:
                cur.execute(f"UPDATE asset={True} FROM Users WHERE id={call.from_user.id}")
                conn.commit()
    elif call.data == "0":
        await bot.send_message(call.from_user.id, quiz.quiz(call="no"))
        if quiz.q < 5:
            ma = InlineKeyboardBuilder()
            ques = random.randint(1, 8)
            q = quiz.quiz(ques)
            t = q[0]
            q.remove(t)
            for j in range(4):
                s = random.choice(q)
                ma.row(InlineKeyboardButton(text=s[0], callback_data=f'{s[1]}'))
                q.remove(s)

            await bot.send_message(call.from_user.id, t, reply_markup=ma.as_markup())
        else:
            await bot.send_message(call.from_user.id, quiz.quiz(call=""))
            if quiz.t >= 3:
                cur.execute(f"UPDATE asset={True} FROM Users WHERE id={call.from_user.id}")
                conn.commit()


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Turn off")
