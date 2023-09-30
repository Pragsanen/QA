import json
import telebot
import re
import time
import copy
from telebot import types
from datetime import datetime
from config import BOT_TOKEN  # Import BOT_TOKEN from config.py

bot = telebot.TeleBot(BOT_TOKEN)

def load_tasks():
    try:
        with open("завдання.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_tasks(tasks):
    with open("завдання.json", "w") as file:
        json.dump(tasks, file)

def display_task_list(chat_id):
    tasks = load_tasks()
    if tasks:
        task_list = ""
        for i, task in enumerate(tasks, start=1):
            status = "[x]" if task["done"] else "[ ]"
            task_description = task["task"]
            deadline = task["deadline"]
            if deadline:
                task_list += f"{i}. {status} {task_description} (Deadline: {deadline})\n"
            else:
                task_list += f"{i}. {status} {task_description}\n"
        bot.send_message(chat_id, f"Your task list:\n{task_list}")
    else:
        bot.send_message(chat_id, "Your task list is empty.")

# Функція для додавання завдання з дедлайном
def add_task_with_deadline(chat_id, task_description, deadline):
    tasks = load_tasks()
    tasks.append({"task": task_description, "done": False, "deadline": deadline})
    save_tasks(tasks)
    bot.send_message(chat_id, f"Task '{task_description}' added with a deadline of {deadline}.")

    # Оновлення списку завдань і відправка його користувачеві
    display_task_list(chat_id)

COMMAND_ADD_TASK = "/addtask"
COMMAND_REMOVE_TASK = "/removetask"
COMMAND_COMPLETE_TASK = "/completetask"
COMMAND_LIST_TASKS = "/listtasks"
COMMAND_CHANGE_DEADLINE = "/changedeadline"
COMMAND_HELP = "/help"
COMMAND_CLEAR_TASKS = "/cleartasks"
COMMAND_NEW_LIST = "/newlist"
COMMAND_EXISTING_LIST = "/existinglist"
COMMAND_SELECT_FILE = "selectfile"

@bot.message_handler(commands=['start'])
def start(message):
    BUTTON_ADD_TASK = 'addtask'
    BUTTON_REMOVE_TASK = 'removetask'
    BUTTON_COMPLETE_TASK = 'completetask'
    BUTTON_LIST_TASKS = 'listtasks'
    BUTTON_CHANGE_DEADLINE = 'changedeadline'
    BUTTON_HELP = 'help'
    BUTTON_CLEAR_TASKS = 'cleartasks'
    BUTTON_NEW_LIST = 'newlist'
    BUTTON_EXISTING_LIST = 'existinglist'
    BUTTON_SELECT_FILE = 'selectfile'

    # Отримання кнопок для відображення
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Add Task', callback_data=BUTTON_ADD_TASK)
    btn2 = types.InlineKeyboardButton('Remove Task', callback_data=BUTTON_REMOVE_TASK)
    btn3 = types.InlineKeyboardButton('Complete Task', callback_data=BUTTON_COMPLETE_TASK)
    btn4 = types.InlineKeyboardButton('List Tasks', callback_data=BUTTON_LIST_TASKS)
    btn5 = types.InlineKeyboardButton('Change Deadline', callback_data=BUTTON_CHANGE_DEADLINE)
    btn6 = types.InlineKeyboardButton('Help', callback_data=BUTTON_HELP)
    btn7 = types.InlineKeyboardButton('Clear Tasks', callback_data=BUTTON_CLEAR_TASKS)
    btn8 = types.InlineKeyboardButton('New List', callback_data=BUTTON_NEW_LIST)
    btn9 = types.InlineKeyboardButton('Existing List', callback_data=BUTTON_EXISTING_LIST)
    btn10 = types.InlineKeyboardButton('Select File', callback_data=BUTTON_SELECT_FILE)  # Added this button

    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.row(btn5, btn6)
    markup.row(btn7)
    markup.row(btn8, btn9)
    markup.row(btn10)

    bot.send_message(message.chat.id, "Welcome to the Task Bot! Here are the available functions:", reply_markup=markup)
# Обробник для додавання завдань з дедлайном
@bot.callback_query_handler(func=lambda call: call.data == 'addtask')
def add_task_callback(call):
    bot.send_message(call.message.chat.id, "You selected 'Add Task'. Please enter the task description.")
    bot.register_next_step_handler(call.message, add_task_description)

# Функція для обробки введеного користувачем дедлайну
def add_task_description(message):
    task_description = message.text
    chat_id = message.chat.id
    if task_description:
        bot.send_message(chat_id, f"You entered the task description: {task_description}. Please enter a deadline in the format 'YYYY-MM-DD HH:MM'.")
        chat_info[chat_id] = {"task_description": task_description}
        bot.register_next_step_handler(message, add_task_deadline)
    else:
        bot.send_message(chat_id, "Please provide a task description.")

# Функція для обробки введеного користувачем дедлайну
def add_task_deadline(message):
    chat_id = message.chat.id
    task_description = chat_info[chat_id]["task_description"]
    deadline = message.text

    # Використовуємо регулярний вираз для перевірки введеного дедлайну
    date_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}"
    if re.match(date_pattern, deadline):
        add_task_with_deadline(chat_id, task_description, deadline)
    else:
        bot.send_message(chat_id, "Invalid deadline format. Please use 'YYYY-MM-DD HH:MM'.")
