import os
import requests
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
import telegram.constants
BOT_TOKEN = os.getenv("telegram_bot_token")
FLASK_URL = "http://localhost:5000"

MEET_TEXT, ATTENDEE_EMAIL = range(2)
TEXT_MESSAGE, PHONE_NUMBER = range(2, 4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    login_url = f"{FLASK_URL}/login?user_id={user_id}"

    await update.message.reply_text(
        f'<a href="{login_url}">🔐 Click this link to login with  Google, only first time required.</a>\n {login_url}\n'
        f'If already logged in once, there is no need to login again. ',
        parse_mode=ParseMode.HTML
    )

async def start_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📅 What is the meeting about?")
    return MEET_TEXT

async def receive_meet_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['meet_text'] = update.message.text
    await update.message.reply_text("👤 Enter the attendee's email address:")
    return ATTENDEE_EMAIL

async def receive_attendee_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    meet_text = context.user_data['meet_text']
    attendee_email = update.message.text

    data = {
        "meet_text": meet_text,
        "attendee_email": attendee_email
    }
    print(data)
    try:
        response = requests.post(f"{FLASK_URL}/schedule", json=data)
        response.raise_for_status()
        result = response.json()

        await update.message.reply_text(
            f"✅ Meeting scheduled!\n📎 Link: {result.get('event_link')}"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to schedule: {str(e)}")

    return ConversationHandler.END

async def start_texting(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('📩 What message would you like to send?')
    return TEXT_MESSAGE

async def receive_text_message(update:Update, context:ContextTypes.DEFAULT_TYPE):
    context.user_data['text_message'] = update.message.text
    await update.message.reply_text("📞 Enter the recipient's phone number:")
    return PHONE_NUMBER

async def receive_phone_number(update:Update, context:ContextTypes.DEFAULT_TYPE):
    message = context.user_data['text_message']
    phone= update.message.text
    data = {"message": message, "phone" : phone}

    try:
        response = requests.post(f"{FLASK_URL}/send_text", json=data)
        response.raise_for_status()
        await update.message.reply_text("✅ Text message sent!")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to send message: {str(e)}")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Scheduling canceled.")
    return ConversationHandler.END


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("schedule", start_schedule)],
        states={
            MEET_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_meet_text)],
            ATTENDEE_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_attendee_email)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],

    )
    text_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("send_text", start_texting)],
        states = {
            TEXT_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_text_message)],
            PHONE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_phone_number)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(text_conv_handler)
    print("🤖 Bot is running...")
    app.run_polling()
