import sqlite3  # Подключение библиотеки для работы с базами данных на основе SQLite
import telebot  # Подключение библиотеки для работы с телеграм ботами
import urllib.parse  # Подключение модуль для работы с URL
import requests  # Подключение библиотеки для работы с HTTP
import json

from telebot import types

bot = telebot.TeleBot(
    "6333177124:AAF77bnJwA1UYwX9cQUnsNdzVaddNhgrfGc")  # Создание телеграм бота, передача уникального токена бота, полученного у BotFather
conn = sqlite3.connect('db/database.db', check_same_thread=False)  # Подключение базы данных
cursor = conn.cursor()  # Создание курсора для работы с таблицами в базе данных
waiting_for_registrations = {}  # Глобальная переменная для хранения состояния ожидания ввода пароля для регистрации
waiting_for_login = {}  # Глобальная переменная для хранения состояния ожидания ввода пароля для аутентификации
user_states = {}
X_API_KEY = "ZDH5SYW-DZJM3DW-NQHZQE8-HSHTBJN"  # Ключ для работы с API Кинопоиска


# Функции, отрабатывающие при наборе 'привет' или 'start', используемые для начала рабоыт с ботом
@bot.message_handler(func=lambda
        message: message.text.lower() == 'привет' or message.text.lower() == 'start' or message.text.lower() == '/start')
def get_text_messages(message):
    text_hi = "Привет, я бот-помощник по выбору фильма. Я готов подсказать вам культовые и интересные фильмы, которые стоит посмотреть. Войдите в систему, чтобы сохранять понравившиеся фильмы."
    keyboard = types.InlineKeyboardMarkup()  # Создание клавиатуры
    key_login = types.InlineKeyboardButton(text='Войти', callback_data='login')  # Кнопка «Войти»
    keyboard.add(key_login)  # Добавление кнопки в клавиатуру
    bot.send_message(message.from_user.id, text=text_hi, reply_markup=keyboard)