def set_deadline(message, deadline):
    chat_id = message.chat.id
    task_description = chat_info[chat_id]["task_description"]
    custom_deadline = message.text

    # Використовуємо регулярний вираз для перевірки введеного дедлайну
    date_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}"
    if re.match(date_pattern, custom_deadline):
        tasks = load_tasks()
        tasks.append({"task": task_description, "done": False, "deadline": custom_deadline})
        save_tasks(tasks)

        # Очищення об'єкта chat_info для даного чату
        chat_info.pop(chat_id, None)

        bot.send_message(chat_id, f"Task '{task_description}' added with a deadline of {custom_deadline}.")

        # Оновлення списку завдань і відправка його користувачеві
        display_task_list(chat_id)
    else:
        bot.send_message(chat_id, "Invalid deadline format. Please use 'YYYY-MM-DD HH:MM'.")

@bot.message_handler(commands=['addtask'])
def add_task_command(message):
    bot.send_message(message.chat.id, "You selected 'Add Task'. Please enter the task description.")
    bot.register_next_step_handler(message, add_task_description)

# Функція для обробки введеного користувачем дедлайну
def add_task_description(message):
    task_description = message.text
    chat_id = message.chat.id
    if task_description:
        bot.send_message(chat_id, f"You entered the task description: {task_description}. Please enter a deadline in the format 'YYYY-MM-DD HH:MM'.")
        chat_info[chat_id] = {"task_description": task_description}
        bot.register_next_step_handler(message, add_task_deadline)
    else:
        bot.send_message(chat_id, "Please provide a task description.")

# Функція для обробки введеного користувачем дедлайну
def add_task_deadline(message):
    chat_id = message.chat.id
    task_description = chat_info[chat_id]["task_description"]
    deadline = message.text

    # Використовуємо регулярний вираз для перевірки введеного дедлайну
    date_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}"
    if re.match(date_pattern, deadline):
        add_task_with_deadline(chat_id, task_description, deadline)
    else:
        bot.send_message(chat_id, "Invalid deadline format. Please use 'YYYY-MM-DD HH:MM'.")
def set_deadline(message, deadline):
    chat_id = message.chat.id
    task_description = chat_info[chat_id]["task_description"]
    custom_deadline = message.text

    # Використовуємо регулярний вираз для перевірки введеного дедлайну
    date_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}"
    if re.match(date_pattern, custom_deadline):
        tasks = load_tasks()
        tasks.append({"task": task_description, "done": False, "deadline": custom_deadline})
        save_tasks(tasks)

        # Очищення об'єкта chat_info для даного чату
        chat_info.pop(chat_id, None)

        bot.send_message(chat_id, f"Task '{task_description}' added with a deadline of {custom_deadline}.")

        # Оновлення списку завдань і відправка його користувачеві
        display_task_list(chat_id)
    else:
        bot.send_message(chat_id, "Invalid deadline format. Please use 'YYYY-MM-DD HH:MM'.")

@bot.callback_query_handler(func=lambda call: call.data == 'removetask')
def remove_task_menu_callback(call):
    bot.send_message(call.message.chat.id, "You selected 'Remove Task'. Please enter the task number to remove.")
    bot.register_next_step_handler(call.message, remove_task_number)
    display_task_list(call.message.chat.id)

