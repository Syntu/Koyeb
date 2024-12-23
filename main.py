import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Flask App for Webhook
app = Flask(__name__)

# Retrieve Telegram Bot Token and Webhook URL from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN or not WEBHOOK_URL:
    raise ValueError("Missing BOT_TOKEN or WEBHOOK_URL in environment variables")

# Global Data Storage (Refresh हुने ठाउँ)
latest_data = {
    "symbol_data": {},
    "general_data": {}
}

# Scrape Sharesansar Data for Specific Symbol
def scrape_symbol_data(symbol_name):
    url = "https://www.sharesansar.com/live-trading"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if cells and cells[1].text.strip().lower() == symbol_name.lower():
            data = {
                "Symbol": cells[1].text.strip(),
                "LTP": cells[2].text.strip(),
                "Change Percent": cells[4].text.strip(),
                "Day High": cells[6].text.strip(),
                "Day Low": cells[7].text.strip(),
                "Volume": cells[8].text.strip(),
            }
            print(f"Scraped data for {symbol_name}: {data}")
            return data
    print(f"No data found for {symbol_name}")
    return None

# Scrape Today's Share Price Summary
def scrape_today_share_price():
    url = "https://www.sharesansar.com/today-share-price"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table_data = soup.find_all("td")
    data = {
        "Turn Over": table_data[10].text.strip(),
        "52 Week High": table_data[19].text.strip(),
        "52 Week Low": table_data[20].text.strip(),
    }
    print(f"Today's share price summary: {data}")
    return data

# Function to Refresh Data Every 10 Minutes
def refresh_data():
    global latest_data
    print("Refreshing data from Sharesansar...")
    latest_data["general_data"] = scrape_today_share_price()
    print(f"Latest general data: {latest_data['general_data']}")

# Telegram Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "Welcome 🙏🙏 to Syntoo's NEPSE💹bot!\n"
            "के को डाटा चाहियो भन्नुस ?\n"
            "म फ्याट्टै खोजिहाल्छु 😂😅\n"
            "Symbol दिनुस जस्तै:- NMB, SHINE, SHPC, SWBBL"
        )
    except Exception as e:
        print(f"Error in start command: {e}")

# Unified Data Handler
async def handle_symbol_or_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        global latest_data
        symbol_name = update.message.text.strip()
        if not symbol_name or symbol_name.startswith("/"):
            return
        
        print(f"Received symbol: {symbol_name}")
        symbol_data = scrape_symbol_data(symbol_name)
        general_data = latest_data.get("general_data", {})

        if symbol_data:
            message = (
                f"Symbol: {symbol_data['Symbol']}\n"
                f"LTP: {symbol_data['LTP']}\n"
                f"Change Percent: {symbol_data['Change Percent']}\n"
                f"Day High: {symbol_data['Day High']}\n"
                f"Day Low: {symbol_data['Day Low']}\n"
                f"Volume: {symbol_data['Volume']}\n"
                f"Turn Over: {general_data.get('Turn Over', 'N/A')}\n"
                f"52 Week High: {general_data.get('52 Week High', 'N/A')}\n"
                f"52 Week Low: {general_data.get('52 Week Low', 'N/A')}"
            )
        else:
            message = (
                f"Symbol '{symbol_name}' ल्या, फेला परेन त 🤗🤗।\n"
                "नआत्तिनु Symbol राम्रो सङ्ग फेरि हान्नु।\n"
                "म जसरी पनि डाटा दिन्छु।"
            )
        await update.message.reply_text(message)
    except Exception as e:
        print(f"Error in handle_symbol_or_input: {e}")

# Initialize Application
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

# Set Webhook
tg_app.bot.set_webhook(WEBHOOK_URL)

# Telegram Webhook Endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        update_data = request.get_json(force=True)
        if update_data is None:
            return "Invalid JSON data", 400
        update = Update.de_json(update_data, tg_app.bot)
        tg_app.update_queue.put(update)
        print(f"Webhook processed: {update}")
        return "OK", 200
    except Exception as e:
        print(f"Error in webhook processing: {e}")
        return "Internal Server Error", 500

if __name__ == "__main__":
    try:
        # Run Flask App
        print("Running Flask app...")
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8443)), debug=True)
    except Exception as e:
        print(f"Error in main: {e}")
