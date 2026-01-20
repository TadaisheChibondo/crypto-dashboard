import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="CryptoLive Pro", page_icon="📈", layout="wide")

st.title("📈 CryptoLive Pro: Technical Analysis")

st.sidebar.header("Settings")
coin_id = st.sidebar.selectbox("Select Coin", ["bitcoin", "ethereum", "solana", "ripple"])
currency = st.sidebar.selectbox("Select Currency", ["usd", "eur", "gbp"])

# --- NEW SETTING: MOVING AVERAGE WINDOW ---
# Let the user decide how "smooth" the trend line should be
sma_window = st.sidebar.slider("SMA Window (Hours)", min_value=5, max_value=50, value=20)

def get_market_data(coin, vs_curr):
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency={vs_curr}&ids={coin}&sparkline=true"
    try:
        response = requests.get(url)
        data = response.json()
        return data[0]
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

if st.button("Analyze Market"):
    data = get_market_data(coin_id, currency)
    
    if data:
        # 1. PREPARE THE DATA
        # CoinGecko sparklines are usually hourly data for the last 7 days
        price_history = data['sparkline_in_7d']['price']
        
        # Create a Pandas DataFrame (The Excel sheet of Python)
        df = pd.DataFrame({'price': price_history})
        
        # 2. CALCULATE INDICATORS (The Algo Trading Logic)
        # Calculate the Simple Moving Average (SMA)
        df['SMA'] = df['price'].rolling(window=sma_window).mean()
        
        # Determine the Trend (Bullish if Price > SMA)
        last_price = df['price'].iloc[-1]
        last_sma = df['SMA'].iloc[-1]
        
        trend = "BULLISH 🟢" if last_price > last_sma else "BEARISH 🔴"
        
        # --- DISPLAY METRICS ---
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Price", f"{data['current_price']} {currency.upper()}")
        col2.metric("Market Trend", trend) # The new "Smart" metric
        col3.metric("24h Change", f"{data['price_change_percentage_24h']:.2f}%")

        # --- PLOT THE CHART (Price vs SMA) ---
        fig = go.Figure()

        # Line 1: The Price (Green/Red area)
        fig.add_trace(go.Scatter(
            y=df['price'], 
            mode='lines', 
            name='Price',
            line=dict(color='#00CC96' if last_price > last_sma else '#EF553B', width=2)
        ))

        # Line 2: The SMA (Yellow trend line)
        fig.add_trace(go.Scatter(
            y=df['SMA'], 
            mode='lines', 
            name=f'SMA {sma_window}',
            line=dict(color='#FFA15A', width=2, dash='dash') # Dashed orange line
        ))
        
        fig.update_layout(
            title=f"{coin_id.capitalize()} Price vs {sma_window}-Hour SMA",
            xaxis_title="Hours Ago (Last 7 Days)",
            yaxis_title=f"Price ({currency.upper()})",
            template="plotly_dark", # Dark mode for that "Pro Trader" look
            margin=dict(l=0, r=0, t=40, b=0),
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show the raw data table at the bottom for verification
        with st.expander("View Analysis Data"):
            st.dataframe(df.tail(10)) # Show just the last 10 rows