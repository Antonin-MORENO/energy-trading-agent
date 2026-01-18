import pandas as pd

def calculate_volatility(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates volatility metrics based on the True Range (TR) to account for price gaps.

    Args:
        df (pd.DataFrame): OHLC market data (Open, High, Low, Close).

    Returns:
        pd.DataFrame: Input DataFrame with added 'True_Range' and 'Vol_Pct' columns.
    """
    df = df.copy()
    
    # Flatten MultiIndex columns if present (handling specific YFinance output format)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
        
    df['Prev_Close'] = df['Close'].shift(1)
    
    # True Range is the maximum of the three components
    df['R1'] = abs(df['High'] - df['Low'])
    df['R2'] = abs(df['High'] - df['Prev_Close'])
    df['R3'] = abs(df['Low'] - df['Prev_Close'])
    df['True_Range'] = df[['R1', 'R2', 'R3']].max(axis=1)
    
    # Normalize volatility as a percentage of the previous close for comparability
    df['Vol_Pct'] = (df['True_Range'] / df['Prev_Close']) * 100
    
    return df.dropna()