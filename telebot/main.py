# Импорты
import random
import time
import telebot
import config
import sqlite3

# Переменные
conn = sqlite3.connect("Users.db", check_same_thread=False)
cur = conn.cursor()
bot = telebot.TeleBot(config.token)
asset = False
ban = False
q = 0
t = 0
URL = ""  # Ссылка в чат
password = "1234"  # Пароль вводимый в addrule addAssetAddrule
mti = 0  # messange thread id туда бот отправляет все заявки и не только
idMessange = 0  # id группы
m = 0
msg = None
# Правила
debug = False
typeServer = False
assetAddrule = False


# Хэндлеры
@bot.message_handler(commands=['start'])
def send_welcome(message):
    global m, typeServer
    if message.chat.id == idMessange:
        typeServer = True
    if not typeServer:
        m = 0
        g = telebot.types.InlineKeyboardMarkup()
        b = telebot.types.InlineKeyboardButton("Получить доступ", callback_data="getasset")
        g.add(b)
        bot.reply_to(message, """Привет! Этот бот сделан для того, чтобы не было спама в чатах.
        """, reply_markup=g)
        try:
            cur.execute("SELECT id FROM Users")
            n = cur.fetchall()
            for i in n:
                if message.from_user.id == i[0]:
                    m = 1
                    break
        except sqlite3.ProgrammingError:
            m = 0
        if m != 1:
            cur.execute("""INSERT INTO Users (id, name, asset, ban, unban) VALUES (?, ?, ?, ?, ?)""",
                        (message.from_user.id, f"{message.from_user.first_name}", False, False, "n"))
            conn.commit()
    else:
        bot.reply_to(message, """Привет! Этот бот просто существует.
                """)
    typeServer = False


# Help
@bot.message_handler(commands=['help'])
def help(message):
    global typeServer
    if message.chat.id == idMessange:
        typeServer = True
    if not typeServer:
        bot.reply_to(message, """Есть команды:
/start
/help
/addrule [правило] [значение]
/asset
        """)
    else:
        bot.reply_to(message, """Есть команды:
/start
/help
/addrule [правило] [значение]
/asset [id пользователя]
/locate {clear}
/ban
/unban
Все команды для админов
                """)
    if debug:
        bot.reply_to(message, f"""typeServer: {typeServer}
debug: {debug}
assetAddrule: {assetAddrule}
                        """)
    typeServer = False


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global m, asset
    if call.data == 'getasset':
        send_asset(call.message)
    if call.data == 'yes' or call.data == 'no':
        quiz(call=call.data, idc=call.message.chat.id)
    if len(call.data.split()) == 2:
        if call.data.split()[1] == "p":

            cur.execute("SELECT id FROM Users")
            n = cur.fetchall()
            for i in n:
                if int(call.data.split()[0]) == i[0]:
                    m = 1
            if m == 1:
                cur.execute(f"SELECT asset FROM Users WHERE id={int(call.data.split()[0])}")
                asset = cur.fetchall()
                if not asset[0][0]:
                    cur.execute("UPDATE Users SET asset=? WHERE id=?", (True, int(call.data.split()[0])))
                    conn.commit()
                    bot.reply_to(call.message,
                                 f"Одобрил {call.from_user.first_name} пользователу с id {call.data.split()[0]}")
                    bot.send_message(int(call.data.split()[0]), "Ваш запрос одобрили снова введите команду /asset")
                if asset[0][0]:
                    bot.reply_to(call.message, f"пользователя с id {call.data.split()[0]} уже одобрили")
        if call.data.split()[1] == "o":
            bot.reply_to(call.message, f"Отказал {call.from_user.first_name} пользователу с id {call.data.split()[0]}")
    if call.data.split()[0] == "ass":
        bot.delete_message(int(call.data.split()[1]), msg.id)


