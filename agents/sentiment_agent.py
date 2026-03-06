# agents/sentiment_agent.py
from duckduckgo_search import DDGS
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import json

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile"
)

def get_social_sentiment(company_name: str, ticker: str) -> dict:
    """
    Scrapes social discussions about a company
    and returns a sentiment analysis.
    """
    print(f"\n💬 SENTIMENT AGENT: Analyzing social buzz for {company_name}...")

    # Search for social discussions
    discussions = []
    queries = [
        f"{ticker} stock Reddit discussion 2025",
        f"{company_name} investor opinion forecast",
        f"{ticker} stock analysis community"
    ]

    try:
        with DDGS() as ddgs:
            for query in queries:
                for r in ddgs.text(query, max_results=3):
                    discussions.append(r.get("body", ""))

        # Combine all text
        combined = " ".join(discussions[:6])[:4000]

        # Analyze with LLM
        result = analyze_social_text(combined, company_name, ticker)
        print(f"✅ Social sentiment: {result['verdict']} ({result['buzz_score']}/10)")
        return result

    except Exception as e:
        print(f"❌ Sentiment agent error: {e}")
        return {
            "verdict":    "Neutral",
            "buzz_score": 5,
            "bull_pct":   50,
            "bear_pct":   50,
            "summary":    "Could not analyze social sentiment",
            "key_themes": [],
            "emoji":      "🟡"
        }


def analyze_social_text(text: str, company_name: str, ticker: str) -> dict:
    """Use LLM to analyze social sentiment from raw text."""
    prompt = f"""You are a financial sentiment analyst.

Analyze the following social media and forum discussions about {company_name} ({ticker}).

Text:
{text}

Respond with ONLY a JSON object in this exact format:
{{
    "verdict": "Bullish",
    "buzz_score": 7,
    "bull_pct": 65,
    "bear_pct": 35,
    "emoji": "🟢",
    "summary": "2-3 sentence summary of what people are saying",
    "key_themes": ["theme 1", "theme 2", "theme 3"],
    "notable_quote": "A representative quote or paraphrase from discussions"
}}

Rules:
- verdict: Bullish, Bearish, or Neutral
- buzz_score: 1-10 overall excitement level
- bull_pct + bear_pct = 100
- emoji: 🟢 Bullish, 🔴 Bearish, 🟡 Neutral
- key_themes: exactly 3 themes
- notable_quote: best representative statement"""

    try:
        response = llm.invoke(prompt)
        text_resp = response.content.strip()
        if "```" in text_resp:
            text_resp = text_resp.split("```")[1].replace("json","").strip()
        return json.loads(text_resp)
    except:
        return {
            "verdict":      "Neutral",
            "buzz_score":   5,
            "bull_pct":     50,
            "bear_pct":     50,
            "emoji":        "🟡",
            "summary":      "Sentiment analysis inconclusive",
            "key_themes":   ["Mixed signals", "Uncertain outlook", "Wait and see"],
            "notable_quote": "Community divided on outlook"
        }


# ── Test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    result = get_social_sentiment("NVIDIA", "NVDA")

    print(f"\n{'='*55}")
    print(f"💬 SOCIAL SENTIMENT: NVIDIA")
    print(f"{'='*55}")
    print(f"Verdict:       {result['emoji']} {result['verdict']}")
    print(f"Buzz Score:    {result['buzz_score']}/10")
    print(f"Bulls:         {result['bull_pct']}%")
    print(f"Bears:         {result['bear_pct']}%")
    print(f"\nSummary: {result['summary']}")
    print(f"\nKey Themes:")
    for t in result['key_themes']:
        print(f"  → {t}")
    print(f"\nNotable: \"{result['notable_quote']}\"")