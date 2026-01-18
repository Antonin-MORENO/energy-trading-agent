import yfinance as yf
import numpy as np
import pandas as pd
from ruamel.yaml import YAML
from datetime import datetime, timedelta
from analytics import calculate_volatility

def run_calibration(ticker="NG=F"):
    """
    Calculates volatility thresholds (Noise, High, Critical) based on historical data
    and automatically updates the settings.yaml configuration.
    """
    print(f"📉 Starting Calibration: Double Regime + Gaps ({ticker})...")
    
    # 1. Download 5 years of data to capture long-term tail risks
    df = yf.download(ticker, period="5y", progress=False)
    
    # Flatten MultiIndex columns (YFinance specific fix)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    df = df.dropna()
    df = calculate_volatility(df)

    
    # 2. Statistical Analysis
    # A. Long Term: 95th percentile over 5 years (Defines "Crisis/War" threshold)
    long_term_95 = np.percentile(df['Vol_Pct'], 95)
    
    # B. Short Term: Recent 6 months market regime (Defines "Tactical" thresholds)
    start_date_short = datetime.now() - timedelta(days=180)
    df_short = df[df.index >= start_date_short]
    
    # Safety check for insufficient recent data
    if df_short.empty:
        print("⚠️ Insufficient recent data. Fallback to long-term metrics.")
        short_term_95 = long_term_95
        short_term_avg = np.mean(df['Vol_Pct'])
    else:
        short_term_95 = np.percentile(df_short['Vol_Pct'], 95)
        short_term_avg = np.mean(df_short['Vol_Pct'])

    # 3. Console Output
    print("\n" + "="*60)
    print("📊 CALIBRATION RESULTS")
    print("="*60)
    print(f"1. Noise Level (Avg)      : {short_term_avg:.2f}%")
    print(f"2. High Volatility (Tactical): {short_term_95:.2f}%  <-- Pour l'alerte 'High Volatility'")
    print(f"3. Critical Level (Crisis)   : {long_term_95:.2f}%  <-- Pour l'alerte 'CRITICAL'")
    print("-" * 60)
    print("👉 Metrics account for Monday morning gaps.")
    print("="*60)
    
    # 4. Update Configuration File
    file_path = "config/settings.yaml"
    yaml = YAML()

    # Load config
    with open(file_path, "r") as f:
        config = yaml.load(f)

    # Update values
    vol_section = config.setdefault('volatility_thresholds', {})

    vol_section['critical'] = float(f"{long_term_95:.2f}")
    vol_section['high']     = float(f"{short_term_95:.2f}")
    vol_section['noise']    = float(f"{short_term_avg:.2f}")

    # Save changes
    with open(file_path, "w") as f:
        yaml.dump(config, f)

    print(f"✅ Configuration updated successfully: {file_path}")
          
if __name__ == "__main__":
    run_calibration()