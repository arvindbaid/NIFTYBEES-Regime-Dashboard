# NIFTYBEES Real-Time Regime Dashboard

[![Streamlit Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-dashboard.streamlit.app)

Real-time market regime detection system for NIFTYBEES with Telegram alerts.

## Features
- Automatic regime classification (Bull/Bear/Volatile/Sideways)
- Strategy recommendations
- Telegram alert integration
- Mobile-responsive dashboard

## Setup Guide
1. **Create Telegram Bot**:
   - Message @BotFather in Telegram
   - Send `/newbot` and follow prompts
   - Copy API token

2. **Get Chat ID**:
   - Visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
   - Send message to your bot
   - Find `chat.id` in JSON response

3. **Deploy to Streamlit**:
   ```bash
   # Clone repository
   git clone https://github.com/yourusername/NIFTYBEES-Regime-Dashboard
   
   # Create new Streamlit app
   https://share.streamlit.io/
   
   # Configure secrets
   TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
   CHAT_ID = "YOUR_CHAT_ID"
