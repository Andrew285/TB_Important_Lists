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

edited_list_id = 0
removed_task = ""
removed_list = ""

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
    cursor.execute("SELECT user_id FROM id_users WHERE user_id = %s", (message.chat.id, ))
    data = cursor.fetchone()
    if data is None:
        cursor.execute("INSERT INTO id_users VALUES (%s)", (message.chat.id, ))

    start_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    start_menu.add(types.KeyboardButton("Create List"),
                   types.KeyboardButton("Edit List"),
                   types.KeyboardButton("Remove List"),
                   types.KeyboardButton("Show List"))
    msg = imprt_bot.send_message(message.chat.id, "Choose List Action:", reply_markup=start_menu)

    imprt_bot.register_next_step_handler(msg, choose_list_action)

def choose_list_action(message):
    if message.text == "Create List":
        list_name = imprt_bot.send_message(message.chat.id, "Enter the name of a new list:")
        imprt_bot.register_next_step_handler(list_name, task_func)
    elif message.text == "Show List":

        cursor.execute(
            "SELECT list_name FROM lists WHERE fk_list_id = %s", (message.chat.id,)
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

    elif message.text == "Edit List":
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
        imprt_bot.register_next_step_handler(msg, edit_list)

    elif message.text == "Remove List":
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
        imprt_bot.register_next_step_handler(msg, remove_list)

def edit_list(message):
    global edited_list_id
    cursor.execute(
        "SELECT list_id FROM lists WHERE list_name = %s", (message.text,)
    )
    edited_list_id = cursor.fetchone()
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    menu.add(types.KeyboardButton("Edit List Name"),
             types.KeyboardButton("Add Task"),
             types.KeyboardButton("Edit Task"),
             types.KeyboardButton("Remove Task"),
             types.InlineKeyboardButton("Return"))
    task_choice = imprt_bot.send_message(message.chat.id, "Choose Task Action:", reply_markup=menu)
    imprt_bot.register_next_step_handler(task_choice, choose_edit_action)

def choose_edit_action(message):
    global edited_list_id
    if message.text == "Edit List Name":
        new_list_name = imprt_bot.send_message(message.chat.id, "Enter the new List Name:")
        imprt_bot.register_next_step_handler(new_list_name, set_new_list_name)

    elif message.text == "Add Task":
        new_task = imprt_bot.send_message(message.chat.id, "Enter the new task")
        imprt_bot.register_next_step_handler(new_task, add_task_to_edit_list)

    elif message.text == "Edit Task":
        cursor.execute(
            "SELECT task_name FROM tasks WHERE fk_task_id = %s", (edited_list_id,)
        )
        tasks_name = []
        while True:
            row = cursor.fetchone()
            if row:
                tasks_name.append(row)
            else:
                break

        start_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for i in range(len(tasks_name)):
            start_menu.add(types.KeyboardButton(text=f"{tasks_name[i][0]}"))
        msg = imprt_bot.send_message(message.chat.id, "Choose List:", reply_markup=start_menu)
        imprt_bot.register_next_step_handler(msg, choose_task_to_edit)

    elif message.text == "Remove Task":
        cursor.execute(
            "SELECT task_name FROM tasks WHERE fk_task_id = %s", (edited_list_id,)
        )
        tasks_name = []
        while True:
            row = cursor.fetchone()
            if row:
                tasks_name.append(row)
            else:
                break

        start_menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for i in range(len(tasks_name)):
            start_menu.add(types.KeyboardButton(text=f"{tasks_name[i][0]}"))
        msg = imprt_bot.send_message(message.chat.id, "Choose List:", reply_markup=start_menu)
        imprt_bot.register_next_step_handler(msg, choose_task_to_remove)

    elif message.text == "Return":
        imprt_bot.register_next_step_handler(message, main_choice_func)

def add_task_to_edit_list(message):
    global edited_list_id
    cursor.execute(
        "INSERT INTO tasks (task_name, fk_task_id)) VALUES (%s, %s)", (message.text, edited_list_id)
    )
    added_task = imprt_bot.send_message(message.chat.id, "Successfully added")
    imprt_bot.register_next_step_handler(added_task, choose_edit_action)

def choose_task_to_edit(message):
    new_task = imprt_bot.send_message(message.chat.id, "Enter the new task:")
    imprt_bot.register_next_step_handler(new_task, set_new_task_name)

def choose_task_to_remove(message):
    global removed_task
    removed_task = message.text
    sure_mssg = imprt_bot.send_message(message.chat.id, "Are you sure?")
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    menu.add(types.KeyboardButton("Yes"),
             types.KeyboardButton("No"))
    msg = imprt_bot.send_message(message.chat.id, "Choose List:", reply_markup=menu)
    imprt_bot.register_next_step_handler(sure_mssg, remove_task_confirm)

def remove_task_confirm(message):
    global removed_task
    if message.text == "Yes":
        cursor.execute(
            "DELETE FROM tasks WHERE task_name = %s", (removed_task,)
        )
        imprt_bot.register_next_step_handler(message, choose_edit_action)

    elif message.text == "No":
        imprt_bot.register_next_step_handler(message, choose_edit_action)

def set_new_task_name(message):
    global edited_list_id
    cursor.execute(
        "UPDATE tasks SET task_name = %s WHERE fk_task_id = %s", (message.text, edited_list_id)
    )
    mssg = imprt_bot.send_message(message.chat.id, "The task was successfully changed")
    imprt_bot.register_next_step_handler(mssg, choose_edit_action)

def set_new_list_name(message):
    global edited_list_id
    cursor.execute(
        "UPDATE lists SET list_name = %s WHERE list_id = %s", (message.text, edited_list_id)
    )
    mssg = imprt_bot.send_message(message.chat.id, "The new List Name was set")
    imprt_bot.register_next_step_handler(mssg, choose_edit_action)

def show_list(message):
    cursor.execute(
        "SELECT list_id FROM lists WHERE list_name = %s", (message.text,)
    )
    list_id = cursor.fetchone()

    cursor.execute(
        "SELECT task_name FROM tasks WHERE fk_task_id = %s", (list_id,)
    )
    task_list = []
    local_string = ""
    while True:
        row = cursor.fetchone()
        if row:
            task_list.append(row)
        else:
            break

    for i in range(len(task_list)):
        local_string += task_list[i]
        local_string += "\n"
    imprt_bot.send_message(message.chat.id, local_string)

def remove_list(message):
    global removed_list
    removed_list = message.text
    menu = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    menu.add(types.KeyboardButton("Yes"),
             types.KeyboardButton("No"))
    msg = imprt_bot.send_message(message.chat.id, "Are you sure?", reply_markup=menu)
    imprt_bot.register_next_step_handler(msg, remove_list_confirm)

def remove_list_confirm(message):
    global removed_list
    if message.text == "Yes":
        cursor.execute(
            "DROP * FROM tasks WHERE fk_task_id = %s", ()
        )
        cursor.execute(
            "DELETE FROM lists WHERE list_name = %s", (removed_list,)
        )
        mssg = imprt_bot.send_message(message.chat.id, "The list was successfully removed")
        imprt_bot.register_next_step_handler(mssg, main_choice_func)

    elif message.text == "No":
        mssg = imprt_bot.send_message(message.chat.id, "Choose Action:")
        imprt_bot.register_next_step_handler(mssg, main_choice_func)

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

    mssg = imprt_bot.send_message(message.chat.id, "You have successfully add the task")
    imprt_bot.register_next_step_handler(mssg, choose_list_action, cur_list_id)

@imprt_bot.message_handler(content_types=['text'])
def echo_all(message):
    main_choice_func(message)


imprt_bot.infinity_polling()