def remove_task_number(message):
    task_number = message.text
    if task_number.isdigit():
        task_number = int(task_number)
        tasks = load_tasks()
        if 1 <= task_number <= len(tasks):
            task = tasks.pop(task_number - 1)
            save_tasks(tasks)
            bot.send_message(message.chat.id, f"Task '{task['task']}' removed.")

            # After removing a task, update the list and send it
            display_task_list(message.chat.id)
        else:
            bot.send_message(message.chat.id, "Invalid task number. Please enter a valid task number.")
    else:
        bot.send_message(message.chat.id, "Please enter a valid task number.")
@bot.message_handler(commands=['removetask'])
def remove_task_menu_command(message):
    bot.send_message(message.chat.id, "You selected 'Remove Task'. Please enter the task number to remove.")
    bot.register_next_step_handler(message, remove_task_number)
def remove_task_number(message):
    task_number = message.text
    if task_number.isdigit():
        task_number = int(task_number)
        tasks = load_tasks()
        if 1 <= task_number <= len(tasks):
            task = tasks.pop(task_number - 1)
            save_tasks(tasks)
            bot.send_message(message.chat.id, f"Task '{task['task']}' removed.")

            # After removing a task, update the list and send it
            display_task_list(message.chat.id)
        else:
            bot.send_message(message.chat.id, "Invalid task number. Please enter a valid task number.")
    else:
        bot.send_message(message.chat.id, "Please enter a valid task number.")

@bot.callback_query_handler(func=lambda call: call.data == 'completetask')
def complete_task_callback(call):
    bot.send_message(call.message.chat.id, "You selected 'Complete Task'. Please enter the task number to mark as completed.")
    bot.register_next_step_handler(call.message, complete_task_number)
    display_task_list(call.message.chat.id)
def complete_task_number(message):
    task_number = message.text
    if task_number.isdigit():
        task_number = int(task_number)
        tasks = load_tasks()
        if 1 <= task_number <= len(tasks):
            task = tasks[task_number - 1]
            task["done"] = True
            save_tasks(tasks)
            bot.send_message(message.chat.id, f"Task '{task['task']}' marked as completed.")
        else:
            bot.send_message(message.chat.id, "Invalid task number. Please enter a valid task number.")
    else:
        bot.send_message(message.chat.id, "Please enter a valid task number.")
@bot.message_handler(commands=['completetask'])
def complete_task_command(message):
    bot.send_message(message.chat.id, "You selected 'Complete Task'. Please enter the task number to mark as completed.")
    bot.register_next_step_handler(message, complete_task_number)
def complete_task_number(message):
    task_number = message.text
    if task_number.isdigit():
        task_number = int(task_number)
        tasks = load_tasks()
        if 1 <= task_number <= len(tasks):
            task = tasks[task_number - 1]
            task["done"] = True
            save_tasks(tasks)
            bot.send_message(message.chat.id, f"Task '{task['task']}' marked as completed.")
        else:
            bot.send_message(message.chat.id, "Invalid task number. Please enter a valid task number.")
    else:
        bot.send_message(message.chat.id, "Please enter a valid task number.")
@bot.callback_query_handler(func=lambda call: call.data == 'listtasks')
def list_tasks_callback(call):
    bot.send_message(call.message.chat.id, "You selected 'List Tasks'. Here are your current tasks:")
    display_task_list(call.message.chat.id)
@bot.message_handler(commands=['listtasks'])
def complete_task_command(message):
    bot.send_message(message.chat.id, "You selected 'List Tasks'. Here are your current tasks:")
    display_task_list(message.chat.id)

from dateutil.relativedelta import relativedelta

# Змінна для зберігання інформації, специфічної для чату
chat_info = {}
# Обробник для зміни дедлайну
@bot.message_handler(commands=['changedeadline'])
def change_deadline_command(message):
    chat_id = message.chat.id
    chat_info[chat_id] = {"changing_deadline": True}
    bot.send_message(chat_id, "Please enter the task number you want to change the deadline for.")

    # Відображення поточного списку завдань
    display_task_list(chat_id)  # Передача завдань у функцію

# Обробник повідомлень, якщо користувач міняє дедлайн
@bot.message_handler(func=lambda message: chat_info.get(message.chat.id, {}).get("changing_deadline", False))
def ask_task_number(message):
    chat_id = message.chat.id
    task_number = message.text
    if task_number.isdigit():
        task_number = int(task_number) - 1  # Віднімання 1, щоб отримати правильний індекс завдання
        tasks = load_tasks()
        if 0 <= task_number < len(tasks):
            task_to_change = tasks[task_number]
            chat_info[chat_id]["task_to_change"] = task_to_change
            old_deadline = task_to_change.get('deadline', None)
            if old_deadline:
                bot.send_message(chat_id, f"Current deadline for task: {old_deadline}")
            bot.send_message(chat_id, "Please enter a new deadline (e.g., 'YYYY-MM-DD HH:MM').")
            bot.register_next_step_handler(message, set_new_deadline)
        else:
            bot.send_message(chat_id, "Invalid task number. Please enter a valid task number.")
    else:
        bot.send_message(chat_id, "Please enter a valid task number.")

