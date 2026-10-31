import os
import telebot
from telebot.types import BotCommand
from google import genai
import yt_dlp

# Load environment variables safely
TELEGRAM_TOKEN = os.environ.get('TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Initialize the official Google GenAI client
ai_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

bot.delete_webhook(drop_pending_updates=True)

bot.set_my_commands([
    BotCommand("start", "Start the bot"),
    BotCommand("help", "Get usage instructions"),
    BotCommand("status", "Check system status")
])

@bot.message_handler(commands=['start'])
def send_start(message):
    bot.reply_to(message, "👋 Hello! I am @normad404, powered by advanced Gemini AI and media downloading tools.")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, 
        "🤖 **Advanced Bot Guide:**\n\n"
        "1. **Smart AI Chat:** Ask me any technical, creative, or general question!\n"
        "2. **Media Downloader:** Send any video link (YouTube, etc.) to download and receive the file directly."
    )

@bot.message_handler(commands=['status'])
def send_status(message):
    bot.reply_to(message, "🟢 Status: Online, connected to Gemini AI and media tools.")

# Media Download Handler (YouTube & Links)
@bot.message_handler(func=lambda message: message.text and ("http://" in message.text or "https://" in message.text))
def handle_media_download(message):
    url = message.text.strip()
    bot.reply_to(message, "📥 Processing and downloading media, please wait...")
    
    output_filename = "downloaded_media.mp4"
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_filename,
        'max_filesize': 50 * 1024 * 1024, # 50MB restriction for Telegram limit compliance
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        with open(output_filename, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file, caption="Here is your requested media! 🎬")
            
        if os.path.exists(output_filename):
            os.remove(output_filename)
            
    except Exception as e:
        bot.reply_to(message, f"❌ Download failed. The link might be restricted or exceed size limits.\nError: {str(e)}")
        if os.path.exists(output_filename):
            os.remove(output_filename)

# Advanced AI Chat Handler (Powered by Gemini)
@bot.message_handler(func=lambda message: True)
def handle_ai_chat(message):
    if not ai_client:
        bot.reply_to(message, "⚠️ Error: GEMINI_API_KEY environment variable is missing on Render!")
        return
        
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Using the current high-performance model endpoint
        response = ai_client.models.generate_content(
            model='gemini-3.8-flash',
            contents=message.text,
        )
        
        bot.reply_to(message, response.text)
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ AI Error: {str(e)}")

print("🚀 Advanced Telegram Bot script initialized...")
bot.infinity_polling()
