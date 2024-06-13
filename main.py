import telegram
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes, ConversationHandler
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from PIL import Image
from io import BytesIO
import sqlite3
from datetime import datetime, date, time


classes = ['Робин Гуд', 'Мотор', 'Каролина', 'Капитаны', 'Гурмания-Давинчи']
genders = ['Женщина', 'Мужчина', 'Орк', 'орк']


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.message.chat_id
    print(user.name)

    con = sqlite3.connect("./resources/db.db")
    cur = con.cursor()
    cur.execute(f"INSERT INTO users(tg_username) VALUES('{user.name}')")
    con.commit()
    con.close()

    await update.message.reply_text('Здравствуй путник!\nЯ буду твоим путеводителем.\n'
                                    'Наши с тобой отношения строятся на честности, не подведи меня.\n'
                                    'Для начала представься')
    return 1


async def name_com(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    user = update.effective_user

    con = sqlite3.connect("./resources/db.db")
    cur = con.cursor()
    cur.execute(f"UPDATE users SET name = '{name}' WHERE tg_username = '{user.name}'")
    con.commit()
    con.close()

    reply_keyboard = [['Женщина', 'Мужчина']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    await update.message.reply_text(f'Так, {name} говоришь?\nХорошо записал\nКто ты?', reply_markup=markup)
    return 2


async def gender_com(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global genders
    gender = update.message.text
    user = update.effective_user

    if gender in genders:
        con = sqlite3.connect("./resources/db.db")
        cur = con.cursor()
        cur.execute(f"UPDATE users SET gender = '{gender}' WHERE tg_username = '{user.name}'")
        reply_keyboard = [['Робин Гуд'],
                          ['Мотор'],
                          ['Каролина'],
                          ['Капитаны'],
                          ['Гурмания-Давинчи']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

        if gender.capitalize() == 'Орк':
            db_user = cur.execute(f"SELECT * FROM users WHERE tg_username = '{user.name}'").fetchone()
            new = db_user[10]
            new = new[:5] + 't'
            cur.execute(f"UPDATE users SET achievements = '{new}' WHERE tg_username = '{user.name}'")
            con.commit()
            con.close()
            await context.bot.send_photo(update.message.chat_id, './resources/ork.png',
                                         caption='Хо-хо-хо\nОрк значит))\nА теперь выберете ваш класс', reply_markup=markup)
            return 3
        else:
            con.commit()
            con.close()
            await update.message.reply_text(f'Есть!\nА теперь выберете ваш класс',
                                            reply_markup=markup)
            return 3
    else:
        reply_keyboard = [['Женщина', 'Мужчина']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

        await update.message.reply_text(f'Ты что такое... Давай заново',
                                        reply_markup=markup)
        return 2


async def class_com(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global classes
    class_wow = update.message.text
    user = update.effective_user

    if class_wow in classes:
        con = sqlite3.connect("./resources/db.db")
        cur = con.cursor()
        cur.execute(f"UPDATE users SET class = '{class_wow}' WHERE tg_username = '{user.name}'")
        con.commit()
        con.close()

        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

        await update.message.reply_text(f'Интересно...\nВаш напарник создал группу?',
                                        reply_markup=markup)
        return 4
    else:
        reply_keyboard = [['Робин Гуд'],
                          ['Мотор'],
                          ['Каролина'],
                          ['Капитаны'],
                          ['Гурмания-Давинчи']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

        await update.message.reply_text(f'Нормально выбери класс >:|',
                                        reply_markup=markup)
        return 3


async def group_com(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = update.message.text
    if response == 'Да':
        await update.message.reply_text(f'Это хорошо, узнай у напарника id группы и вводи сюда', reply_markup=ReplyKeyboardRemove())
        return 6
    elif response == 'Нет':
        await update.message.reply_text(f'Тогда давайте создадим.\nПридумай название для группы', reply_markup=ReplyKeyboardRemove())
        return 5
    else:
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f'чаво, ответь нормально', reply_markup=markup)
        return 4


async def make_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_name = update.message.text
    user = update.effective_user

    con = sqlite3.connect("./resources/db.db")
    cur = con.cursor()
    cur.execute(f"INSERT INTO groups(name) VALUES('{group_name}')")
    gr_id = cur.execute(f"SELECT * FROM groups WHERE name = '{group_name}'").fetchone()
    cur.execute(f"UPDATE users SET group_id = {gr_id[0]} WHERE tg_username = '{user.name}'")
    con.commit()
    con.close()
    reply_keyboard = [['Профиль'],
                      ['Проверка ежедневных заданий'],
                      ['Использовать токен'],
                      ['Квесты', 'Ачивки']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

    await update.message.reply_text(f'Готово, регистрация закончена!\nТвоя группа: {gr_id[1]}\nID группы: {gr_id[0]}', reply_markup=markup)
    return ConversationHandler.END


async def find_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_id = update.message.text
    user = update.effective_user

    con = sqlite3.connect("./resources/db.db")
    cur = con.cursor()
    gr = cur.execute(f"SELECT * FROM groups WHERE id = {group_id}").fetchone()
    cur.execute(f"UPDATE users SET group_id = {group_id} WHERE tg_username = '{user.name}'")
    con.commit()
    con.close()
    reply_keyboard = [['Профиль'],
                      ['Проверка ежедневных заданий'],
                      ['Использовать токен'],
                      ['Квесты', 'Ачивки']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

    await update.message.reply_text(f'Готово, регистрация закончена!\nТвоя группа: {gr[1]}', reply_markup=markup)
    return ConversationHandler.END


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return ConversationHandler.END


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    con = sqlite3.connect("./resources/db.db")
    cur = con.cursor()
    db_user = cur.execute(f"SELECT * FROM users WHERE tg_username = '{user.name}'").fetchone()
    gr = cur.execute(f"SELECT * FROM groups WHERE id = {db_user[3]}").fetchone()
    con.close()

    chat_id = update.message.chat_id

    image = Image.open('./resources/bg.png')
    player_png = Image.open(f'./resources/classes/{db_user[7]}/{db_user[6].capitalize()}/player.png')
    image.paste(player_png, (451, 486), player_png)

    bio = BytesIO()
    bio.name = 'image.PNG'
    image.save(bio, 'PNG')
    bio.seek(0)
    lvl, exp = lvl_exp(db_user[5])

    reply_keyboard = [['Профиль'],
                      ['Проверка ежедневных заданий'],
                      ['Использовать токен'],
                      ['Квесты', 'Ачивки']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

    await context.bot.send_photo(chat_id, bio,
                                 caption=f'Имя: {db_user[1]}\n'
                                         f'Группа: {gr[1]}\n'
                                         f'Уровень: {db_user[4]}\n'
                                         f'Токенов на ништяки: {db_user[15]}\n'
                                         f'Опыт: {exp}\n', reply_markup=markup)


async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    f = open("./resources/day.txt", "r")
    dt_str = f.read()
    f.close()
    dt = datetime.strptime(dt_str, "%d/%m/%Y")
    if datetime.today().date() > dt.date():
        con = sqlite3.connect("./resources/db.db")
        cur = con.cursor()
        every = cur.execute(f"SELECT * FROM users").fetchall()
        for j in range(len(every)):
            cur.execute(f"UPDATE users SET daily_was = 'f' WHERE id = {every[j][0]}")
        con.commit()
        con.close()

        f = open("./resources/day.txt", "w")
        f.write(datetime.today().strftime("%d/%m/%Y"))
        f.close()
        print('yeah')

    con = sqlite3.connect("./resources/db.db")
    cur = con.cursor()
    db_user = cur.execute(f"SELECT * FROM users WHERE tg_username = '{user.name}'").fetchone()

    if db_user[9] == 'f':
        cur.execute(f"UPDATE users SET daily_was = 't' WHERE tg_username = '{user.name}'")
        con.commit()
        con.close()

        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f'Ты поднял детей сегодня?', reply_markup=markup)
        return 1
    else:
        reply_keyboard = [['Профиль'],
                          ['Проверка ежедневных заданий'],
                          ['Использовать токен'],
                          ['Квесты', 'Ачивки']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        await update.message.reply_text(f'Вы уже сегодня делали проверку', reply_markup=markup)
        con.close()
        return ConversationHandler.END


async def first_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = update.message.text
    user = update.effective_user

    if response == 'Да':
        context.user_data['daily'] = 't'
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f'Ты сходил на зарядку?', reply_markup=markup)
        return 2
    elif response == 'Нет':
        context.user_data['daily'] = 'f'
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f'Ты сходил на зарядку?', reply_markup=markup)
        return 2
    else:
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f'Ты поднял детей сегодня?', reply_markup=markup)
        return 1


async def second_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = update.message.text
    user = update.effective_user

    if response == 'Да':
        context.user_data['daily'] += 't'
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f'Ты отвел на допы?', reply_markup=markup)
        return 3
    elif response == 'Нет':
        context.user_data['daily'] += 'f'
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f'Ты отвел на допы?', reply_markup=markup)
        return 3
    else:
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f'Ты сходил на зарядку?', reply_markup=markup)
        return 2


async def third_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = update.message.text
    user = update.effective_user

    if response == 'Да':
        context.user_data['daily'] += 't'
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f'Ты организовал обзвон?', reply_markup=markup)
        return 4
    elif response == 'Нет':
        context.user_data['daily'] += 'f'
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f'Ты организовал обзвон?', reply_markup=markup)
        return 4
    else:
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f'Ты отвел на допы?', reply_markup=markup)
        return 3


async def fourth_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = update.message.text
    user = update.effective_user

    if response == 'Да':
        context.user_data['daily'] += 't'
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f'Ты поиграл с детьми?', reply_markup=markup)
        return 5
    elif response == 'Нет':
        context.user_data['daily'] += 'f'
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f'Ты поиграл с детьми?', reply_markup=markup)
        return 5
    else:
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f'Ты организовал обзвон?', reply_markup=markup)
        return 4


