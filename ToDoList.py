import json
import telebot
from telebot import types
from datetime import datetime  # Додайте імпорт datetime
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

# Функція для відображення списку завдань
def display_task_list(chat_id):
    tasks = load_tasks()
    if tasks:
        task_list = ""
        for i, task in enumerate(tasks, start=1):
            status = "[x]" if task["done"] else "[ ]"
            task_description = task["task"]
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
        bot.send_message(message.chat.id, f"Task '{task_description}' added.")
    else:
        bot.send_message(message.chat.id, "Please provide a task description.")

# Обробник події "Remove Task"
@bot.callback_query_handler(func=lambda call: call.data == 'removetask')
def remove_task_callback(call):
    bot.send_message(call.message.chat.id, "You selected 'Remove Task'. Please enter the task description to remove.")
    bot.register_next_step_handler(call.message, remove_task_description)

# Функція для обробки введеного користувачем опису завдання для видалення
def remove_task_description(message):
    task_description = message.text
    if task_description:
        tasks = load_tasks()
        task_removed = None
        for task in tasks:
            if task["task"].lower() == task_description.lower():
                task_removed = task
                tasks.remove(task)
                break
        save_tasks(tasks)
        if task_removed:
            bot.send_message(message.chat.id, f"Task '{task_description}' removed.")
        else:
            bot.send_message(message.chat.id, f"Task '{task_description}' not found.")
    else:
        bot.send_message(message.chat.id, "Please provide a task description.")

# Обробник події "Complete Task"
@bot.callback_query_handler(func=lambda call: call.data == 'completetask')
def complete_task_callback(call):
    bot.send_message(call.message.chat.id, "You selected 'Complete Task'. Please enter the task description to mark as completed.")
    bot.register_next_step_handler(call.message, complete_task_description)

# Функція для обробки введеного користувачем опису завдання для відмітки як виконаного
def complete_task_description(message):
    task_description = message.text
    if task_description:
        tasks = load_tasks()
        task_completed = False
        for task in tasks:
            if task["task"].lower() == task_description.lower():
                task["done"] = True
                task_completed = True
                break
        save_tasks(tasks)
        if task_completed:
            bot.send_message(message.chat.id, f"Task '{task_description}' marked as completed.")
        else:
            bot.send_message(message.chat.id, f"Task '{task_description}' not found.")
    else:
        bot.send_message(message.chat.id, "Please provide a task description.")

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

    markup.row(btn1, btn2)
    markup.row(btn3, btn4)

    bot.send_message(message.chat.id, "Welcome to the Task Bot! Here are the available functions:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'help')
def help_callback(call):
    bot.send_message(call.message.chat.id, "This is the help message.")

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, """
    Here are the available commands:
    - /addtask [task]: Add a new task to your list.
    - /removetask [task]: Remove a task from your list.
    - /completetask [task]: Mark a task as completed.
    - /listtasks: View your current task list. """)

print("Bot is running...")
bot.polling(none_stop=True)