# Функции, отрабатывающие при определенной callback_data
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "login":  # call.data это callback_data, которую мы указали при объявлении кнопки
        user_id = call.from_user.id
        cursor.execute('SELECT * FROM users WHERE id_user = ?',
                       (user_id,))  # Проверка наличия пользователя в базе данных
        user = cursor.fetchone()
        if user is not None:
            bot.send_message(user_id, 'Напишите пароль')
            waiting_for_login[user_id] = True
        else:
            bot.send_message(user_id, 'Давайте зарегистрируем Вас, придумайте и напишите пожалуйста пароль')
            waiting_for_registrations[user_id] = True
    elif call.data == "main":
        text_main = f"Здравствуйте, {call.from_user.first_name}, что Вы хотите сделать?"
        keyboard = types.InlineKeyboardMarkup()  # Создание клавиатуры
        key_list = types.InlineKeyboardButton(text='Избранное', callback_data='list')  # Кнопка «Избранное»
        keyboard.add(key_list)  # Добавление кнопки в клавиатуру
        key_name = types.InlineKeyboardButton(text='Поиск по названию',
                                              callback_data='name')  # Кнопка «Поиск по названию»
        keyboard.add(key_name)  # Добавление кнопки в клавиатуру
        key_genre = types.InlineKeyboardButton(text='Поиск по жанру', callback_data='genre')  # Кнопка «Поиск по жанру»
        keyboard.add(key_genre)  # Добавление кнопки в клавиатуру
        key_data = types.InlineKeyboardButton(text='Поиск по дате выхода',
                                              callback_data='data')  # Кнопка «Поиск по дате выхода»
        keyboard.add(key_data)  # Добавление кнопки в клавиатуру
        key_new = types.InlineKeyboardButton(text='Популярные фильмы',
                                             callback_data='best')  # Кнопка «Популярные фильмы»
        keyboard.add(key_new)  # Добавление кнопки в клавиатуру
        key_name = types.InlineKeyboardButton(text='Фильмы режиссера',
                                              callback_data='films_by_director')  # Кнопка «Поиск по названию»
        keyboard.add(key_name)  # Добавление кнопки в клавиатуру
        key_name = types.InlineKeyboardButton(text='Фильмы, в которых снялся актёр',
                                              callback_data='films_by_actor')  # Кнопка «Поиск по названию»
        keyboard.add(key_name)  # Добавление кнопки в клавиатуру
        bot.send_message(call.message.chat.id, text=text_main, reply_markup=keyboard)
    elif call.data == "list":
        text_list = f"Что Вы хотите сделать?"
        keyboard = types.InlineKeyboardMarkup()  # Создание клавиатуры
        key_check = types.InlineKeyboardButton(text='Просмотреть избранное',
                                               callback_data='check')  # Кнопка «Просмотреть избранное»
        keyboard.add(key_check)  # Добавление кнопки в клавиатуру
        key_add = types.InlineKeyboardButton(text='Добавить в избранное',
                                             callback_data='add')  # Кнопка «Добавить в избранное»
        keyboard.add(key_add)  # Добавление кнопки в клавиатуру
        key_edit = types.InlineKeyboardButton(text='Убрать фильм из избранного',
                                              callback_data='edit')  # Кнопка «Убрать фильм из избранного»
        keyboard.add(key_edit)  # Добавление кнопки в клавиатуру
        bot.send_message(call.message.chat.id, text=text_list, reply_markup=keyboard)
    elif call.data == "check":
        user_id = call.from_user.id
        cursor.execute("SELECT film_id FROM favorite WHERE user_id = ?", (user_id,))
        results = cursor.fetchall()
        film_ids = [result[0] for result in results]
        cnt = 1
        for i in film_ids:
            url = f"https://api.kinopoisk.dev/v1.4/movie/{i}"

            headers = {
                "accept": "application/json",
                "X-API-KEY": "80CPWV4-2N3MGYZ-GC6JRS5-JZTENT8"
            }

            response = requests.get(url, headers=headers)
            response_dict = json.loads(response.text)
            list_of_dicts = response_dict["genres"]
            values = [value for dict_item in list_of_dicts for value in dict_item.values()]
            values_str = ', '.join(values)
            text = f'{cnt}. Название: {response_dict["name"]} \nЖанр: {values_str} \nГод выхода: {response_dict["year"]} \nОписание: {response_dict["shortDescription"]}'
            bot.send_message(user_id, text)
            cnt += 1

        keyboard = types.InlineKeyboardMarkup()  # Создание клавиатуры
        key_add = types.InlineKeyboardButton(text='Добавить в избранное',
                                             callback_data='add')  # Кнопка «Добавить в избранное»
        keyboard.add(key_add)  # Добавление кнопки в клавиатуру
        key_edit = types.InlineKeyboardButton(text='Убрать фильм из избранного',
                                              callback_data='edit')  # Кнопка «Убрать фильм из избранного»
        keyboard.add(key_edit)  # Добавление кнопки в клавиатуру
        key_main = types.InlineKeyboardButton(text='Главное меню', callback_data='main')  # Кнопка «Главное меню»
        keyboard.add(key_main)  # Добавление кнопки в клавиатуру
        bot.send_message(call.message.chat.id, text="Что Вы хотите сделать?", reply_markup=keyboard)
    elif call.data == "edit":
        user_id = call.from_user.id
        bot.send_message(user_id, 'Напишите номер фильма, который вы хотите убрать из избранного')
        user_states[user_id] = "Waiting to edit"
    elif call.data == "add":
        user_id = call.from_user.id
        bot.send_message(user_id, 'Напишите название фильма, который вы хотите добавить в избранное')
        user_states[user_id] = "Waiting to add"
    elif call.data == "name":
        user_id = call.from_user.id
        bot.send_message(user_id, 'Напишите название фильма, который вы хотите найти')
        user_states[user_id] = "Waiting to find"
    elif call.data == "genre":
        user_id = call.from_user.id
        bot.send_message(user_id, 'Напишите жанр по которому вы хотите найти фильм')
        user_states[user_id] = "Waiting to genre"
    elif call.data == "data":
        user_id = call.from_user.id
        bot.send_message(user_id, 'Напишите год по которому вы хотите найти фильм')
        user_states[user_id] = "Waiting to data"
    elif call.data == "films_by_director":
        user_id = call.from_user.id
        bot.send_message(user_id, 'Напишите имя режиссера, фильмы котрого вы хотите узнать')
        user_states[user_id] = "Waiting for films by director"
    elif call.data == "films_by_actor":
        user_id = call.from_user.id
        bot.send_message(user_id, 'Напишите имя актера, интересующего вас')
        user_states[user_id] = "Waiting for films with actor"
    elif call.data == "best":
        user_id = call.from_user.id
        url = "https://api.kinopoisk.dev/v1.4/movie?page=1&limit=10&notNullFields=name&notNullFields=shortDescription&notNullFields=year&rating.kp=9-10"
        headers = {
            "accept": "application/json",
            "X-API-KEY": "80CPWV4-2N3MGYZ-GC6JRS5-JZTENT8"
        }

        response = requests.get(url, headers=headers)
        response_dict = json.loads(response.text)
        for i in range(10):
            list_of_dicts = response_dict["docs"][i]["genres"]
            values = [value for dict_item in list_of_dicts for value in dict_item.values()]
            values_str = ', '.join(values)
            text = f'Название: {response_dict["docs"][i]["name"]} \nЖанр: {values_str} \nГод выхода: {response_dict["docs"][i]["year"]} \nОписание: {response_dict["docs"][i]["shortDescription"]}'
            bot.send_message(call.from_user.id, text)
        keyboard = types.InlineKeyboardMarkup()  # Создание клавиатуры
        key_main = types.InlineKeyboardButton(text='Главное меню', callback_data='main')  # Кнопка «Главное меню»
        keyboard.add(key_main)  # Добавление кнопки в клавиатуру
        bot.send_message(call.from_user.id, text='Вот список из 10 популярных фильмов всех времен!',
                         reply_markup=keyboard)


