import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import time
import requests
from datetime import datetime

# ===== CONFIGURATION =====
TICKER = "NIFTYBEES.NS"
REFRESH_INTERVAL = 300  # seconds (5 minutes)
TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
CHAT_ID = st.secrets["CHAT_ID"]

# ===== HELPER FUNCTIONS =====
def fetch_data():
    """Fetch real-time 5-min data"""
    return yf.download(TICKER, period="1d", interval="5m")

def calculate_regime(df):
    """Calculate market regime using simplified rules"""
    df.ta.adx(length=14, append=True)
    df.ta.sma(length=50, append=True)
    df.ta.sma(length=200, append=True)
    df.ta.atr(length=14, append=True)
    
    adx = df["ADX_14"].iloc[-1]
    sma_ratio = df["SMA_50"].iloc[-1] / df["SMA_200"].iloc[-1]
    atr_ratio = df["ATRr_14"].iloc[-1] / df["SMA_50"].iloc[-1]
    
    if adx > 25:
        return "STRONG_BULL" if sma_ratio > 1.05 else "STRONG_BEAR"
    elif atr_ratio > 0.03:
        return "VOLATILE"
    elif adx < 20:
        return "SIDEWAYS"
    else:
        return "TRANSITION"

def send_telegram_alert(message):
    """Send alert via Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, params=params)

# ===== STRATEGY MAPPING =====
STRATEGY_MAP = {
    "STRONG_BULL": {"strategy": "DMA Momentum", "allocation": "100%"},
    "VOLATILE": {"strategy": "Mean-Reversion", "allocation": "80%"},
    "STRONG_BEAR": {"strategy": "Cash", "allocation": "0%"},
    "SIDEWAYS": {"strategy": "Mean-Reversion", "allocation": "50%"},
    "TRANSITION": {"strategy": "Hybrid", "allocation": "50%"}
}

# ===== STREAMLIT APP =====
st.set_page_config(page_title="NIFTYBEES Regime Dashboard", layout="wide")

# Sidebar configuration
st.sidebar.header("Configuration")
bull_threshold = st.sidebar.slider("Bull SMA Ratio", 1.03, 1.10, 1.05)
vol_threshold = st.sidebar.slider("Volatility Threshold", 0.02, 0.05, 0.03)

# Main dashboard
st.title("📊 NIFTYBEES Real-Time Market Regime Dashboard")
status_col, strategy_col = st.columns([2, 1])

# Initialize session state
if "last_regime" not in st.session_state:
    st.session_state.last_regime = None
if "last_update" not in st.session_state:
    st.session_state.last_update = datetime.now()

# Main update loop
while True:
    try:
        df = fetch_data()
        current_regime = calculate_regime(df)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Display regime status
        with status_col:
            st.subheader(f"Current Regime: :red[{current_regime}]")
            st.caption(f"Last update: {timestamp}")
            
            # Display indicators
            st.metric("ADX(14)", f"{df['ADX_14'].iloc[-1]:.1f}")
            st.metric("SMA Ratio", f"{df['SMA_50'].iloc[-1]/df['SMA_200'].iloc[-1]:.4f}")
            st.metric("ATR Ratio", f"{df['ATRr_14'].iloc[-1]/df['SMA_50'].iloc[-1]:.4f}")
            
            # Display chart
            st.line_chart(df[["Close", "SMA_50", "SMA_200"]].tail(50))
        
        # Display strategy recommendation
        with strategy_col:
            st.subheader("Recommended Strategy")
            strategy = STRATEGY_MAP[current_regime]
            st.metric("Allocation", strategy["allocation"])
            st.metric("Strategy", strategy["strategy"])
            
            st.subheader("Action Plan")
            if current_regime in ["VOLATILE", "SIDEWAYS"]:
                st.write("- Buy 1/3 when Z-score < -1")
                st.write("- Scale-in on new lows")
                st.write("- Exit above 5-day EMA")
            elif current_regime == "STRONG_BULL":
                st.write("- Enter when 50EMA > 200EMA")
                st.write("- Exit when 50EMA < 200EMA")
            else:
                st.write("- Maintain cash position")
                st.write("- Monitor for regime change")
        
        # Send alert on regime change
        if st.session_state.last_regime and current_regime != st.session_state.last_regime:
            alert_msg = f"🚨 REGIME CHANGE: {st.session_state.last_regime} → {current_regime}"
            send_telegram_alert(alert_msg)
            st.toast(alert_msg, icon="🚨")
            
        st.session_state.last_regime = current_regime
        st.session_state.last_update = timestamp
        
        time.sleep(REFRESH_INTERVAL)
        st.experimental_rerun()
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        time.sleep(60)
