hereimport os
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
TOKEN=os.environ.get("BOT_TOKEN")
async def start(update, context):
    await update.message.reply_text("Bot is LIVE")
async def echo(update, context):
    await update.message.reply_text(update.message.text)
app=Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, echo))
app.run_polling()