# Обработчик регистрации
@bot.message_handler(func=lambda message: waiting_for_registrations.get(message.from_user.id))
def handle_password(message):
    user_id = message.from_user.id
    password = message.text
    cursor.execute('INSERT INTO users (id_user, user_name, password) VALUES (?, ?, ?)',
                   (user_id, message.from_user.first_name, password))  # Сохранение пароля в базе данных
    conn.commit()
    text_pass = "Пароль успешно сохранен!"
    keyboard = types.InlineKeyboardMarkup()  # Создание клавиатуры
    key_cont = types.InlineKeyboardButton(text='Продолжить', callback_data='main')  # Кнопка «Продолжить»
    keyboard.add(key_cont)  # Добавление кнопки в клавиатуру
    bot.send_message(message.chat.id, text=text_pass, reply_markup=keyboard)
    waiting_for_registrations.pop(user_id)


# Обработчик аутентификации
@bot.message_handler(func=lambda message: waiting_for_login.get(message.from_user.id))
def handle_password(message):
    user_id = message.from_user.id
    password = message.text
    cursor.execute('SELECT * FROM users WHERE id_user = ?', (user_id,))  # Проверка пароля
    user = cursor.fetchone()
    if user[3] == password:
        text_pass = "Вы успешно вошли!"
        keyboard = types.InlineKeyboardMarkup()  # Создание клавиатуры
        key_cont = types.InlineKeyboardButton(text='Продолжить', callback_data='main')  # Кнопка «Продолжить»
        keyboard.add(key_cont)  # Добавление кнопки в клавиатуру
        bot.send_message(message.chat.id, text=text_pass, reply_markup=keyboard)
        waiting_for_login.pop(user_id)
    else:
        text_pass_error = f"Неверный пароль"
        keyboard = types.InlineKeyboardMarkup()  # Создание клавиатуры
        key_cont = types.InlineKeyboardButton(text='Повторить попытку',
                                              callback_data='login')  # Кнопка «Повторить попытку»
        keyboard.add(key_cont)  # Добавление кнопки в клавиатуру
        bot.send_message(message.chat.id, text=text_pass_error, reply_markup=keyboard)
        waiting_for_login.pop(user_id)


