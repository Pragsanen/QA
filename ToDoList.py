import telebot

bot = telebot.TeleBot('6476351106:AAGW_MvwaqmRgJ8mx5sUN6gjMoAfoVlxiHU')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Welcome to the Todo List Bot!\nType /help for instructions.")

@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, """
    Here are the available commands:
    - /addtask [task]: Add a new task to your list.
    - /removetask [task]: Remove a task from your list.
    - /completetask [task]: Mark a task as completed.
    - /listtasks: View your current task list.
    """)

@bot.message_handler(commands=['addtask'])
def add_task(message):
    task = message.text.replace('/addtask ', '')
    # Add code to handle adding tasks here
    bot.send_message(message.chat.id, f"Task '{task}' added.")

@bot.message_handler(commands=['removetask'])
def remove_task(message):
    task = message.text.replace('/removetask ', '')
    # Add code to handle removing tasks here
    bot.send_message(message.chat.id, f"Task '{task}' removed.")

@bot.message_handler(commands=['completetask'])
def complete_task(message):
    task = message.text.replace('/completetask ', '')
    # Add code to handle completing tasks here
    bot.send_message(message.chat.id, f"Task '{task}' marked as completed.")

@bot.message_handler(commands=['listtasks'])
def list_tasks(message):
    # Add code to list tasks here
    tasks = ["Task 1", "Task 2", "Task 3"]  # Replace with actual task list
    task_list = "\n".join(tasks)
    bot.send_message(message.chat.id, f"Your task list:\n{task_list}")

print("Bot is running...")
bot.polling()