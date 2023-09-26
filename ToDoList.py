import json
import telebot
from telebot import types
from datetime import datetime
bot = telebot.TeleBot('6476351106:AAGW_MvwaqmRgJ8mx5sUN6gjMoAfoVlxiHU')
def load_tasks():
    try:
        with open("завдання.json", "r") as file:
            tasks = json.load(file)
    except FileNotFoundError:
        tasks = []  # Якщо файл не знайдено, створюємо пустий список завдань
    return tasks

def save_tasks(tasks):
    with open("завдання.json", "w") as file:
        json.dump(tasks, file)

# Обробник події "Clear Tasks"
@bot.callback_query_handler(func=lambda call: call.data == 'cleartasks')
def clear_tasks_callback(call):
    tasks = load_tasks()
    if tasks:
        tasks.clear()
        save_tasks(tasks)
        bot.send_message(call.message.chat.id, "Your task list has been cleared.")
    else:
        bot.send_message(call.message.chat.id, "Your task list is already empty.")


# Функція для відображення списку завдань
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


# Обробник події "Add Task"
@bot.callback_query_handler(func=lambda call: call.data == 'addtask')
def add_task_callback(call):
    bot.send_message(call.message.chat.id, "You selected 'Add Task'. Please enter the task description.")
    bot.register_next_step_handler(call.message, add_task_description)

# Функція для обробки введеного користувачем опису завдання
def add_task_description(message):
    task_description = message.text
    if task_description:
        tasks = load_tasks()
        tasks.append({"task": task_description, "done": False, "deadline": None})
        save_tasks(tasks)
        # Після додавання опису завдання, запитати про дедлайн
        bot.send_message(message.chat.id,
                         f"Task '{task_description}' added. Please enter the deadline (e.g., 'YYYY-MM-DD HH:MM').")
        bot.register_next_step_handler(message, add_task_deadline)
    else:
        bot.send_message(message.chat.id, "Please provide a task description.")
    # Функція для обробки введеного користувачем дедлайну
def add_task_deadline(message):
        deadline = message.text
        if deadline:
            try:
                deadline_date = datetime.strptime(deadline, "%Y-%m-%d %H:%M")  # Припустимий формат дедлайну
                tasks = load_tasks()
                latest_task = tasks[-1]  # Отримуємо останнє додане завдання
                latest_task["deadline"] = deadline_date.strftime(
                    "%Y-%m-%d %H:%M")  # Додаємо дедлайн до останнього завдання
                save_tasks(tasks)
                bot.send_message(message.chat.id, f"Deadline for task '{latest_task['task']}' set to {deadline}.")
            except ValueError:
                bot.send_message(message.chat.id, "Invalid deadline format. Please use 'YYYY-MM-DD HH:MM'.")
        else:
            bot.send_message(message.chat.id, "Please provide a deadline.")
# Обробник події "Remove Task"
@bot.callback_query_handler(func=lambda call: call.data == 'removetask')
def remove_task_menu_callback(call):
    bot.send_message(call.message.chat.id, "You selected 'Remove Task'. Please enter the task number to remove.")
    bot.register_next_step_handler(call.message, remove_task_number)
    display_task_list(call.message.chat.id)
# Функція для обробки введеного користувачем номера завдання для видалення
def remove_task_number(message):
    task_number = message.text
    if task_number.isdigit():
        task_number = int(task_number)
        tasks = load_tasks()
        if 1 <= task_number <= len(tasks):
            task = tasks.pop(task_number - 1)
            save_tasks(tasks)
            bot.send_message(message.chat.id, f"Task '{task['task']}' removed.")

            # Після видалення завдання оновлюємо список і відправляємо користувачу
            display_task_list(message.chat.id)
        else:
            bot.send_message(message.chat.id, "Invalid task number. Please enter a valid task number.")
    else:
        bot.send_message(message.chat.id, "Please enter a valid task number.")

# Оновлений список завдань
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

# Обробник події "Complete Task"
@bot.callback_query_handler(func=lambda call: call.data == 'completetask')
def complete_task_callback(call):
    bot.send_message(call.message.chat.id, "You selected 'Complete Task'. Please enter the task number to mark as completed.")
    bot.register_next_step_handler(call.message, complete_task_number)

# Функція для обробки введеного користувачем номера завдання для відмітки як виконаного
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


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Add Task', callback_data='addtask')
    btn2 = types.InlineKeyboardButton('Remove Task', callback_data='removetask')
    btn3 = types.InlineKeyboardButton('Complete Task', callback_data='completetask')
    btn4 = types.InlineKeyboardButton('List Tasks', callback_data='listtasks')
    btn5 = types.InlineKeyboardButton('Help', callback_data='help')
    btn6 = types.InlineKeyboardButton('Clear Tasks', callback_data='cleartasks')

    markup.row(btn1, btn2)
    markup.row(btn3, btn4)
    markup.row(btn5, btn6)

    bot.send_message(message.chat.id, "Welcome to the Task Bot! Here are the available functions:", reply_markup=markup)


# Обробник події "Help"
@bot.callback_query_handler(func=lambda call: call.data == 'help')
def help_callback(call):
    bot.send_message(call.message.chat.id,"""
    Here are the available commands:
    - /addtask [task]: Add a new task to your list.
    - /removetask [task]: Remove a task from your list.
    - /completetask [task]: Mark a task as completed.
    - /listtasks: View your current task list. """)

print("Bot is running...")
bot.polling(none_stop=True)