# Обработчик редактирования избранного
@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == "Waiting to edit")
def edit_list(message):
    user_id = message.from_user.id
    film_number = int(message.text) - 1
    cursor.execute("SELECT film_id FROM favorite WHERE user_id = ?", (user_id,))
    results = cursor.fetchall()
    film_ids = [result[0] for result in results]
    if film_number < len(film_ids):
        film_id_to_delete = film_ids[film_number]
        delete_sql = "DELETE FROM favorite WHERE film_id = ? AND user_id = ?"
        cursor.execute(delete_sql, (film_id_to_delete, user_id))
        conn.commit()
        text_delete = "Фильм успешно удален!"
        keyboard = types.InlineKeyboardMarkup()  # Создание клавиатуры
        key_check = types.InlineKeyboardButton(text='Просмотреть избранное',
                                               callback_data='check')  # Кнопка «Просмотреть избранное»
        keyboard.add(key_check)  # Добавление кнопки в клавиатуру
        key_main = types.InlineKeyboardButton(text='Главное меню', callback_data='main')  # Кнопка «Главное меню»
        keyboard.add(key_main)  # Добавление кнопки в клавиатуру
        bot.send_message(message.chat.id, text=text_delete, reply_markup=keyboard)
        user_states.pop(user_id)
    else:
        text_delete_error = "Введен неправильный номер фильма"
        keyboard = types.InlineKeyboardMarkup()  # Создание клавиатуры
        key_check = types.InlineKeyboardButton(text='Просмотреть избранное',
                                               callback_data='check')  # Кнопка «Просмотреть избранное»
        keyboard.add(key_check)  # Добавление кнопки в клавиатуру
        key_main = types.InlineKeyboardButton(text='Главное меню', callback_data='main')  # Кнопка «Главное меню»
        keyboard.add(key_main)  # Добавление кнопки в клавиатуру
        bot.send_message(message.chat.id, text=text_delete_error, reply_markup=keyboard)
        user_states.pop(user_id)


