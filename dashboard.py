import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import yaml
from datetime import datetime
from dotenv import load_dotenv
from src.agent import EnergyTradingAgent
from src.data_loader import MarketDataLoader
from src.analytics import calculate_volatility

# Configuration & Setup
with open("config/settings.yaml", "r") as f:
    config = yaml.safe_load(f)

st.set_page_config(page_title="Energy Trading Dashboard", layout="wide", page_icon="⚡")
load_dotenv()


# Map volatility thresholds for easy access
thresholds = config['volatility_thresholds']
VOL_THRESHOLDS = {
    "CRITICAL_WAR": thresholds['critical'],
    "HIGH_TACTICAL": thresholds['high'],
    "NOISE_LEVEL": thresholds['noise']
}


st.title("⚡ Energy Trading Dashboard")

# Layout: 2/3 Quantitative (Charts) | 1/3 Qualitative (AI News)
col_charts, col_news = st.columns([2, 1], gap="medium")

# Initialize Loader
loader = MarketDataLoader()
primary_ticker = config['market']['primary_ticker']
raw_data = yf.download(primary_ticker, period="2y", progress=False)

# ==============================================================================
# LEFT COLUMN: QUANTITATIVE ANALYSIS (Charts & Metrics)
# ==============================================================================
with col_charts:
    st.subheader("📈 Market Reality")
    
    if isinstance(raw_data.columns, pd.MultiIndex):
        raw_data.columns = raw_data.columns.get_level_values(0)

    if not raw_data.empty:
        # Apply centralized analytics logic
        df = calculate_volatility(raw_data)
        
        # Extract latest data points
        last_day = df.iloc[-1]
        last_date = df.index[-1]
        current_vol = last_day['Vol_Pct']
        current_price = last_day['Close']
        
        # Dynamic label for the date
        if last_date.date() == datetime.now().date():
            vol_label = "Today's Volatility"
        else:
            vol_label = f"Volatility ({last_date.strftime('%a %d')})"

        # Trend Calculation (vs Noise Level)
        last_month_vol = df['Vol_Pct'].tail(22).mean()
        trend_delta = last_month_vol - VOL_THRESHOLDS["NOISE_LEVEL"]
        trend_icon = "↗️ Heating Up" if trend_delta > 0 else "↘️ Cooling Down"

        
        # Market Regime Determination
        if current_vol > VOL_THRESHOLDS["CRITICAL_WAR"]:
            status = "🔴 DEFCON 1 (WAR/CRISIS)"
        elif current_vol > VOL_THRESHOLDS["HIGH_TACTICAL"]:
            status = "🟠 HIGH VOLATILITY"
        elif current_vol > VOL_THRESHOLDS["NOISE_LEVEL"]:
            status = "🟡 ACTIVE MARKET"
        else:
            status = "🟢 NOISE / CALM"

       # Key Metrics Display
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Price", f"${current_price:.3f}")
        c2.metric(vol_label, f"{current_vol:.2f}%", delta=f"{current_vol - VOL_THRESHOLDS['NOISE_LEVEL']:.2f}% vs Avg", delta_color="off")
        c3.metric("Trend (1M)", f"{last_month_vol:.2f}%", delta=trend_icon)
        c4.info(f"Status : {status}")
        

        # Primary Chart (Candlestick)
        # Timeframe selector
        time_frame = st.pills("Timeframe", ["1M", "3M", "6M", "1Y"], default="3M", selection_mode="single", label_visibility="collapsed")
        if not time_frame: time_frame = "3M"
        
        lookback_map = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365}
        lookback = lookback_map.get(time_frame, 90)
        
        df_plot = df.tail(lookback)

        fig = go.Figure(data=[go.Candlestick(x=df_plot.index, open=df_plot['Open'], high=df_plot['High'], low=df_plot['Low'], close=df_plot['Close'], name="Natural Gas")])
        
        # Add Annotation for Critical Volatility Events
        if current_vol > VOL_THRESHOLDS["HIGH_TACTICAL"]:
            alert_color = "red" if current_vol > VOL_THRESHOLDS["CRITICAL_WAR"] else "orange"
            alert_msg = "CRITICAL" if current_vol > VOL_THRESHOLDS["CRITICAL_WAR"] else "HIGH VOL"
            fig.add_annotation(x=df_plot.index[-1], y=df_plot['High'].iloc[-1], text=f"⚠️ {alert_msg}", showarrow=True, arrowhead=1, ax=0, ay=-40, bgcolor=alert_color, bordercolor=alert_color, font=dict(color="white"))

        fig.update_layout(title=dict(text=f"{primary_ticker} Futures", font=dict(size=18, color="white")), yaxis_title="Price", template="plotly_dark", height=450, margin=dict(l=0, r=0, t=40, b=0), xaxis=dict(rangeslider=dict(visible=False)))
        st.plotly_chart(fig, use_container_width=True)

        # Secondary Indicators (Correlation & RSI)
        st.caption("📊 Deep Dive Indicators")
        col_a, col_b = st.columns(2)
        
        with col_a: # Correlation Analysis
            
            # Compare with Secondary Ticker (e.g., Oil)
            secondary_ticker = config['market']['secondary_ticker']
            oil_data = yf.download(secondary_ticker, period="2y", progress=False)
            if isinstance(oil_data.columns, pd.MultiIndex): oil_data.columns = oil_data.columns.get_level_values(0)
            
            # Align data on common dates
            common_index = df_plot.index.intersection(oil_data.index)
            gas_aligned = df_plot.loc[common_index]['Close']
            oil_aligned = oil_data.loc[common_index]['Close']
            
            # Normalize to percentage change for comparison
            gas_norm = (gas_aligned / gas_aligned.iloc[0] - 1) * 100
            oil_norm = (oil_aligned / oil_aligned.iloc[0] - 1) * 100
            
            fig_corr = go.Figure()
            fig_corr.add_trace(go.Scatter(x=common_index, y=gas_norm, mode='lines', name='Gas', line=dict(color='#00B5F7')))
            fig_corr.add_trace(go.Scatter(x=common_index, y=oil_norm, mode='lines', name='Oil', line=dict(color='#FFD700')))
            fig_corr.update_layout(template="plotly_dark", height=200, margin=dict(l=0, r=0, t=30, b=0), showlegend=True, title="Oil (Yellow) vs Gas (Blue) - Normalized %")
            st.plotly_chart(fig_corr, use_container_width=True)

        with col_b: # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            rsi_plot = rsi.tail(len(df_plot))
            
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=df_plot.index, y=rsi_plot, name='RSI', line=dict(color='#9D00FF')))
            fig_rsi.add_hline(y=70, line_dash="dot", line_color="red")
            fig_rsi.add_hline(y=30, line_dash="dot", line_color="green")
            fig_rsi.update_layout(template="plotly_dark", height=200, yaxis=dict(range=[0, 100]), margin=dict(l=0, r=0, t=30, b=0), showlegend=True, title="⚡ RSI Indicator (Overbought > 70)")
            st.plotly_chart(fig_rsi, use_container_width=True)

