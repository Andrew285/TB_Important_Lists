import telebot
from telebot import types
import psycopg2
from config import host, user, password, port, db_name
from psycopg2 import sql

#connection to exist database
connection = psycopg2.connect(
    host = host,
    user = user,
    password = password,
    database = db_name,
    port = port
)
connection.autocommit = True
cursor = connection.cursor()

imprt_bot = telebot.TeleBot("2135473258:AAFdtzE5w55BZE11b7SE5wMvL6o4RLE_JH0")

cursor.execute(
        """CREATE TABLE IF NOT EXISTS id_users(
            user_id integer PRIMARY KEY
        );"""
    )

cursor.execute(
        """CREATE TABLE IF NOT EXISTS lists(
            list_id serial PRIMARY KEY,
            list_name varchar(20) NOT NULL,
            fk_list_id integer REFERENCES id_users(user_id) NOT NULL
        );"""
    )

cursor.execute(
        """CREATE TABLE IF NOT EXISTS tasks(
            task_id serial PRIMARY KEY,
            task_name text NOT NULL,
            task_date varchar(20),
            task_priority integer,
            task_tag varchar(20),
            task_done varchar(10),
            fk_task_id integer REFERENCES lists(list_id) NOT NULL
        );"""
    )


@imprt_bot.message_handler(commands=['start'])
def main_choice_func(message):
    cursor.execute(f"SELECT user_id FROM id_users WHERE user_id = {message.chat.id};")
    data = cursor.fetchone()
    if data is None:
        cursor.execute(f"INSERT INTO id_users VALUES ({message.chat.id});")

    start_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    start_menu.add(types.KeyboardButton("Create List"),
                   types.KeyboardButton("Edit List"),
                   types.KeyboardButton("Remove List"),
                   types.KeyboardButton("Show List"),
                   types.KeyboardButton("Return"))
    msg = imprt_bot.send_message(message.chat.id, "Choose List Action:", reply_markup=start_menu)

    imprt_bot.register_next_step_handler(msg, choose_list_action)

def choose_list_action(message):
    if message.text == "Create List":
        list_name = imprt_bot.send_message(message.chat.id, "Enter the name of a new list:")
        imprt_bot.register_next_step_handler(list_name, task_func)
    elif message.text == "Show List":

        cursor.execute(
            "SELECT list_name FROM lists;"
        )
        list_name = []
        while True:
            row = cursor.fetchone()
            if row:
                list_name.append(row)
            else:
                break

        start_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for i in range(len(list_name)):
            start_menu.add(types.KeyboardButton(text=f"{list_name[i][0]}"))
        msg = imprt_bot.send_message(message.chat.id, "Choose List:", reply_markup=start_menu)
        imprt_bot.register_next_step_handler(msg, show_list)

def show_list(message):
    cursor.execute(
        "SELECT list_id FROM lists WHERE list_name = %s", (message.text,)
    )
    list_id = cursor.fetchone()

    cursor.execute(
        "SELECT * FROM tasks WHERE fk_task_id = %s", (list_id, )
    )
    task_list = []
    local_string = ""
    while True:
        row = cursor.fetchone()
        if row:
            task_list.append(row)
        else:
            break

    # local_string = "dfgsdfh"
    imprt_bot.send_message(message.chat.id, str(len(task_list)))
    imprt_bot.send_message(message.chat.id, task_list[0])
    for i in range(message.chat.id, len(task_list)):

        local_string += f"{i}. "
        for j in range(len(task_list[i])):
            local_string += f"{task_list[i][j]} | "
        # local_string += "\n"
    imprt_bot.send_message(message.chat.id, local_string)

def task_func(message):
    cursor.execute(
        "INSERT INTO lists (list_name, fk_list_id) VALUES (%s, %s)", (message.text, message.chat.id)
    )

    cursor.execute(
        f"SELECT list_id FROM lists WHERE fk_list_id = {message.chat.id};"
    )
    list_id = []
    while True:
        row = cursor.fetchone()
        if row:
            list_id.append(row)
        else:
            break
    current_list_id = list_id[-1][0]

    menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    menu.add(types.KeyboardButton("Add Task"),
             types.KeyboardButton("Edit Task"),
             types.KeyboardButton("Remove Task"),
             types.InlineKeyboardButton("Return"))
    task_choice = imprt_bot.send_message(message.chat.id, "Choose Task Action:", reply_markup=menu)
    imprt_bot.register_next_step_handler(task_choice, choose_task_action, current_list_id)

def choose_task_action(message, cur_list_id):
    if message.text == "Add Task":
        take_task = imprt_bot.send_message(message.chat.id, "Enter the task")
        imprt_bot.register_next_step_handler(take_task, add_task, cur_list_id)

    elif message.text == "Edit Task":
        pass

    elif message.text == "Remove Task":
        pass

    elif message.text == "Return":
        imprt_bot.register_next_step_handler(message, choose_list_action, cur_list_id)

def add_task(message, cur_list_id):

    imprt_bot.send_message(message.chat.id, cur_list_id)
    cursor.execute(
        "INSERT INTO tasks (task_name, fk_task_id) VALUES (%s, %s)", (message.text, cur_list_id)
    )

    imprt_bot.send_message(message.chat.id, "You have successfully add the task. Now choose the task action")

@imprt_bot.message_handler(content_types=['text'])
def echo_all(message):
    main_choice_func(message)


imprt_bot.infinity_polling()