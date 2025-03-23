import os
import asyncio
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "YOUR_BOT_TOKEN"
ADMIN_CHAT_ID = "YOUR_ADMIN_CHAT_ID"

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Dictionary to store user responses
user_data = {}

# Function to start the bot menu
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Web Development", callback_data="web_dev")],
        [InlineKeyboardButton("Digital Marketing", callback_data="digital_marketing")],
        [InlineKeyboardButton("SEO Optimization", callback_data="seo")],
        [InlineKeyboardButton("Graphic Design", callback_data="graphic_design")],
        [InlineKeyboardButton("Other", callback_data="other")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("👋 Welcome! What service do you need?", reply_markup=reply_markup)

# Function to handle button clicks
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_data[query.from_user.id] = {"service": query.data, "state": "waiting_for_details"}

    service_name = {
        "web_dev": "Web Development",
        "digital_marketing": "Digital Marketing",
        "seo": "SEO Optimization",
        "graphic_design": "Graphic Design",
        "other": "Other"
    }.get(query.data, "Unknown Service")

    await query.message.reply_text(f"🖥️ You selected *{service_name}*. Please describe your project.")

# Function to collect project details
async def collect_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in user_data and user_data[user_id]["state"] == "waiting_for_details":
        user_data[user_id]["details"] = update.message.text
        user_data[user_id]["state"] = "waiting_for_contact"

        await update.message.reply_text("📞 Please provide your contact details (Email/Phone).")
    else:
        await update.message.reply_text("⚠️ Please select a service first by using /start.")

# Function to collect contact details and send data
async def collect_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id in user_data and user_data[user_id]["state"] == "waiting_for_contact":
        user_data[user_id]["contact"] = update.message.text

        service = user_data[user_id]["service"]
        details = user_data[user_id]["details"]
        contact = user_data[user_id]["contact"]
        username = update.message.from_user.username or "Unknown User"

        message = (
            f"📩 **New Service Request**\n\n"
            f"👤 **User**: @{username}\n"
            f"🔹 **Service**: {service}\n"
            f"📝 **Details**: {details}\n"
            f"📞 **Contact**: {contact}"
        )

        # Send request to admin
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=message)

        await update.message.reply_text("✅ Thanks! Your request has been saved and sent. We'll contact you soon.")

        # Clear user data after submission
        del user_data[user_id]
    else:
        await update.message.reply_text("⚠️ Please describe your project first.")

# Function to run the bot
async def run_bot():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_details))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_contact))

    await app.run_polling()

# Start Flask and bot together
if __name__ == "__main__":
    # Start Flask in a separate thread
    from threading import Thread
    Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))).start()

    # Start Telegram bot
    asyncio.run(run_bot())
