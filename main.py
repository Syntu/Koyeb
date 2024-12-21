import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request

# Flask App for Webhook
app = Flask(__name__)

# Telegram Bot Token र Webhook URL
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = f"https://tg1nepse.onrender.com/webhook"

# Global Data Storage (Refresh हुने ठाउँ)
latest_data = {
    "general_data": {}
}

# Scrape Today's Share Price Summary
def scrape_today_share_price():
    url = "https://www.sharesansar.com/today-share-price"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table_data = soup.find_all("td")
    if table_data:
        data = {
            "Turn Over": table_data[10].text.strip(),
            "52 Week High": table_data[19].text.strip(),
            "52 Week Low": table_data[20].text.strip(),
        }
        return data
    return {"Turn Over": "N/A", "52 Week High": "N/A", "52 Week Low": "N/A"}

# Function to Refresh Data Every 10 Minutes
def refresh_data():
    global latest_data
    print("Refreshing data from Sharesansar...")
    latest_data["general_data"] = scrape_today_share_price()

# Telegram Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome 🙏🙏 to Syntoo's NEPSE💹bot!\n"
        "के को डाटा चाहियो भन्नुस ?\n"
        "म फ्याट्टै खोजिहाल्छु 😂😅\n"
        "कुनै पनि Symbol दिनुस, जस्तै: NMB, SHINE, SHPC, SWBBL"
    )

# Unified Data Handler
async def handle_symbol_or_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global latest_data
    symbol_name = update.message.text.strip()
    general_data = latest_data["general_data"]

    if general_data:
        message = (
            f"Turn Over: {general_data['Turn Over']}\n"
            f"52 Week High: {general_data['52 Week High']}\n"
            f"52 Week Low: {general_data['52 Week Low']}\n"
        )
    else:
        message = "डाटा उपलब्ध छैन। कृपया केही समयपछि प्रयास गर्नुहोस्।"
    
    await update.message.reply_text(message)

# Telegram Webhook Endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), tg_app.bot)
    tg_app.update_queue.put(update)
    return "OK", 200

if __name__ == "__main__":
    # Initialize Telegram Application
    tg_app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Add Command Handlers
    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol_or_input))

    # Initialize Scheduler
    scheduler = BackgroundScheduler()
    scheduler.add_job(refresh_data, "interval", minutes=10)
    scheduler.start()

    # Refresh Data Initially
    refresh_data()

    # Set Telegram Webhook
    tg_app.bot.set_webhook(WEBHOOK_URL)

    # Run Flask App with Gunicorn
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8443)))
