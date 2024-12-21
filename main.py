import requests
from bs4 import BeautifulSoup
from datetime import datetime, time
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Telegram Bot Token
BOT_TOKEN = "YOUR_BOT_TOKEN"

# Scrape Sharesansar Data
def scrape_live_trading():
    url = "https://www.sharesansar.com/live-trading"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Extract table data
    table_data = soup.find_all("td")
    data = {
        "Symbol": table_data[1].text.strip(),
        "LTP": table_data[2].text.strip(),
        "Change Percent": table_data[4].text.strip(),
        "Day High": table_data[6].text.strip(),
        "Day Low": table_data[7].text.strip(),
        "Volume": table_data[8].text.strip(),
    }
    return data

def scrape_today_share_price():
    url = "https://www.sharesansar.com/today-share-price"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Extract table data
    table_data = soup.find_all("td")
    data = {
        "Turn Over": table_data[10].text.strip(),
        "52 Week High": table_data[19].text.strip(),
        "52 Week Low": table_data[20].text.strip(),
    }
    return data

# Combine both scrapes
def get_stock_data():
    live_data = scrape_live_trading()
    today_price = scrape_today_share_price()
    return {**live_data, **today_price}

# Schedule Function
def schedule_stock_data():
    now = datetime.now()
    trading_start = time(10, 45)
    trading_end = time(15, 5)
    
    if trading_start <= now.time() <= trading_end:
        return get_stock_data()
    else:
        return get_stock_data()  # Return last available data

# Telegram Command Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Stock Market Bot! Use /data to get the latest stock info.")

async def get_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = schedule_stock_data()
    message = (
        f"Symbol: {data['Symbol']}\n"
        f"LTP: {data['LTP']}\n"
        f"Change Percent: {data['Change Percent']}\n"
        f"Day High: {data['Day High']}\n"
        f"Day Low: {data['Day Low']}\n"
        f"Volume: {data['Volume']}\n"
        f"Turn Over: {data['Turn Over']}\n"
        f"52 Week High: {data['52 Week High']}\n"
        f"52 Week Low: {data['52 Week Low']}"
    )
    await update.message.reply_text(message)

# Main Function
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("data", get_data))
    
    app.run_polling()