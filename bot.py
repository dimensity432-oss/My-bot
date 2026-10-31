import os
import telebot
from telebot.types import BotCommand

# Fetches your token securely from the cloud dashboard
TOKEN = os.environ.get('TOKEN')
bot = telebot.TeleBot(TOKEN)

bot.delete_webhook(drop_pending_updates=True)

bot.set_my_commands([
    BotCommand("start", "Start the bot"),
    BotCommand("help", "Get usage instructions"),
    BotCommand("status", "Check system status")
])

@bot.message_handler(commands=['start'])
def send_start(message):
    bot.reply_to(message, "👋 Welcome to @normad404! I am online and running via GitHub deployment.")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "Commands available:\n/start - Wake up\n/help - Help menu\n/status - System status")

@bot.message_handler(commands=['status'])
def send_status(message):
    bot.reply_to(message, "🟢 Status: Active & Listening.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"You said: {message.text}")

print("🚀 Bot is live and polling...")
bot.infinity_polling()
