import os
import telebot
from telebot.types import BotCommand
from google import genai
import yt_dlp

# Get tokens from environment variables
TELEGRAM_TOKEN = os.environ.get('TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Initialize the Google GenAI client (Gemini)
ai_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

bot.delete_webhook(drop_pending_updates=True)

bot.set_my_commands([
    BotCommand("start", "Start the bot"),
    BotCommand("help", "Get usage instructions"),
    BotCommand("status", "Check system status")
])

@bot.message_handler(commands=['start'])
def send_start(message):
    bot.reply_to(message, "👋 Hey there! I am @normad404, your advanced AI-powered bot. Ask me anything or send a media link to download!")

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, 
        "🤖 **Bot Capabilities:**\n\n"
        "1. **Smart AI Chat:** Just type any question, and I'll answer using Gemini AI.\n"
        "2. **Media Downloader:** Send a YouTube or video link, and I will download and send the file back to you!"
    )

@bot.message_handler(commands=['status'])
def send_status(message):
    bot.reply_to(message, "🟢 Status: AI engine active, downloader ready.")

# Handle Media Downloading (YouTube / Web links)
@bot.message_handler(func=lambda message: message.text and ("http://" in message.text or "https://" in message.text))
def handle_media_download(message):
    url = message.text.strip()
    bot.reply_to(message, "📥 Downloading media, please wait a moment...")
    
    output_filename = "downloaded_media.mp4"
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_filename,
        'max_filesize': 50 * 1024 * 1024, # Limit to 50MB for Telegram limits
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        with open(output_filename, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file, caption="Here is your downloaded media! 🎬")
            
        # Clean up file after sending
        if os.path.exists(output_filename):
            os.remove(output_filename)
            
    except Exception as e:
        bot.reply_to(message, f"❌ Failed to download media. It might be too large or restricted.\nError: {str(e)}")
        if os.path.exists(output_filename):
            os.remove(output_filename)

# Handle Smart AI Chat (Powered by Gemini)
@bot.message_handler(func=lambda message: True)
def handle_ai_chat(message):
    if not ai_client:
        bot.reply_to(message, f"You said: {message.text} (Note: Gemini API Key is missing in environment variables!)")
        return
        
    try:
        # Show 'typing...' action so the user knows the AI is thinking
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Query Gemini AI
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=message.text,
        )
        
        bot.reply_to(message, response.text)
        
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error communicating with AI: {str(e)}")

print("🚀 Advanced AI Bot is live...")
bot.infinity_polling()