@bot.message_handler(commands=['addme'])
def send_addme(message):
    global m, typeServer
    if message.chat.id == idMessange:
        typeServer = True
    try:
        cur.execute("SELECT id FROM Users")
        n = cur.fetchall()
        for i in n:
            if message.from_user.id == i[0]:
                m = 1
                break
    except sqlite3.ProgrammingError:
        m = 0
    else:
        bot.send_message(idMessange, f"Пользователь уже добавлен")
    if m != 1:
        cur.execute("""INSERT INTO Users (id, name, asset, ban, unban) VALUES (?, ?, ?, ?, ?)""",
                    (message.from_user.id, f"{message.from_user.first_name}", False, False, "n"))
        bot.send_message(idMessange, f"Пользователь с id: {message.from_user.id}", message_thread_id=mti)
        conn.commit()
    typeServer = False


# Addrule
@bot.message_handler(commands=['addrule'])
def send_addrule(message):
    global debug, typeServer, assetAddrule
    if len(message.text.split()) == 3:
        if message.chat.id == idMessange:
            typeServer = True
        if typeServer and bot.get_chat_member(message.chat.id,
                                              message.from_user.id).status != "restricted" or not typeServer:
            if message.text.split()[1] == "debug" and assetAddrule:
                if message.text.split()[2].lower() == "false":
                    debug = False
                    bot.reply_to(message, f"Debug: {debug}")
                elif message.text.split()[2].lower() == "true":
                    debug = True
                    bot.reply_to(message, f"Debug: {debug}")
                else:
                    bot.reply_to(message, f"Значение должно быть true или false или у Вас нет доступа.")
            elif message.text.split()[1] == "debug" and not assetAddrule:
                bot.reply_to(message, f"У Вас нет доступа.")
            if message.text.split()[1] == "removeQuiz" and assetAddrule:
                g = telebot.types.InlineKeyboardMarkup()
                b = telebot.types.InlineKeyboardButton("Remove", callback_data="remove")
                g.add(b)
                bot.send_message(message.from_user.id, "Remove", reply_markup=g)
                if len(message.text.split()) <= 2:
                    bot.reply_to(message, "Нужно вставить какой-либо символ")
            elif message.text.split()[1] == "removeQuiz" and not assetAddrule:
                bot.reply_to(message, f"У Вас нет доступа.")
            if message.text.split()[1] == "addTicket" and assetAddrule and not typeServer:
                bot.send_message(idMessange, f"""Фамилия пользователя: {message.from_user.first_name}
    Id пользователя: {message.from_user.id}
    Ждет ответ на запрос P.S.: Если Вам попадется это сообщение просто удалите и не обращайте на него внимание""",
                                 message_thread_id=mti)
                if len(message.text.split()) <= 2:
                    bot.reply_to(message, "Нужно вставить какой-либо символ")
            elif message.text.split()[1] == "addTicket" and not assetAddrule:
                bot.reply_to(message, f"У Вас нет доступа.")
            elif message.text.split()[1] == "addTicket" and typeServer:
                bot.reply_to(message, f"Нельзя это сделать в группе.")

            if message.text.split()[1] == "addAssetAddrule":
                if message.text.split()[2] == password:
                    assetAddrule = not assetAddrule
                    bot.reply_to(message, f"assetAddrule: {assetAddrule}")
                else:
                    bot.reply_to(message, f"Значение должно быть конбинацией симвовов или неверный пароль.")
        else:
            bot.reply_to(message, f"У вас нет доступа")
    else:
        bot.reply_to(message, "Синтаксис: /addrule [правило] [значение]")
    typeServer = False


