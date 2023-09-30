import json
import telebot
import re
import time
import copy
from telebot import types
from datetime import datetime

bot = telebot.TeleBot('6476351106:AAGW_MvwaqmRgJ8mx5sUN6gjMoAfoVlxiHU')

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

# Оновлений обробник для додавання завдань з дедлайном
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

@bot.callback_query_handler(func=lambda call: call.data == 'completetask')
def complete_task_callback(call):
    bot.send_message(call.message.chat.id, "You selected 'Complete Task'. Please enter the task number to mark as completed.")
    bot.register_next_step_handler(call.message, complete_task_number)

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

from dateutil.relativedelta import relativedelta

# Змінна для зберігання інформації, специфічної для чату
chat_info = {}

# Callback-функція для кнопки зміни дедлайну
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
                bot.send_message(chat_id, "There is no current deadline for this task. You can't change it.")
        else:
            bot.send_message(chat_id, "Invalid task number. Please enter a valid task number.")
    else:
        bot.send_message(chat_id, "Please enter a valid task number.")

# Функція для зміни дедлайну
def set_new_deadline(message):
    chat_id = message.chat.id
    new_deadline = message.text
    if new_deadline:
        try:
            deadline_date = datetime.strptime(new_deadline, "%Y-%m-%d %H:%M")
            task_to_change = chat_info[chat_id]["task_to_change"]
            old_deadline = task_to_change.get('deadline', None)

            # Створення глибокої копії задачі
            task_tmp = copy.deepcopy(task_to_change)

            # Оновлення дедлайну для копії задачі
            task_tmp['deadline'] = deadline_date.strftime("%Y-%m-%d %H:%M")

            # Оновлення списку завдань у файлі
            tasks = load_tasks()

            for i, task in enumerate(tasks):
                if task["task"] == task_to_change["task"]:
                    # Замінюємо оригінальну задачу на копію з оновленим дедлайном
                    tasks[i] = task_tmp
                    break

            save_tasks(tasks)

            # Очищення змінних для зміни дедлайну
            chat_info[chat_id].pop("changing_deadline", None)
            chat_info[chat_id].pop("task_to_change", None)

            # Видалення попереднього повідомлення
            bot.delete_message(chat_id=chat_id, message_id=message.message_id)

        except Exception as e:
            bot.send_message(chat_id, f"An error occurred: {str(e)}")

# Функція для відображення оновленого списку завдань
def display_updated_task_list(chat_id, tasks):
    if not tasks:
        bot.send_message(chat_id, "There are no tasks.")
    else:
        message = "Updated Task List:\n"
        for i, task in enumerate(tasks, start=1):
            message += f"{i}. {task['task']}"
            if task['deadline']:
                message += f" - Deadline: {task['deadline']}"
            message += "\n"
        bot.send_message(chat_id, message)

@bot.callback_query_handler(func=lambda call: call.data == 'cleartasks')
def clear_tasks_callback(call):
    tasks = load_tasks()
    if tasks:
        tasks.clear()
        save_tasks(tasks)
        bot.send_message(call.message.chat.id, "Your task list has been cleared.")
    else:
        bot.send_message(call.message.chat.id, "Your task list is already empty.")

# Function to display the task list
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
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Add Task', callback_data='addtask')
    btn2 = types.InlineKeyboardButton('Remove Task', callback_data='removetask')
    btn3 = types.InlineKeyboardButton('Complete Task', callback_data='completetask')
    btn4 = types.InlineKeyboardButton('List Tasks', callback_data='listtasks')
    btn5 = types.InlineKeyboardButton('Change Deadline', callback_data='changedeadline')
    btn6 = types.InlineKeyboardButton('Help', callback_data='help')
    btn7 = types.InlineKeyboardButton('Clear Tasks', callback_data='cleartasks')

    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.row(btn5, btn6)
    markup.row(btn7)

    bot.send_message(message.chat.id, "Welcome to the Task Bot! Here are the available functions:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == 'help')
def help_callback(call):
    bot.send_message(call.message.chat.id, """
    Here are the available commands:
    - /addtask [task]: Add a new task to your list.
    - /removetask [task]: Remove a task from your list.
    - /completetask [task]: Mark a task as completed.
    - /listtasks: View your current task list.
    - /changedeadline: Change the deadline for a task.
    - /cleartasks: Clear your task list.
    """)

print("Bot is running...")
bot.polling(none_stop=True)
