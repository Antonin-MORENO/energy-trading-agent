import os
import requests
import yfinance as yf
import yaml
from datetime import datetime, timedelta  # <--- INDISPENSABLE pour le voyage dans le temps

class MarketDataLoader:
    """
    Handles data ingestion from external APIs:
    1. NewsAPI for textual market intelligence.
    2. Yahoo Finance for quantitative market data.
    """
    def __init__(self):
        # Load API keys
        self.news_api_key = os.getenv("NEWS_API_KEY")

        # Load configuration settings
        with open("config/settings.yaml", "r") as f:
            self.config = yaml.safe_load(f)
    
    def fetch_real_news(self, topic="energy trading", days_ago=0):
        """
        Fetches news articles from NewsAPI.

        Args:
            topic (str): The search query (e.g., "Natural Gas").
            days_ago (int): 0 for real-time news, >0 for historical simulation (backtesting).
        """
        url = "https://newsapi.org/v2/everything"
        
        
        
        # 1. Date Management (Real-time vs Backtesting)
        if days_ago > 0:
            # Historical Mode: Calculate specific past date
            target_date = datetime.now() - timedelta(days=days_ago)
            date_str = target_date.strftime('%Y-%m-%d')
            
            
            
            
            params = {
                "q": topic,
                "language": "en",
                "sortBy": "relevancy", 
                "apiKey": self.news_api_key,
                "pageSize": 5,
                "from": date_str,  
                "to": date_str
            }
        else:
            # Real-time Mode (Default)
            params = {
                "q": topic,
                "language": "en",
                "sortBy": "relevancy",
                "apiKey": self.news_api_key,
                "pageSize": 5
            }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if data.get("status") != "ok":
                print(f"⚠️ API Error: {data.get('message')}")
                return []

            # 2. Format Results
            formatted_news = []
            for article in data.get('articles', []):
                formatted_news.append({
                    "text": article['title'] + ". " + (article['description'] or ""),
                    "date": article['publishedAt']
                })
                
            return formatted_news

        except Exception as e:
            print(f"Error fetching news: {e}")
            return []

    def fetch_market_prices(self):
        """
        Retrieves recent pricing data for primary and secondary assets defined in settings.
        Returns:
            pd.DataFrame: 'Close' prices for the requested tickers.
        """
        
        primary = self.config['market']['primary_ticker']
        secondary = self.config['market']['secondary_ticker']
        tickers = [primary, secondary]
        
        # Download 5 days of hourly data for correlation analysis
        data = yf.download(tickers, period="5d", interval="1h", progress=False)
        return data['Close']