# Asset Внимание пользователь должен быть в базе данных, чтобы это работало!
@bot.message_handler(commands=['asset'])
def send_asset(message):
    global asset, m, bann, typeServer, msg
    if message.chat.id == idMessange:
        typeServer = True
    if not typeServer:
        cur.execute(f"SELECT asset FROM Users WHERE id={message.chat.id}")
        asset = cur.fetchall()
        cur.execute(f"SELECT ban FROM Users WHERE id={message.chat.id}")
        bann = cur.fetchall()
        if bann:
            if debug:
                bot.send_message(message.chat.id, f"Time: {time.ctime(time.time())}")
            cur.execute(f"SELECT unban FROM Users WHERE id={message.chat.id}")
            unban = cur.fetchall()[0][0].split(".")
            if unban[0] != "p":
                if unban[0] != "n":
                    tim = time.ctime(time.time()).split()
                    if tim[1] == "January":
                        tim1 = 1
                    if tim[1] == "February":
                        tim1 = 2
                    if tim[1] == "March":
                        tim1 = 3
                    if tim[1] == "April":
                        tim1 = 4
                    if tim[1] == "May":
                        tim1 = 5
                    if tim[1] == "June":
                        tim1 = 6
                    if tim[1] == "Julie":
                        tim1 = 7
                    if tim[1] == "August":
                        tim1 = 8
                    if tim[1] == "September":
                        tim1 = 9
                    if tim[1] == "October":
                        tim1 = 10
                    if tim[1] == "November":
                        tim1 = 11
                    if tim[1] == "December":
                        tim1 = 12
                    if int(tim[4]) >= unban[2] and tim1 >= unban[1] and int(tim[2]) >= unban[0]:
                        bann = ((False,),)
                        cur.execute("UPDATE Users SET ban=?, unban=? WHERE id=?",
                                    (False, "n", message.chat.id))
                        conn.commit()
                else:
                    bann = ((False,),)
                    cur.execute("UPDATE Users SET ban=?, unban=? WHERE id=?",
                                (False, "n", message.chat.id))
                    conn.commit()
        if not asset[0][0] and not bann[0][0]:
            if message.chat.id <= 5400000000:
                bot.send_message(message.chat.id, "Запрос отправлен")
                g = telebot.types.InlineKeyboardMarkup()
                b1 = telebot.types.InlineKeyboardButton("Принять", callback_data=f"{message.chat.id} p")
                b2 = telebot.types.InlineKeyboardButton("Отказать", callback_data=f"{message.chat.id} o")
                g.add(b1, b2)
                msg = bot.send_message(idMessange, f"""Имя пользователя: {message.chat.first_name}
Id пользователя: {message.chat.id}
Ждет ответ на вопрос""", message_thread_id=3, reply_markup=g)
            else:
                if debug:
                    bot.send_message("id:", message.chat.id)
                ques = random.randint(1, 8)
                quiz(ques, idc=message.chat.id)
        elif asset[0][0] and not bann[0][0]:
            g = telebot.types.InlineKeyboardMarkup()
            b = telebot.types.InlineKeyboardButton("Ссылка-приглашение в группу.", URL)
            g.add(b)
            bot.send_message(message.chat.id, f"У вас есть доступ!", reply_markup=g)
        elif bann[0][0]:
            bot.send_message(message.chat.id, f"Вы забанены в данной группе")
    elif bot.get_chat_member(message.chat.id, message.from_user.id).status != "restricted":
        m = 0
        if len(message.text.split()) == 2:
            cur.execute("SELECT id FROM Users")
            n = cur.fetchall()
            for i in n:
                if int(message.text.split()[1]) == i[0]:
                    m = 1

            if m == 1:
                cur.execute(f"SELECT asset FROM Users WHERE id={int(message.text.split()[1])}")
                asset = cur.fetchall()
                if not asset:
                    cur.execute("UPDATE Users SET asset=? WHERE id=?", (True, message.from_user.id))
                    conn.commit()
                    bot.reply_to(message, "Заявка принята")
                else:
                    bot.reply_to(message, "Пользователь уже член группы")
            else:
                bot.reply_to(message, "Данного пользователя нет в базе данных")
        if debug:
            bot.send_message(message.from_user.id, f"typeServer: {typeServer}")
    typeServer = False