# Функція для встановлення нового дедлайну
def set_new_deadline(message):
    chat_id = message.chat.id
    new_deadline = message.text
    task_to_change = chat_info[chat_id]["task_to_change"]

    # Створення глибокої копії задачі
    task_tmp = copy.deepcopy(task_to_change)

    try:
        deadline_date = datetime.strptime(new_deadline, "%Y-%m-%d %H:%M")

        # Оновлення дедлайну для копії задачі
        task_tmp['deadline'] = deadline_date.strftime("%Y-%m-%d %H:%M")

        # Оновлення списку завдань у файлі
        tasks = load_tasks()
        task_found = False  # Змінна для відстеження, чи знайдено завдання для оновлення

        for i, task in enumerate(tasks):
            if task["task"] == task_to_change["task"]:
                # Замінюємо оригінальну задачу на копію з оновленим дедлайном
                tasks[i] = task_tmp
                task_found = True
                break

        if not task_found:
            # Якщо завдання для оновлення не знайдено, то додаємо нове завдання
            tasks.append(task_tmp)

        save_tasks(tasks)

        # Очищення змінних для зміни дедлайну
        chat_info[chat_id].pop("changing_deadline", None)
        chat_info[chat_id].pop("task_to_change", None)

        # Видалення попереднього повідомлення
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)

        bot.send_message(chat_id, "Deadline updated successfully!")

    except ValueError:
        # Якщо формат дедлайну неправильний, запитати ще раз
        bot.send_message(chat_id, "Invalid date format. Please enter a new deadline in the format 'YYYY-MM-DD HH:MM'.")
        bot.send_message(chat_id, "Please enter a new deadline (e.g., 'YYYY-MM-DD HH:MM').")

    except KeyError:
        # Якщо завдання не має поточного дедлайну, додати новий дедлайн
        tasks = load_tasks()
        tasks.append(task_tmp)
        save_tasks(tasks)

        # Очищення змінних для зміни дедлайну
        chat_info[chat_id].pop("changing_deadline", None)
        chat_info[chat_id].pop("task_to_change", None)

        # Видалення попереднього повідомлення
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)

        bot.send_message(chat_id, "Deadline added successfully!")

@bot.callback_query_handler(func=lambda call: call.data == 'changedeadline')
def change_deadline_button_callback(call):
    chat_id = call.message.chat.id
    chat_info[chat_id] = {"changing_deadline": True}
    bot.send_message(chat_id, "Please enter the task number you want to change the deadline for.")

    # Відображення поточного списку завдань
    display_task_list(chat_id)  # Передача завдань у функцію

# Обробник повідомлень, якщо користувач міняє дедлайн
@bot.message_handler(func=lambda message: chat_info.get(message.chat.id, {}).get("changing_deadline", False))
def ask_task_number(message):
    chat_id = message.chat.id
    task_number = message.text
    if task_number.isdigit():
        task_number = int(task_number) - 1  # Віднімання 1, щоб отримати правильний індекс завдання
        tasks = load_tasks()
        if 0 <= task_number < len(tasks):
            task_to_change = tasks[task_number]
            chat_info[chat_id]["task_to_change"] = task_to_change
            old_deadline = task_to_change.get('deadline', None)
            if old_deadline:
                bot.send_message(chat_id, f"Current deadline for task: {old_deadline}")
            bot.send_message(chat_id, "Please enter a new deadline (e.g., 'YYYY-MM-DD HH:MM').")
            bot.register_next_step_handler(message, set_new_deadline)
        else:
            bot.send_message(chat_id, "Invalid task number. Please enter a valid task number.")
    else:
        bot.send_message(chat_id, "Please enter a valid task number.")

