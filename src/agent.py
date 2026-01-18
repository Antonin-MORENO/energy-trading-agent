import yaml
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from src.schema import MarketSignal, EventCategory

load_dotenv()

class EnergyTradingAgent:
    """
    AI Agent responsible for analyzing energy market news and extracting 
    structured trading signals using a Large Language Model.
    """
    def __init__(self):
        # Load configuration
        with open("config/settings.yaml", "r") as f:
            self.config = yaml.safe_load(f)

        # 1. Configure LLM
        # Set temperature to 0.0 for deterministic, logic-driven outputs
        self.llm = ChatGroq(
            model_name=self.config['model']['name'],
            temperature=0.0, 
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        
        # 2. Define System Prompt
        # Enforces specific domain logic to override general sentiment bias        
        self.system_prompt = """
        You are an expert Energy Commodities Trader (Gas, Oil, LNG).
        Your job is to analyze news and extract structured data for a trading desk.
        
        CRITICAL RULES FOR SENTIMENT (Must Override General Sentiment):
        1. SUPPLY DISRUPTION (War, Bombing, Strikes, Leaks) -> BULLISH (Prices UP).
        2. NEW SUPPLY / EXPORTS (New pipeline, Deal signed) -> BEARISH (Prices DOWN).
        3. DEMAND DESTRUCTION (Warm winter, Recession) -> BEARISH.
        
        EXAMPLES OF LOGIC:
        
        News: "Russia strikes Ukraine gas storage facility with missiles."
        -> Category: Supply Shock
        -> Sentiment: Bullish (Reason: Storage destroyed = Less supply = Higher Prices)
        
        News: "Freeport LNG terminal restarts operations ahead of schedule."
        -> Category: Supply Shock
        -> Sentiment: Bearish (Reason: More supply arriving on market)
        
        News: "US Carbon emissions rose 2%."
        -> Category: Macro Economic
        -> Sentiment: Neutral/Bearish (Reason: Regulatory risk, not a physical shock)
        """
        
        # 3. Create Prompt Template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "{text}"),
        ])
        
        # 4. Build Chain
        # Binds the prompt to the LLM and enforces the Pydantic schema (MarketSignal)
        self.chain = self.prompt | self.llm.with_structured_output(MarketSignal)

    def analyze_news(self, news_text: str) -> MarketSignal:
        """
        Processes raw news text through the LLM chain to return a structured signal.
        """
        
        try:
            signal = self.chain.invoke({"text": news_text})
            return signal
        except Exception as e:
            print(f"Error during analysis: {e}")
            return None

    def evaluate_risk(self, signal: MarketSignal):
        """
        Evaluates the category of the signal to determine if an alert is required.
        """
        
        # Define high-priority categories from schema
        critical_categories = [
            EventCategory.SUPPLY_SHOCK, 
            EventCategory.GEOPOLITICAL,
            EventCategory.WEATHER_EVENT
        ]
        
        if signal.category in critical_categories:
            return self._trigger_alert(signal)
        else:
            return self._log_info(signal)

    def _trigger_alert(self, signal: MarketSignal):
        print(f"🚨 ALERT: {signal.category.value} -> {signal.headline}")
        return "ALERT_SENT"

    def _log_info(self, signal: MarketSignal):
        print(f"ℹ️  Info: {signal.category.value} -> {signal.headline}")
        return "LOGGED"