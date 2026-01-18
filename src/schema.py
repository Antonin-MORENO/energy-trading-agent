from pydantic import BaseModel, Field, field_validator
from typing import List, Union
from enum import Enum

class EventCategory(str, Enum):
    """
    Standardized categories for market events to ensure consistent classification.
    """
    SUPPLY_SHOCK = "Supply Shock"
    WEATHER_EVENT = "Weather Event"
    MACRO_ECONOMIC = "Macro Economic"
    INVENTORY = "Inventory Report"
    GEOPOLITICAL = "Geopolitical Tension"
    OTHER = "Other / Noise"

class MarketSignal(BaseModel):
    """
    Represents a structured trading signal extracted from unstructured news text.
    This model serves as the schema for the LLM's output validation.
    """
    headline: str = Field(description="A short, catchy title.")
    
    affected_assets: Union[List[str], str] = Field(
        description="List of energy assets. If one, return a list like ['Natural Gas']."
    )
    
    # The description below acts as a strict instruction for LLM
    category: EventCategory = Field(
        description="""Classify strictly:
        - Supply Shock: PHYSICAL disruptions (Explosion, Leak, Strike, Embargo). DO NOT put 'Pollution' or 'Carbon' stats here.
        - Weather Event: Hurricane, Cold Snap, Heatwave.
        - Macro Economic: Inflation, GDP, Fed, AND Environmental/Carbon/Pollution stats.
        - Inventory Report: EIA/API storage data.
        - Geopolitical Tension: War, Treaty, Sanctions, Export Deals.
        - Other / Noise: Analyst opinions, Science discoveries, General stock market news.
        """
    )
    
    # Explicit instruction to differentiate 'Human Sentiment' from 'Market Price Action'
    sentiment: str = Field(
        description="""
        MARKET IMPACT ONLY (Ignore human emotion):
        - 'Bullish': Prices UP. (e.g. War, Pipeline Explosion, Strike, Cold Weather).
        - 'Bearish': Prices DOWN. (e.g. Peace treaty, Warm weather, New discovery, Economic crash).
        - 'Neutral': No price movement.
        """
    )
    
    summary: str = Field(description="A concise technical summary.")
    trading_recommendation: str = Field(description="Actionable advice (e.g., 'Monitor spreads').")

    @field_validator('affected_assets', mode='before')
    @classmethod
    def parse_assets(cls, v):
        """
        Validator to ensure 'affected_assets' is always returned as a list,
        even if the LLM outputs a single string.
        """
        if isinstance(v, str):
            return [v]
        return v