import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request

app = Flask(__name__)

# Telegram Bot Token र Webhook URL
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = "https://tg1nepse.onrender.com/webhook"

# Global Data Storage
latest_data = {"general_data": {}}

# Refresh Data Function
def refresh_data():
    global latest_data
    print("Refreshing data...")
    latest_data["general_data"] = scrape_today_share_price()

@app.route("/", methods=["GET"])
def home():
    return "This is Syntoo's NEPSE bot. Webhook is active!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), tg_app.bot)
    tg_app.update_queue.put(update)
    return "OK", 200

def scrape_symbol_data(symbol_name):
    url = "https://www.sharesansar.com/live-trading"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if cells and cells[1].text.strip().lower() == symbol_name.lower():
            return {
                "Symbol": cells[1].text.strip(),
                "LTP": cells[2].text.strip(),
                "Change Percent": cells[4].text.strip(),
                "Day High": cells[6].text.strip(),
                "Day Low": cells[7].text.strip(),
                "Volume": cells[8].text.strip(),
            }
    return None

def scrape_today_share_price():
    url = "https://www.sharesansar.com/today-share-price"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    table_data = soup.find_all("td")
    return {
        "Turn Over": table_data[10].text.strip(),
        "52 Week High": table_data[19].text.strip(),
        "52 Week Low": table_data[20].text.strip(),
    }

# Telegram Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome 🙏🙏 to Syntoo's NEPSE💹bot! Symbol दिनुस जस्तै: NMB, SHINE"
    )

async def handle_symbol_or_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global latest_data
    symbol_name = update.message.text.strip()
    symbol_data = scrape_symbol_data(symbol_name)
    general_data = latest_data["general_data"]

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
        message = f"Symbol '{symbol_name}' फेला परेन। फेरि प्रयास गर्नुहोस्।"
    await update.message.reply_text(message)

if __name__ == "__main__":
    tg_app = ApplicationBuilder().token(BOT_TOKEN).build()
    tg_app.add_handler(CommandHandler("start", start))
    tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol_or_input))

    scheduler = BackgroundScheduler()
    scheduler.add_job(refresh_data, "interval", minutes=10)
    scheduler.start()

    refresh_data()
    tg_app.bot.set_webhook(WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8443)))