# ==============================================================================
# RIGHT COLUMN: QUALITATIVE ANALYSIS (AI News Feed)
# ==============================================================================
with col_news:
    st.subheader("🤖 AI Intel Feed")
    
    # Search controls
    default_topic = config['agent'].get('search_topic_default', "Natural Gas OR LNG")
    topic = st.text_input("Topic", value=default_topic, label_visibility="collapsed")
    
    # Refresh Button (Clears session state to force new fetch)
    if st.button("⚡ REFRESH MARKET NEWS", type="primary", use_container_width=True):
        if 'news_signals' in st.session_state:
            del st.session_state['news_signals']
    
    st.divider()

    # News Fetching Logic
    def fetch_and_analyze_news(search_topic):
        agent = EnergyTradingAgent()
        signals = []
        with st.spinner(f"AI Agent analyzing global wires for: {search_topic}..."):

            news_items = loader.fetch_real_news(topic=search_topic)
            
            for item in news_items:
                signal = agent.analyze_news(item['text'])
                # Filter out noise
                if signal and signal.category.value != "Other / Noise":
                    signals.append(signal)
        return signals


    # Persistence: Load news only if not already in Session State
    if 'news_signals' not in st.session_state:
        st.session_state['news_signals'] = fetch_and_analyze_news(topic)

    # Display Logic 
    signals_to_display = st.session_state['news_signals']

    if signals_to_display:
        for signal in signals_to_display:
            # Determine visual style based on sentiment
            border_color = "red" if signal.sentiment == "Bearish" else "green" if signal.sentiment == "Bullish" else "grey"
            icon = "🐻" if signal.sentiment == "Bearish" else "🐂" if signal.sentiment == "Bullish" else "⚖️"
            
            with st.container(border=True):
                # Header
                st.markdown(f"**{signal.category.value}** • {icon} {signal.sentiment}")
                
                # Headline
                st.markdown(f"#### {signal.headline}")
                
                # Summary
                st.caption(signal.summary)
                
                # Recommendation
                st.markdown(f"**👉 Action:** `{signal.trading_recommendation}`")
    else:
        st.info("No critical market signals found at this moment.")
                