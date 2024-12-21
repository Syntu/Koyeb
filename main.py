import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Telegram Bot Token (Environment Variable बाट लिन्छ)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Scrape Sharesansar Data for Specific Symbol
def scrape_symbol_data(symbol_name):
    url = "https://www.sharesansar.com/live-trading"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Extract all rows in the table
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
            return data
    return None

# Scrape Today's Share Price Summary
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

# Telegram Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome 🙏🙏 to Syntoo's NEPSE💹bot!\n"
        "के को डाटा चाहियो भन्नुस ?\n"
        "म फ्याट्टै खोजिहाल्छु 😂😅\n"
        "Symbol दिनुस जस्तै:- NMB, SHINE, SHPC, SWBBL"
    )

# Unified Data Handler
async def handle_symbol_or_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get Symbol Name from Message Text
    symbol_name = update.message.text.strip()
    
    # Check if the input is valid (avoid empty inputs or commands being processed)
    if not symbol_name or symbol_name.startswith("/"):
        return
    
    symbol_data = scrape_symbol_data(symbol_name)
    general_data = scrape_today_share_price()

    if symbol_data:
        message = (
            f"Symbol: {symbol_data['Symbol']}\n"
            f"LTP: {symbol_data['LTP']}\n"
            f"Change Percent: {symbol_data['Change Percent']}\n"
            f"Day High: {symbol_data['Day High']}\n"
            f"Day Low: {symbol_data['Day Low']}\n"
            f"Volume: {symbol_data['Volume']}\n"
            f"Turn Over: {general_data['Turn Over']}\n"
            f"52 Week High: {general_data['52 Week High']}\n"
            f"52 Week Low: {general_data['52 Week Low']}"
        )
    else:
        message = f"""Symbol '{symbol_name}' ल्या, फेला परेन त 🤗🤗।
        नआत्तिनु Symbol राम्रो सङ्ग फेरि हान्नु।
        म जसरी पनि डाटा दिन्छु।"""
    
    await update.message.reply_text(message)

# Main Function
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Command Handlers
    app.add_handler(CommandHandler("start", start))
    
    # Message Handler for Symbol Input or Direct Text (No Commands)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_symbol_or_input))
    
    # Run the Bot
    app.run_polling()
