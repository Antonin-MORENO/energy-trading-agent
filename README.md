# ⚡ Energy Trading AI Desk

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/AI-Llama3_via_Groq-f55036)
![Finance](https://img.shields.io/badge/Domain-Energy_Markets-green)

> **Une exploration de l'IA appliquée à la finance : Comment transformer un LLM généraliste en un analyste de marché spécialisé ?**

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](TON_LIEN_STREAMLIT_ICI)

![Dashboard Preview](demo_screenshot.png)
*(Ajoute une capture d'écran de ton dashboard ici)*

---

## 🎯 L'Objectif de l'Exploration

Ce projet est né d'une question simple : **Est-il possible d'utiliser un LLM "généraliste" (comme Llama 3) pour interpréter fiablements des signaux de marché complexes ?**

Les traders en énergie doivent corréler deux mondes :
1.  **Le monde Quantitatif :** Des séries temporelles précises (Prix, Volatilité).
2.  **Le monde Qualitatif :** Un flux chaotique d'informations (Géopolitique, Météo, Stocks).

J'ai construit ce système pour **orchestrer** ces deux mondes. L'objectif n'était pas seulement d'afficher des courbes, mais de créer un **Agent Autonome** capable de "lire" les news et de rejeter le bruit médiatique pour ne garder que les signaux de trading valides.

## 🏗️ Architecture du Système

Le système repose sur une architecture modulaire séparant strictement l'ingestion de données, l'analyse mathématique et le raisonnement cognitif (IA).

```mermaid
graph TD
    subgraph "Data Layer"
        A[Yahoo Finance API] -->|Prix OHLC| B(Data Loader)
        C[NewsAPI] -->|Articles Bruts| B
    end

    subgraph "Intelligence Layer"
        B -->|Séries Temporelles| D{Analytics Engine}
        D -->|Calcul Volatilité| E[Régimes de Marché]
        
        B -->|Texte Non structuré| F{AI Agent}
        F -->|Prompt Engineering| G[Llama 3 via Groq]
        G -->|Extraction Structurée| H[Signal Trading]
    end

    subgraph "Presentation Layer"
        E --> I[Streamlit Dashboard]
        H --> I
        I -->|Interface Trader| J(Utilisateur)
    end