# locate
@bot.message_handler(commands=['locate'])
def locate(message):
    global mti, idMessange, typeServer
    if message.chat.id == idMessange:
        typeServer = True
    if (mti == 0 or (len(message.text.split()) == 2 and message.text.split()[1] == "clear")) and \
            bot.get_chat_member(message.chat.id, message.from_user.id).status != "restricted" and typeServer:
        idMessange = message.chat.id
        try:
            mti = message.reply_to_message.message_thread_id
        except:
            bot.send_message(idMessange, "Это основной чат")
        else:
            if debug:
                bot.send_message(idMessange, f"idMessange: {idMessange}, mti: {mti}", message_thread_id=mti)
    elif mti != 0 and typeServer:
        bot.send_message(idMessange, "Бот уже обнаружил чат и канал", message_thread_id=mti)
        if debug:
            bot.send_message(idMessange, f"idMessange: {idMessange}, mti: {mti}", message_thread_id=mti)
    elif not typeServer:
        bot.reply_to(message, "Команда не работает")
    typeServer = False


# ban Внимание пользователь должен пройти проверку бота, чтобы это работало!
@bot.message_handler(commands=['ban'])
def ban(message):
    if bot.get_chat_member(message.chat.id, message.from_user.id).status != "restricted":
        if len(message.text.split()) == 1 and bot.get_chat_member(message.chat.id,
                                                                  message.from_user.id).status != "restricted":
            if bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id) == "restricted":
                bot.send_message(idMessange, f"Пользователь с id: {message.reply_to_message.from_user.id} кикнут",
                                 message_thread_id=mti)
                cur.execute("UPDATE Users SET ban=?, unban=? WHERE id=?",
                            (True, "p", message.reply_to_message.from_user.id))
                conn.commit()
                bot.send_message(message.reply_to_message.from_user.id, f"Вы пермонентно забанены.",
                                 message_thread_id=mti)
            else:
                bot.send_message(idMessange, f"Надо отправить ответом на сообщение или он модератор, или выше стоящий. ",
                                 message_thread_id=mti)
        elif len(message.text.split()) == 2 and bot.get_chat_member(message.chat.id,
                                                                    message.from_user.id).status != "restricted":
            if bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id) == "restricted":
                bot.send_message(idMessange,
                                 f"Пользователь с id: {message.reply_to_message.from_user.id} кикнут до {message.text.split()[1]}",
                                 message_thread_id=mti)
                cur.execute("UPDATE Users SET ban=?, unban=? WHERE id=?",
                            (True, message.text.split()[1], message.reply_to_message.from_user.id))
                conn.commit()
                bot.send_message(message.reply_to_message.from_user.id, f"Вы забанены до {message.text.split()[1]}.")
            else:
                bot.send_message(idMessange, f"Надо отправить ответом на сообщение или он модератор или выше стоящий. ",
                                 message_thread_id=mti)
                if debug:
                    bot.send_message(idMessange, f"""Status: {bot.get_chat_member(message.chat.id,
                                                 message.from_user.id).status}""")
        bot.kick_chat_member(chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id)
    else:
        bot.send_message(idMessange, "Синтаксис: /ban {время}(не указав его пользователь будет \
                                     пермонентно забанен,\
                                      время надо указывать таким образом: 12.05.2025(Двенадцатое мая 2025 года))",
                         message_thread_id=mti)


# unban Внимание пользователь должен пройти проверку бота, чтобы это работало!
@bot.message_handler(commands=['unban'])
def unban(message):
    if bot.get_chat_member(message.chat.id, message.from_user.id).status != "restricted":
        cur.execute(f"SELECT ban FROM Users WHERE id={message.from_user.id}")
        ban = cur.fetchall()
        if bot.get_chat_member(message.chat.id, message.reply_to_message.from_user.id) == "restricted" and not ban:
            bot.send_message(idMessange,
                             f"Пользователь с id: {message.reply_to_message.from_user.id} разбанен",
                             message_thread_id=mti)
            cur.execute("UPDATE Users SET ban=?, unban=? WHERE id=?",
                        (False, "n", message.reply_to_message.from_user.id))
            conn.commit()
            bot.send_message(message.reply_to_message.from_user.id, "Вы разбанены.")
        else:
            bot.send_message(idMessange,
                             f"Надо отправить ответом на сообщение или он не забанен. ",
                             message_thread_id=mti)
        bot.kick_chat_member(chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id)
    else:
        bot.send_message(idMessange, "Синтаксис: /unban", message_thread_id=mti)