# Обработчик поиска фильма по названию
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "Waiting to find")
def film_by_name(message):
    user_input = message.text
    encoded_string = urllib.parse.quote(user_input)
    url = f"https://api.kinopoisk.dev/v1.4/movie/search?page=1&limit=10&query={encoded_string}"
    headers = {
        "accept": "application/json",
        "X-API-KEY": "80CPWV4-2N3MGYZ-GC6JRS5-JZTENT8"
    }
    response = requests.get(url, headers=headers)
    response_dict = json.loads(response.text)
    print(response_dict)
    for i in range(10):
        list_of_dicts = response_dict["docs"][i]["genres"]
        values = [value for dict_item in list_of_dicts for value in dict_item.values()]
        values_str = ', '.join(values)
        text = f'Название: {response_dict["docs"][i]["name"]} \nЖанр: {values_str} \nГод выхода: {response_dict["docs"][i]["year"]} \nОписание: {response_dict["docs"][i]["shortDescription"]} \nОценка по Кинопоиске: {response_dict["docs"][i]["rating"]["kp"]}'
        bot.send_message(message.from_user.id, text)
    keyboard = types.InlineKeyboardMarkup()  # Создание клавиатуры
    key_main = types.InlineKeyboardButton(text='Главное меню', callback_data='main')  # Кнопка «Главное меню»
    keyboard.add(key_main)  # Добавление кнопки в клавиатуру
    bot.send_message(message.chat.id, text='Вот список из 10 фильмов с таким названием!', reply_markup=keyboard)
    user_states.pop(message.from_user.id)


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "Waiting to add")
def adding_film(message):
    user_input = message.text
    encoded_string = urllib.parse.quote(user_input)
    url = f"https://api.kinopoisk.dev/v1.4/movie/search?page=1&limit=1&query={encoded_string}"
    headers = {
        "accept": "application/json",
        "X-API-KEY": "80CPWV4-2N3MGYZ-GC6JRS5-JZTENT8"
    }
    response = requests.get(url, headers=headers)
    response_dict = json.loads(response.text)
    film_id = int(response_dict["docs"][0]["id"])
    cursor.execute('INSERT INTO favorite (user_id, film_id) VALUES (?, ?)',
                   (message.from_user.id, film_id))  # Заносим значения из аргументов функции в соответствующие столбцы
    conn.commit()
    text_add = "Фильм успешно добавлен!"
    keyboard = types.InlineKeyboardMarkup()  # Создание клавиатуры
    key_check = types.InlineKeyboardButton(text='Просмотреть избранное',
                                           callback_data='check')  # Кнопка «Просмотреть избранное»
    keyboard.add(key_check)  # Добавление кнопки в клавиатуру
    key_main = types.InlineKeyboardButton(text='Главное меню', callback_data='main')  # Кнопка «Главное меню»
    keyboard.add(key_main)  # Добавление кнопки в клавиатуру
    bot.send_message(message.chat.id, text=text_add, reply_markup=keyboard)
    user_states.pop(message.from_user.id)


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "Waiting to genre")
def searching_by_genre(message):
    user_input = message.text
    encoded_string = urllib.parse.quote(user_input)
    url = f"https://api.kinopoisk.dev/v1.4/movie?page=1&limit=10&selectFields=&genres.name={encoded_string}"

    headers = {
        "accept": "application/json",
        "X-API-KEY": "80CPWV4-2N3MGYZ-GC6JRS5-JZTENT8"
    }

    response = requests.get(url, headers=headers)
    response_dict = json.loads(response.text)
    for i in range(10):
        list_of_dicts = response_dict["docs"][i]["genres"]
        values = [value for dict_item in list_of_dicts for value in dict_item.values()]
        values_str = ', '.join(values)
        text = f'Название: {response_dict["docs"][i]["name"]} \nЖанр: {values_str} \nГод выхода: {response_dict["docs"][i]["year"]} \nОписание: {response_dict["docs"][i]["shortDescription"]}'
        bot.send_message(message.from_user.id, text)
    keyboard = types.InlineKeyboardMarkup()  # Создание клавиатуры
    key_main = types.InlineKeyboardButton(text='Главное меню', callback_data='main')  # Кнопка «Главное меню»
    keyboard.add(key_main)  # Добавление кнопки в клавиатуру
    bot.send_message(message.chat.id, text='Вот список из 10 популярных фильмов данного жанра!', reply_markup=keyboard)
    user_states.pop(message.from_user.id)


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "Waiting to data")
def searching_by_genre(message):
    user_input = message.text
    encoded_string = urllib.parse.quote(user_input)
    url = f"https://api.kinopoisk.dev/v1.4/movie?page=1&limit=10&year={encoded_string}"
    headers = {
        "accept": "application/json",
        "X-API-KEY": "80CPWV4-2N3MGYZ-GC6JRS5-JZTENT8"
    }

    response = requests.get(url, headers=headers)
    response_dict = json.loads(response.text)
    for i in range(10):
        list_of_dicts = response_dict["docs"][i]["genres"]
        values = [value for dict_item in list_of_dicts for value in dict_item.values()]
        values_str = ', '.join(values)
        text = f'Название: {response_dict["docs"][i]["name"]} \nЖанр: {values_str} \nГод выхода: {response_dict["docs"][i]["year"]} \nОписание: {response_dict["docs"][i]["shortDescription"]}'
        bot.send_message(message.from_user.id, text)
    keyboard = types.InlineKeyboardMarkup()  # Создание клавиатуры
    key_main = types.InlineKeyboardButton(text='Главное меню', callback_data='main')  # Кнопка «Главное меню»
    keyboard.add(key_main)  # Добавление кнопки в клавиатуру
    bot.send_message(message.chat.id, text='Вот список из 10 популярных фильмов данного года!', reply_markup=keyboard)
    user_states.pop(message.from_user.id)


