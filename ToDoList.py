import json

import telebot
from telebot import types
import json

bot = telebot.TeleBot('6476351106:AAGW_MvwaqmRgJ8mx5sUN6gjMoAfoVlxiHU')

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton('/help')
    markup.row(btn1)
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


@bot.message_handler(commands=['addtask'])
def add_task(message):
    task_description = message.text.replace('/addtask ', '')

    if task_description:
        tasks.append({"task": task_description, "done": False, "deadline": None})

        # Function to save tasks to a JSON file
        def save_tasks():
            with open("tasks.json", "w") as file:
                json.dump(tasks, file)

        save_tasks()  # Save the updated task list

        bot.send_message(message.chat.id, f"Task '{task_description}' added.")
    else:
        bot.send_message(message.chat.id, "Please provide a task description.")


@bot.message_handler(commands=['removetask'])
def remove_task(message):
    task_description = message.text.replace('/removetask ', '')

    if task_description:
        task_removed = None
        for t in task_description:
            if t["task"].lower() == task_description.lower():
                task_removed = t
                task_description.remove(t)
                break

        # Function to save tasks to a JSON file
        def save_tasks():
            with open("tasks.json", "w") as file:
                json.dump(task_description, file)

        if task_removed:
            bot.send_message(message.chat.id, f"Task '{task_description}' removed.")
        else:
            bot.send_message(message.chat.id, f"Task '{task_description}' not found.")
    else:
        bot.send_message(message.chat.id, "Please provide a task description.")


@bot.message_handler(commands=['completetask'])
def complete_task(message):
    task = message.text.replace('/completetask ', '')

    if task:
        task_completed = False
        for t in task:
            if t["task"] == task:
                t["done"] = True
                task_completed = True
                break

        # Function to save tasks to a JSON file
        def save_tasks():
            with open("tasks.json", "w") as file:
                json.dump(task, file)

        if task_completed:
            bot.send_message(message.chat.id, f"Task '{task}' marked as completed.")
        else:
            bot.send_message(message.chat.id, f"Task '{task}' not found.")
    else:
        bot.send_message(message.chat.id, "Please provide a task description.")


tasks = []  # Initialize an empty list to store tasks

@bot.message_handler(commands=['listtasks'])
def list_tasks(message):
    task_list = ""

    if tasks:  # Use 'tasks' (plural) instead of 'list_tasks' (function name)
        for i, task in enumerate(tasks, start=1):
            status = "[x]" if task["done"] else "[ ]"
            task_description = task["task"]
            task_list += f"{i}. {status} {task_description}\n"
    else:
        task_list = "Your task list is empty."

    bot.send_message(message.chat.id, f"Your task list:\n{task_list}")


print("Bot is running...")
bot.polling()