# quiz
def quiz(qus=0, call="", idc=0):
    global q, t
    if call == "yes":
        bot.send_message(idc, "Правильно!")
        t += 1
        q += 1
        ques = random.randint(1, 8)
        quiz(ques, idc=idc)
    elif call == "no":
        bot.send_message(idc, "Неправильно!")
        q += 1
        ques = random.randint(1, 8)
        quiz(ques, idc=idc)
    if qus == 1 and q != 5:
        g = telebot.types.InlineKeyboardMarkup()
        b1 = telebot.types.InlineKeyboardButton("Kingsong 15A", callback_data="no")
        b2 = telebot.types.InlineKeyboardButton("Inmotion V8", callback_data="yes")
        b3 = telebot.types.InlineKeyboardButton("Gotway ALF", callback_data="no")
        b4 = telebot.types.InlineKeyboardButton("Ninebot XL", callback_data="no")
        tq = [b1, b2, b3, b4]
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        bot.send_message(idc, "Самое популярное моноколесо 2017 года?", reply_markup=g)
    elif qus == 2 and q != 5:
        g = telebot.types.InlineKeyboardMarkup()
        b1 = telebot.types.InlineKeyboardButton("25 км/ч", callback_data="no")
        b2 = telebot.types.InlineKeyboardButton("35 км/ч", callback_data="yes")
        b3 = telebot.types.InlineKeyboardButton("30 км/ч", callback_data="no")
        b4 = telebot.types.InlineKeyboardButton("40 км/ч", callback_data="no")
        tq = [b1, b2, b3, b4]
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        bot.send_message(idc, "Какая максимальная скорость у Kingsong 16S?", reply_markup=g)
    elif qus == 3 and q != 5:
        g = telebot.types.InlineKeyboardMarkup()
        b1 = telebot.types.InlineKeyboardButton("Мопеду", callback_data="no")
        b2 = telebot.types.InlineKeyboardButton("Средству индивидуальной мобильности", callback_data="yes")
        b3 = telebot.types.InlineKeyboardButton("Мотоциклу", callback_data="no")
        b4 = telebot.types.InlineKeyboardButton("Спортивному снаряду", callback_data="no")
        tq = [b1, b2, b3, b4]
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        bot.send_message(idc, "Согласно ПДД РФ, моноколесо относится к:", reply_markup=g)
    elif qus == 4 and q != 5:
        g = telebot.types.InlineKeyboardMarkup()
        b1 = telebot.types.InlineKeyboardButton("Рогейн", callback_data="no")
        b2 = telebot.types.InlineKeyboardButton("Монокросс", callback_data="yes")
        b3 = telebot.types.InlineKeyboardButton("Мотокросс", callback_data="no")
        b4 = telebot.types.InlineKeyboardButton("ERacing", callback_data="no")
        tq = [b1, b2, b3, b4]
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        bot.send_message(idc, "Как называются гонки на моноколесах по пересечённой местности?", reply_markup=g)
    elif qus == 5 and q != 5:
        g = telebot.types.InlineKeyboardMarkup()
        b1 = telebot.types.InlineKeyboardButton("Кричать: \"Это баг, не фича!\"", callback_data="no")
        b2 = telebot.types.InlineKeyboardButton("Сбавить скорость", callback_data="yes")
        b3 = telebot.types.InlineKeyboardButton("Закрыть глаза и надеяться на подвеску", callback_data="no")
        b4 = telebot.types.InlineKeyboardButton("Позвонить маме", callback_data="no")
        tq = [b1, b2, b3, b4]
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        bot.send_message(idc, "Что делать, если вы заметили воблинг на скорости?", reply_markup=g)
    elif qus == 6 and q != 5:
        g = telebot.types.InlineKeyboardMarkup()
        b1 = telebot.types.InlineKeyboardButton("Надеть защиту", callback_data="no")
        b2 = telebot.types.InlineKeyboardButton("Смотреть видео на YouTube во время езды", callback_data="yes")
        b3 = telebot.types.InlineKeyboardButton("Уступать дорогу пешеходам", callback_data="no")
        b4 = telebot.types.InlineKeyboardButton("Проверить колесо перед выездом", callback_data="no")
        tq = [b1, b2, b3, b4]
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        bot.send_message(idc, "Что из этого не является правилом безопасного катания?", reply_markup=g)
    elif qus == 7 and q != 5:
        g = telebot.types.InlineKeyboardMarkup()
        b1 = telebot.types.InlineKeyboardButton("45 кг с подвеской, потому что круто", callback_data="no")
        b2 = telebot.types.InlineKeyboardButton("Inmotion V8", callback_data="yes")
        b3 = telebot.types.InlineKeyboardButton("Monster Pro на 134 вольта", callback_data="no")
        b4 = telebot.types.InlineKeyboardButton("Колесо обозрения", callback_data="no")
        tq = [b1, b2, b3, b4]
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        bot.send_message(idc, "Какое колесо лучше всего подходит для обучения?", reply_markup=g)
    elif qus == 8 and q != 5:
        g = telebot.types.InlineKeyboardMarkup()
        b1 = telebot.types.InlineKeyboardButton("В ближайший шиномонтаж — вдруг пригодится", callback_data="no")
        b2 = telebot.types.InlineKeyboardButton("В МоноВики (eucs.wiki)", callback_data="yes")
        b3 = telebot.types.InlineKeyboardButton("Оставить себе — знания должны быть тайной", callback_data="no")
        b4 = telebot.types.InlineKeyboardButton("Написать на стене в подъезде: \"Gotway был тут\"", callback_data="no")
        tq = [b1, b2, b3, b4]
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        rb = random.choice(tq)
        g.add(rb)
        tq.remove(rb)
        bot.send_message(idc, "Куда следует сообщить новую информацию о моноколёсах, если вы её обнаружили?",
                         reply_markup=g)
    elif q == 5 and t >= 3 and call == "":
        cur.execute(f"SELECT name FROM Users WHERE id={idc}")
        name = cur.fetchall()
        bot.send_message(idc, "Поздравляю! Вы прошли викторину! Запрос уже отправлен.")
        g = telebot.types.InlineKeyboardMarkup()
        b1 = telebot.types.InlineKeyboardButton("Принять", callback_data=f"{idc} p {name[0][0]}")
        b2 = telebot.types.InlineKeyboardButton("Отказать", callback_data=f"{idc} o")
        g.add(b1, b2)
        bot.send_message(idMessange, f"""Имя пользователя: {name[0][0]}
Id пользователя: {idc}
Ждет ответ на вопрос""", message_thread_id=3, reply_markup=g)
    elif q == 5 and t != q and call == "":
        bot.send_message(idc, "Увы. Вы непрошли викторину. Препройдите её.")
        if debug:
            bot.send_message(idc, f"Questions: {t}/{q}")


# Проверка на бан по сообщению. Внимание пользователь должен быть в базе данных, чтобы это работало!
@bot.message_handler()
def seek(message):
    global m, typeServer
    if message.chat.id == idMessange:
        typeServer = True
    if typeServer:
        cur.execute("SELECT id FROM Users")
        n = cur.fetchall()
        for i in n:
            if message.from_user.id == i[0]:
                m = 1
        if m == 1:
            cur.execute(f"SELECT ban FROM Users WHERE id={message.from_user.id}")
            ban = cur.fetchall()[0][0]
            if ban:
                bot.kick_chat_member(chat_id=idMessange, user_id=message.from_user.id)
                bot.send_message(message.from_user.id, "Попробуйте ввести сюда /asset если не сработает, то подождите если вас не забанили пермонентно")


bot.infinity_polling()
conn.close()