async def fifth_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = update.message.text
    user = update.effective_user

    if response == 'Да':
        context.user_data['daily'] += 't'
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f'Ты уложил спать детей?', reply_markup=markup)
        return 6
    elif response == 'Нет':
        context.user_data['daily'] += 'f'
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f'Ты уложил спать детей?', reply_markup=markup)
        return 6
    else:
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f'Ты поиграл с детьми?', reply_markup=markup)
        return 5


async def sixth_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = update.message.text
    user = update.effective_user

    if response == 'Да':
        context.user_data['daily'] += 't'
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f'Ты сходил на планерку?', reply_markup=markup)
        return 7
    elif response == 'Нет':
        context.user_data['daily'] += 'f'
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f'Ты сходил на планерку?', reply_markup=markup)
        return 7
    else:
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f'Ты сходил на планерку?', reply_markup=markup)
        return 6


async def seventh_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = update.message.text
    user = update.effective_user
    chat_id = update.message.chat_id

    if response == 'Да':
        context.user_data['daily'] += 't'
        reply_keyboard = [['Профиль'],
                          ['Проверка ежедневных заданий'],
                          ['Использовать токен'],
                          ['Квесты', 'Ачивки']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

        con = sqlite3.connect("./resources/db.db")
        cur = con.cursor()
        db_user = cur.execute(f"SELECT * FROM users WHERE tg_username = '{user.name}'").fetchone()
        new_daily = ''
        for i in range(len(db_user[8])):
            if db_user[8][i] == 't' or context.user_data['daily'][i] == 't':
                new_daily += 't'
            else:
                new_daily += 'f'
        print(new_daily)
        context.user_data.clear()
        if new_daily == 'ttttttt':
            cur.execute(f"UPDATE users SET daily = 'fffffff' WHERE tg_username = '{user.name}'")
            lvl, exp = lvl_exp(db_user[5] + 100)
            cur.execute(f"UPDATE users SET exp = {db_user[5] + 100} WHERE tg_username = '{user.name}'")
            cur.execute(f"UPDATE users SET tokens = {db_user[15] + (lvl - db_user[4])} WHERE tg_username = '{user.name}'")
            cur.execute(f"UPDATE users SET level = {lvl} WHERE tg_username = '{user.name}'")
            if db_user[11] >= 4 and db_user[10][0] == 'f':
                new = db_user[10]
                new = 't' + new[1:]
                cur.execute(f"UPDATE users SET achievements = '{new}' WHERE tg_username = '{user.name}'")
                cur.execute(f"UPDATE users SET number_daily = {db_user[11] + 1} WHERE tg_username = '{user.name}'")
                con.commit()
                con.close()
                await context.bot.send_photo(chat_id, './resources/trud.png',
                                             caption='Проверка выполнена, вы заработали 100 опыта!', reply_markup=markup)
                return ConversationHandler.END
            else:
                cur.execute(f"UPDATE users SET number_daily = {db_user[11] + 1} WHERE tg_username = '{user.name}'")
                con.commit()
                con.close()
                await update.message.reply_text(f'Проверка выполнена, вы заработали 100 опыта!', reply_markup=markup)
                return ConversationHandler.END
        else:
            cur.execute(f"UPDATE users SET daily = '{new_daily}' WHERE tg_username = '{user.name}'")
            con.commit()
            con.close()
            await update.message.reply_text(f'Проверка выполнена', reply_markup=markup)
            return ConversationHandler.END
    elif response == 'Нет':
        context.user_data['daily'] += 'f'
        reply_keyboard = [['Профиль'],
                          ['Проверка ежедневных заданий'],
                          ['Использовать токен'],
                          ['Квесты', 'Ачивки']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

        con = sqlite3.connect("./resources/db.db")
        cur = con.cursor()
        db_user = cur.execute(f"SELECT * FROM users WHERE tg_username = '{user.name}'").fetchone()
        new_daily = ''
        for i in range(len(db_user[8])):
            if db_user[8][i] == 't' or context.user_data['daily'][i] == 't':
                new_daily += 't'
            else:
                new_daily += 'f'
        print(new_daily)
        context.user_data.clear()
        if new_daily == 'ttttttt':
            cur.execute(f"UPDATE users SET daily = 'fffffff' WHERE tg_username = '{user.name}'")
            lvl, exp = lvl_exp(db_user[5] + 100)
            cur.execute(f"UPDATE users SET exp = {db_user[5] + 100} WHERE tg_username = '{user.name}'")
            cur.execute(
                f"UPDATE users SET tokens = {db_user[15] + (lvl - db_user[4])} WHERE tg_username = '{user.name}'")
            cur.execute(f"UPDATE users SET level = {lvl} WHERE tg_username = '{user.name}'")
            if db_user[11] >= 4 and db_user[10][0] == 'f':
                new = db_user[10]
                new = 't' + new[1:]
                cur.execute(f"UPDATE users SET achievements = '{new}' WHERE tg_username = '{user.name}'")
                cur.execute(f"UPDATE users SET number_daily = {db_user[11] + 1} WHERE tg_username = '{user.name}'")
                con.commit()
                con.close()
                await context.bot.send_photo(chat_id, './resources/trud.png',
                                             caption='Проверка выполнена, вы заработали 100 опыта!',
                                             reply_markup=markup)
            else:
                con.commit()
                con.close()
                await update.message.reply_text(f'Проверка выполнена, вы заработали 100 опыта!', reply_markup=markup)
                return ConversationHandler.END
        else:
            cur.execute(f"UPDATE users SET daily = '{new_daily}' WHERE tg_username = '{user.name}'")
            con.commit()
            con.close()
            await update.message.reply_text(f'Проверка выполнена', reply_markup=markup)
            return ConversationHandler.END
    else:
        reply_keyboard = [['Да', 'Нет']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        await update.message.reply_text(f'Ты сходил на планерку?', reply_markup=markup)
        return 7


def lvl_exp(exp):
    if exp >= 4560:
        return [10, exp - 4650]
    elif exp >= 3850:
        return [9, exp - 3850]
    elif exp >= 3100:
        return [8, exp - 3100]
    elif exp >= 2400:
        return [7, exp - 2400]
    elif exp >= 1750:
        return [6, exp - 1750]
    elif exp >= 1150:
        return [5, exp - 1150]
    elif exp >= 650:
        return [4, exp - 650]
    elif exp >= 300:
        return [3, exp - 300]
    elif exp >= 100:
        return [2, exp - 100]
    else:
        return [1, exp]


async def visitka_svecha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.message.chat_id
    reply_keyboard = [['Профиль'],
                      ['Проверка ежедневных заданий'],
                      ['Использовать токен'],
                      ['Квесты', 'Ачивки']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

    con = sqlite3.connect("./resources/db.db")
    cur = con.cursor()
    db_user = cur.execute(f"SELECT * FROM users WHERE tg_username = '{user.name}'").fetchone()
    lvl, exp = lvl_exp(db_user[5] + 150)
    cur.execute(f"UPDATE users SET exp = {db_user[5] + 150} WHERE tg_username = '{user.name}'")
    cur.execute(f"UPDATE users SET tokens = {db_user[15] + (lvl - db_user[4])} WHERE tg_username = '{user.name}'")
    cur.execute(f"UPDATE users SET level = {lvl} WHERE tg_username = '{user.name}'")
    if update.message.text == 'Тематическая свечка' and db_user[12] >= 2 and db_user[10][1] == 'f':
        new = db_user[10]
        new = new[:1] + 't' + new[2:]
        cur.execute(f"UPDATE users SET achievements = '{new}' WHERE tg_username = '{user.name}'")
        cur.execute(f"UPDATE users SET svecha = {db_user[12] + 1} WHERE tg_username = '{user.name}'")
        con.commit()
        con.close()
        await context.bot.send_photo(chat_id, './resources/svecha.png',
                                     caption='Вы заработали 150 опыта!', reply_markup=markup)
    elif update.message.text == 'Тематическая свечка':
        cur.execute(f"UPDATE users SET svecha = {db_user[12] + 1} WHERE tg_username = '{user.name}'")
        con.commit()
        con.close()

        await update.message.reply_text('Вы заработали 150 опыта!', reply_markup=markup)

    if update.message.text == 'Подготовка визитки' and db_user[13] == 1 and db_user[10][2] == 'f':
        new = db_user[10]
        new = new[:2] + 't' + new[3:]
        cur.execute(f"UPDATE users SET achievements = '{new}' WHERE tg_username = '{user.name}'")
        cur.execute(f"UPDATE users SET visit = 1 WHERE tg_username = '{user.name}'")
        con.commit()
        con.close()
        await context.bot.send_photo(chat_id, './resources/svecha.png',
                                     caption='Вы заработали 150 опыта!', reply_markup=markup)
    elif update.message.text == 'Подготовка визитки':
        cur.execute(f"UPDATE users SET visit = 1 WHERE tg_username = '{user.name}'")
        con.commit()
        con.close()

        await update.message.reply_text('Вы заработали 150 опыта!', reply_markup=markup)


async def dance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.message.chat_id
    reply_keyboard = [['Профиль'],
                      ['Проверка ежедневных заданий'],
                      ['Использовать токен'],
                      ['Квесты', 'Ачивки']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

    con = sqlite3.connect("./resources/db.db")
    cur = con.cursor()
    db_user = cur.execute(f"SELECT * FROM users WHERE tg_username = '{user.name}'").fetchone()
    lvl, exp = lvl_exp(db_user[5] + 200)
    cur.execute(f"UPDATE users SET exp = {db_user[5] + 200} WHERE tg_username = '{user.name}'")
    cur.execute(f"UPDATE users SET tokens = {db_user[15] + (lvl - db_user[4])} WHERE tg_username = '{user.name}'")
    cur.execute(f"UPDATE users SET level = {lvl} WHERE tg_username = '{user.name}'")

    if update.message.text == 'Выступление на любом из концертов' and db_user[14] == 1 and db_user[10][2] == 'f':
        new = db_user[10]
        new = new[:2] + 't' + new[3:]
        cur.execute(f"UPDATE users SET achievements = '{new}' WHERE tg_username = '{user.name}'")
        cur.execute(f"UPDATE users SET scene = 1 WHERE tg_username = '{user.name}'")
        con.commit()
        con.close()
        await context.bot.send_photo(chat_id, './resources/svecha.png',
                                     caption='Вы заработали 200 опыта!', reply_markup=markup)
    elif update.message.text == 'Подготовка визитки':
        cur.execute(f"UPDATE users SET scene = 1 WHERE tg_username = '{user.name}'")
        con.commit()
        con.close()

        await update.message.reply_text('Вы заработали 200 опыта!', reply_markup=markup)
    else:
        con.commit()
        con.close()
        await update.message.reply_text('Вы заработали 200 опыта!', reply_markup=markup)


async def token_com(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    reply_keyboard = [['Профиль'],
                      ['Проверка ежедневных заданий'],
                      ['Использовать токен'],
                      ['Квесты', 'Ачивки']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

    f = open("./resources/day.txt", "r")
    dt_str = f.read()
    f.close()
    dt = datetime.strptime(dt_str, "%d/%m/%Y")
    if datetime.today().date() > dt.date():
        con = sqlite3.connect("./resources/db.db")
        cur = con.cursor()
        every = cur.execute(f"SELECT * FROM users").fetchall()
        for j in range(len(every)):
            cur.execute(f"UPDATE users SET token_used = 0 WHERE id = {every[j][0]}")
        con.commit()
        con.close()

        f = open("./resources/day.txt", "w")
        f.write(datetime.today().strftime("%d/%m/%Y"))
        f.close()
        print('yeah')

    con = sqlite3.connect("./resources/db.db")
    cur = con.cursor()
    db_user = cur.execute(f"SELECT * FROM users WHERE tg_username = '{user.name}'").fetchone()
    pairs = cur.execute(f"SELECT * FROM users WHERE group_id = {db_user[3]}").fetchall()
    chk = True
    for was in pairs:
        if was[16] == 1:
            chk = False
    if chk and db_user[15] > 0:
        cur.execute(f"UPDATE users SET tokens = {db_user[15] - 1} WHERE tg_username = '{user.name}'")
        cur.execute(f"UPDATE users SET token_used = 1 WHERE tg_username = '{user.name}'")
        con.commit()
        con.close()
        await update.message.reply_text('Вы использовали ваш токен! Отдыхайте!', reply_markup=markup)
    else:
        con.commit()
        con.close()
        await update.message.reply_text('Вы не можете использовать токен :(', reply_markup=markup)


async def boss(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat_id = update.message.chat_id
    reply_keyboard = [['Профиль'],
                      ['Проверка ежедневных заданий'],
                      ['Использовать токен'],
                      ['Квесты', 'Ачивки']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

    con = sqlite3.connect("./resources/db.db")
    cur = con.cursor()
    db_user = cur.execute(f"SELECT * FROM users WHERE tg_username = '{user.name}'").fetchone()
    lvl, exp = lvl_exp(db_user[5] + 500)
    cur.execute(f"UPDATE users SET exp = {db_user[5] + 500} WHERE tg_username = '{user.name}'")
    cur.execute(f"UPDATE users SET tokens = {db_user[15] + (lvl - db_user[4])} WHERE tg_username = '{user.name}'")
    cur.execute(f"UPDATE users SET level = {lvl} WHERE tg_username = '{user.name}'")
    if db_user[10][4] == 'f':
        new = db_user[10]
        new = new[:4] + 't' + new[5:]
        cur.execute(f"UPDATE users SET achievements = '{new}' WHERE tg_username = '{user.name}'")
        con.commit()
        con.close()
        await context.bot.send_photo(chat_id, './resources/boss.png',
                                     caption='Вы заработали 500 опыта!', reply_markup=markup)
    else:
        con.commit()
        con.close()
        await update.message.reply_text('Вы заработали 500 опыта!', reply_markup=markup)


async def help_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    await update.message.reply_text('Я rpgbot для лагеря, сделанный чувачком)')


async def main_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    reply_keyboard = [['Профиль'],
                      ['Проверка ежедневных заданий'],
                      ['Использовать токен'],
                      ['Квесты', 'Ачивки']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.message.reply_text('Возвращаю обратно...', reply_markup=markup)


async def quests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    reply_keyboard = [['Подготовка визитки'],
                      ['Тематическая свечка'],
                      ['Выступление на любом из концертов'],
                      ['Придумать флешмоб'],
                      ['БОСС: Разнять драку и успокоить детей'],
                      ['БОСС: Поговорить с конфликтным родителем и урегулировать конфликт'],
                      ['БОСС: Оветить за свой косяк на планёрке'],
                      ['Главная страница']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.message.reply_text('Здесь ты можешь выбрать те квесты, которые выполнил\n'
                                    'Если ничего из этого ты не сделал, можешь вернуться на главную страницу', reply_markup=markup)


async def achievement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user = update.effective_user

    con = sqlite3.connect("./resources/db.db")
    cur = con.cursor()
    db_user = cur.execute(f"SELECT * FROM users WHERE tg_username = '{user.name}'").fetchone()
    con.close()
    all_achievements = ['Трудяга', 'Озаритель', 'Тамада', 'Выживший', 'ВедьМук я столько пережил', 'ОРК']

    for num in range(len(db_user[10])):
        if db_user[10][num] == 'f':
            all_achievements[num] = '???'

    reply_keyboard = [['Профиль'],
                      ['Проверка ежедневных заданий'],
                      ['Использовать токен'],
                      ['Квесты', 'Ачивки']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    await update.message.reply_text(f'Твои ачивки:\n'
                                    f'1: {all_achievements[0]}\n'
                                    f'2: {all_achievements[1]}\n'
                                    f'3: {all_achievements[2]}\n'
                                    f'4: {all_achievements[3]}\n'
                                    f'5: {all_achievements[4]}\n'
                                    f'6: {all_achievements[5]}',
                                    reply_markup=markup)


def main():
    application = Application.builder().token('6463784741:AAEfxTuQ5kbB0zsW73f9OQS_PqglBVNcpnM').build()

    start_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={1: [MessageHandler(filters.TEXT & ~filters.COMMAND, name_com)],
                2: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender_com)],
                3: [MessageHandler(filters.TEXT & ~filters.COMMAND, class_com)],
                4: [MessageHandler(filters.TEXT & ~filters.COMMAND, group_com)],
                5: [MessageHandler(filters.TEXT & ~filters.COMMAND, make_group)],
                6: [MessageHandler(filters.TEXT & ~filters.COMMAND, find_group)]},
        fallbacks=[CommandHandler('252352346345563735736', stop)]
    )

    daily_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^Проверка ежедневных заданий$'), daily)],
        states={1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_response)],
                2: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_response)],
                3: [MessageHandler(filters.TEXT & ~filters.COMMAND, third_response)],
                4: [MessageHandler(filters.TEXT & ~filters.COMMAND, fourth_response)],
                5: [MessageHandler(filters.TEXT & ~filters.COMMAND, fifth_response)],
                6: [MessageHandler(filters.TEXT & ~filters.COMMAND, sixth_response)],
                7: [MessageHandler(filters.TEXT & ~filters.COMMAND, seventh_response)]},
        fallbacks=[CommandHandler('252352346345563735736', stop)]
    )

    application.add_handler(start_handler)
    application.add_handler(CommandHandler('help', help_func))
    application.add_handler(MessageHandler(filters.Regex('^Профиль$'), profile))
    application.add_handler(MessageHandler(filters.Regex('^Главная страница$'), main_page))
    application.add_handler(MessageHandler(filters.Regex('^Квесты$'), quests))
    application.add_handler(MessageHandler(filters.Regex('^Ачивки$'), achievement))
    application.add_handler(MessageHandler(filters.Regex('^Использовать токен$'), token_com))
    application.add_handler(MessageHandler(filters.Regex('^Подготовка визитки|Тематическая свечка$'), visitka_svecha))
    application.add_handler(
        MessageHandler(filters.Regex('^Выступление на любом из концертов|Придумать флешмоб$'), dance))
    application.add_handler(
        MessageHandler(filters.Regex('^БОСС: Разнять драку и успокоить детей|'
                                     'БОСС: Оветить за свой косяк на планёрке|'
                                     'БОСС: Поговорить с конфликтным родителем и урегулировать конфликт$'), boss))
    application.add_handler(daily_handler)

    application.run_polling()


if __name__ == '__main__':
    print('Work!')
    main()