# Обработчик поиска фильма по названию
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "Waiting for films by director")
def film_by_name(message):
    user_input = message.text
    encoded_string = urllib.parse.quote(user_input)
    url = f"https://api.kinopoisk.dev/v1.4/person/search?page=1&limit=30&query={encoded_string}"

    headers = {
        "accept": "application/json",
        "X-API-KEY": "80CPWV4-2N3MGYZ-GC6JRS5-JZTENT8"
    }
    response = requests.get(url, headers=headers)
    response_dict = json.loads(response.text)
    director_id = int(response_dict["docs"][0]["id"])
    url_1 = f"https://api.kinopoisk.dev/v1.4/person/{director_id}"
    response_1 = requests.get(url_1, headers=headers)
    response_dict_1 = json.loads(response_1.text)
    for i in range(30):
        if response_dict_1["movies"][i]["name"] is not None:
            name = f'Название: {response_dict_1["movies"][i]["name"]}'
        else:
            name = f'Название: {response_dict_1["movies"][i]["alternativeName"]}'
        if response_dict_1["movies"][i]["rating"] is not None:
            rate = f'Оценка по Кинопоиске: {response_dict_1["movies"][i]["rating"]}'
        else:
            rate = 'Фильм пока не оценивали на Кинопоиске :('
        text = f'{name}  \n{rate}'
        bot.send_message(message.from_user.id, text)
    keyboard = types.InlineKeyboardMarkup()  # Создание клавиатуры
    key_main = types.InlineKeyboardButton(text='Главное меню', callback_data='main')  # Кнопка «Главное меню»
    keyboard.add(key_main)  # Добавление кнопки в клавиатуру
    bot.send_message(message.chat.id, text='Вот список фильмов этого режиссера!', reply_markup=keyboard)
    user_states.pop(message.from_user.id)


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "Waiting for films with actor")
def film_by_name(message):
    user_input = message.text
    encoded_string = urllib.parse.quote(user_input)
    url = f"https://api.kinopoisk.dev/v1.4/person/search?page=1&limit=30&query={encoded_string}"

    headers = {
        "accept": "application/json",
        "X-API-KEY": "80CPWV4-2N3MGYZ-GC6JRS5-JZTENT8"
    }
    response = requests.get(url, headers=headers)
    response_dict = json.loads(response.text)
    actor_id = int(response_dict["docs"][0]["id"])
    url_1 = f"https://api.kinopoisk.dev/v1.4/person/{actor_id}"
    response_1 = requests.get(url_1, headers=headers)
    response_dict_1 = json.loads(response_1.text)

    for i in range(30):
        if response_dict_1["movies"][i]["name"] is not None:
            name = f'Название: {response_dict_1["movies"][i]["name"]}'
        else:
            name = f'Название: {response_dict_1["movies"][i]["alternativeName"]}'
        if response_dict_1["movies"][i]["rating"] is not None:
            rate = f'Оценка по Кинопоиске: {response_dict_1["movies"][i]["rating"]}'
        else:
            rate = 'Фильм пока не оценивали на Кинопоиске :('
        text = f'{name}  \n{rate}'
        bot.send_message(message.from_user.id, text)
    keyboard = types.InlineKeyboardMarkup()  # Создание клавиатуры
    key_main = types.InlineKeyboardButton(text='Главное меню', callback_data='main')  # Кнопка «Главное меню»
    keyboard.add(key_main)  # Добавление кнопки в клавиатуру
    bot.send_message(message.chat.id, text='Вот список фильмов с этим актёером!', reply_markup=keyboard)
    user_states.pop(message.from_user.id)


bot.polling(none_stop=True, interval=0)  # Запуск бота, чтобы он прослушивал события и отвечал на них
