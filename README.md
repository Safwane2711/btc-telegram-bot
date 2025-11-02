# BTC Telegram Bot
This project is a Python script that sends the current Bitcoin price to a Telegram chat. It uses the free CoinGecko API to fetch:
- Bitcoin price in USD
- 24-hour price change (percentage)

## 1. Local Setup
a) Clone the repository:
git clone https://github.com/Safwane2711/btc-telegram-bot.git
cd btc-telegram-bot

b) Install dependencies:
pip install -r requirements.txt

c) Create a `.env` file (based on `.env.example`) and add:
COINGECKO_API_KEY=your_api_key
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

d) Run the bot:
python main.py

The bot will send a price update immediately, then every hour.

## 2. Deploy on Railway (Cloud)
1. Push this project to GitHub
2. Go to https://railway.app and create a new project
3. Connect your GitHub repository
4. Add environment variables from `.env` in Railway
5. Set the start command:
python main.py

Once deployed, the bot runs 24/7, even if your computer is turned off.

## 3. Possible Improvements
- Add EUR or multiple currencies
- Save price data to a CSV file
- Add Telegram commands (/price, /help, etc.)
- Generate daily summary or price graphs

## Author
Project by Safwane Eidel, created to learn Python.
