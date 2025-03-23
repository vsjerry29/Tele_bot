from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "7934096978:AAGZG2WydqqHtYiMC1-rKnG_Rnz_-Tsx1V0"
ADMIN_CHAT_ID = "698414698"

# Dictionary to store user responses
user_data = {}

# Function to save user requests to a file
def save_request_to_file(user_id, username, service, details, contact):
    with open("requests.txt", "a", encoding="utf-8") as file:
        file.write(f"User ID: {user_id}\n")
        file.write(f"Username: @{username}\n")
        file.write(f"Service: {service}\n")
        file.write(f"Details: {details}\n")
        file.write(f"Contact: {contact}\n")
        file.write("=" * 50 + "\n")  # Separator

# Function to show the main menu
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

        # Save request to file
        save_request_to_file(user_id, username, service, details, contact)

        await update.message.reply_text("✅ Thanks! Your request has been saved and sent. We'll contact you soon.")

        # Clear user data after submission
        del user_data[user_id]
    else:
        await update.message.reply_text("⚠️ Please describe your project first.")

# Main function to start the bot
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_details))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, collect_contact))

    app.run_polling()

if __name__ == "__main__":
    main()