def set_new_deadline(message):
    chat_id = message.chat.id
    new_deadline = message.text
    task_to_change = chat_info[chat_id]["task_to_change"]

    # Створення глибокої копії задачі
    task_tmp = copy.deepcopy(task_to_change)

    try:
        deadline_date = datetime.strptime(new_deadline, "%Y-%m-%d %H:%M")

        # Оновлення дедлайну для копії задачі
        task_tmp['deadline'] = deadline_date.strftime("%Y-%m-%d %H:%M")

        # Оновлення списку завдань у файлі
        tasks = load_tasks()
        task_found = False  # Змінна для відстеження, чи знайдено завдання для оновлення

        for i, task in enumerate(tasks):
            if task["task"] == task_to_change["task"]:
                # Замінюємо оригінальну задачу на копію з оновленим дедлайном
                tasks[i] = task_tmp
                task_found = True
                break

        if not task_found:
            # Якщо завдання для оновлення не знайдено, то додаємо нове завдання
            tasks.append(task_tmp)

        save_tasks(tasks)

        # Очищення змінних для зміни дедлайну
        chat_info[chat_id].pop("changing_deadline", None)
        chat_info[chat_id].pop("task_to_change", None)

        # Видалення попереднього повідомлення
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)

        bot.send_message(chat_id, "Deadline updated successfully!")

    except ValueError:
        # Якщо формат дедлайну неправильний, запитати ще раз
        bot.send_message(chat_id, "Invalid date format. Please enter a new deadline in the format 'YYYY-MM-DD HH:MM'.")
        bot.send_message(chat_id, "Please enter a new deadline (e.g., 'YYYY-MM-DD HH:MM').")

    except KeyError:
        # Якщо завдання не має поточного дедлайну, додати новий дедлайн
        tasks = load_tasks()
        tasks.append(task_tmp)
        save_tasks(tasks)

        # Очищення змінних для зміни дедлайну
        chat_info[chat_id].pop("changing_deadline", None)
        chat_info[chat_id].pop("task_to_change", None)

        # Видалення попереднього повідомлення
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)

        bot.send_message(chat_id, "Deadline added successfully!")

@bot.message_handler(commands=['cleartasks'])
def clear_tasks_command(message):
    tasks = load_tasks()
    if tasks:
        tasks.clear()
        save_tasks(tasks)
        bot.send_message(message.chat.id, "Your task list has been cleared.")
    else:
        bot.send_message(message.chat.id, "Your task list is already empty.")
@bot.callback_query_handler(func=lambda call: call.data == 'cleartasks')
def clear_tasks_callback(call):
    tasks = load_tasks()
    if tasks:
        tasks.clear()
        save_tasks(tasks)
        bot.send_message(call.message.chat.id, "Your task list has been cleared.")
    else:
        bot.send_message(call.message.chat.id, "Your task list is already empty.")

@bot.message_handler(commands=['help'])
def help_tasks_command(message):
    bot.send_message(message.chat.id, """
        Here are the available commands:
        start - Start using the bot.
        /addtask - Add a new task to your to-do list.
        /removetask - Remove a task from your to-do list.
        /completetask - Mark a task as completed.
        /listtasks - List all the tasks in your to-do list.
        /changedeadline - Change the deadline for a task.
        /help - Get assistance and instructions on using the bot.
        /cleartasks - Clear all tasks from your to-do list.
        /selectfile - Create or select a file for working with tasks.
        /existinglist - Choose an existing list to work with.
        /newlist - Create a new to - do list.""")
@bot.callback_query_handler(func=lambda call: call.data == 'help')
def help_callback(call):
    bot.send_message(call.message.chat.id, """
        Here are the available commands:
        start - Start using the bot.
        /addtask - Add a new task to your to-do list.
        /removetask - Remove a task from your to-do list.
        /completetask - Mark a task as completed.
        /listtasks - List all the tasks in your to-do list.
        /changedeadline - Change the deadline for a task.
        /help - Get assistance and instructions on using the bot.
        /cleartasks - Clear all tasks from your to-do list.
        /selectfile - Create or select a file for working with tasks.
        /existinglist - Choose an existing list to work with.
        /newlist - Create a new to - do list.""")\

todo_lists = {}\

@bot.callback_query_handler(func=lambda call: call.data == 'newlist')
def new_list_callback(call):
    chat_id = call.message.chat.id
    bot.send_message(chat_id, "You have chosen to create a new to-do list. Please enter the name of the new list.")
    bot.register_next_step_handler(call.message, create_new_list)

def create_new_list(message):
    chat_id = message.chat.id
    new_list_name = message.text

    if chat_id not in todo_lists:
        todo_lists[chat_id] = []

    todo_lists[chat_id].append({"list_name": new_list_name, "tasks": []})

    bot.send_message(chat_id, f"New to-do list '{new_list_name}' has been created.")
@bot.message_handler(commands=['newlist'])
def new_list_command(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "You have chosen to create a new to-do list. Please enter the name of the new list.")
    bot.register_next_step_handler(message, create_new_list)

def create_new_list(message):
    chat_id = message.chat.id
    new_list_name = message.text

    if chat_id not in todo_lists:
        todo_lists[chat_id] = []

    todo_lists[chat_id].append({"list_name": new_list_name, "tasks": []})

    bot.send_message(chat_id, f"New to-do list '{new_list_name}' has been created.'.")

# Handling the /existinglist command
@bot.message_handler(commands=['existinglist'])
def existing_list_command(message):
    chat_id = message.chat.id

    if chat_id in todo_lists:
        existing_lists = [list_info["list_name"] for list_info in todo_lists[chat_id]]
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for list_name in existing_lists:
            markup.add(list_name)

        bot.send_message(chat_id, "You have chosen to work with an existing list. Please select a list from the options below:", reply_markup=markup)
        bot.register_next_step_handler(message, choose_existing_list)
    else:
        bot.send_message(chat_id, "Unfortunately, you don't have any created to-do lists. Please create a new list using the /newlist command.")

def choose_existing_list(message):
    chat_id = message.chat.id
    selected_list_name = message.text

    list_index = -1
    if chat_id in todo_lists:
        for idx, list_info in enumerate(todo_lists[chat_id]):
            if list_info["list_name"] == selected_list_name:
                list_index = idx
                break

    if list_index != -1:
        bot.send_message(chat_id, f"You have chosen the to-do list '{selected_list_name}'. You can now interact with this list.")
    else:
        bot.send_message(chat_id, "List not found. Please select an existing list from the options below:")
        existing_list_command(message)
@bot.callback_query_handler(func=lambda call: call.data == 'existinglist')
def existing_list_callback(call):
    chat_id = call.message.chat.id

    if chat_id in todo_lists:
        existing_lists = [list_info["list_name"] for list_info in todo_lists[chat_id]]
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for list_name in existing_lists:
            markup.add(list_name)

        bot.send_message(chat_id, "You have chosen to work with an existing list. Please select a list from the options below:", reply_markup=markup)
        bot.register_next_step_handler(call.message, choose_existing_list)
    else:
        bot.send_message(chat_id, "Unfortunately, you don't have any created to-do lists. Please create a new list using the /newlist command.")

def choose_existing_list(message):
    chat_id = message.chat.id
    selected_list_name = message.text

    list_index = -1
    if chat_id in todo_lists:
        for idx, list_info in enumerate(todo_lists[chat_id]):
            if list_info["list_name"] == selected_list_name:
                list_index = idx
                break

    if list_index != -1:
        bot.send_message(chat_id, f"You have chosen the to-do list '{selected_list_name}'. You can now interact with this list.")
    else:
        bot.send_message(chat_id, "List not found. Please select an existing list from the options below:")
        existing_list_callback(message)
# Callback query handler for selectfile
@bot.callback_query_handler(func=lambda call: call.data == 'selectfile')
def select_file_callback(call):
    chat_id = call.message.chat.id

    # Assuming you want to provide options for selecting or creating a file
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("Select Existing File", "Create New File")

    bot.send_message(chat_id, "You have chosen to work with files. Please select an option:", reply_markup=markup)
    bot.register_next_step_handler(call.message, handle_file_option)

# Message handler for /selectfile command
@bot.message_handler(commands=['selectfile'])
def select_file_command(message):
    chat_id = message.chat.id

    # Assuming you want to provide options for selecting or creating a file
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add("Select Existing File", "Create New File")

    bot.send_message(chat_id, "You have chosen to work with files. Please select an option:", reply_markup=markup)
    bot.register_next_step_handler(message, handle_file_option)

def handle_file_option(message):
    chat_id = message.chat.id
    option = message.text

    if option == "Select Existing File":
        # Handle the logic for selecting an existing file
        bot.send_message(chat_id, "You have selected to select an existing file. Implement this functionality here.")
    elif option == "Create New File":
        # Handle the logic for creating a new file
        bot.send_message(chat_id, "You have selected to create a new file. Implement this functionality here.")
    else:
        bot.send_message(chat_id, "Invalid option. Please select an option from the provided choices.")


print("Bot is running...")
bot.polling(none_stop=True)

