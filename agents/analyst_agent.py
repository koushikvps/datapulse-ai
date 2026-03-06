# agents/analyst_agent.py
from langchain_groq import ChatGroq
from dotenv import load_dotenv

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.stock_agent import format_market_cap

import os
import json

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile"
)

def generate_analysis(
    company_name: str,
    ticker: str,
    stock_data: dict,
    news_articles: list,
    sentiment: dict,
    risk: dict
) -> dict:
    """
    Generates a professional analyst report with
    Buy / Hold / Sell recommendation and price target.
    """
    print(f"\n🧠 ANALYST AGENT: Writing analysis for {company_name}...")

    # Build rich context
    price          = stock_data.get("current_price", 0)
    change_pct     = stock_data.get("change_pct", 0)
    market_cap     = format_market_cap(stock_data.get("market_cap", 0))
    pe             = stock_data.get("pe_ratio", "N/A")
    analyst_target = stock_data.get("analyst_target")
    sector         = stock_data.get("sector", "Unknown")
    news_sentiment = sentiment.get("verdict", "Neutral")
    social_bulls   = sentiment.get("bull_pct", 50)
    risk_score     = risk.get("overall_score", 5)
    risk_label     = risk.get("overall_label", "Medium Risk")
    key_risks      = risk.get("key_risks", [])
    news_summary   = "\n".join([
        f"- {a.get('emoji','🟡')} {a['title'][:80]}"
        for a in news_articles[:5]
    ])

    prompt = f"""You are a senior equity analyst at Goldman Sachs writing a professional research note.

=== COMPANY DATA ===
Company: {company_name} ({ticker})
Sector: {sector}
Current Price: ${price}
Today's Change: {change_pct:+.2f}%
Market Cap: {market_cap}
P/E Ratio: {pe}
Analyst Consensus Target: ${analyst_target if analyst_target else 'N/A'}

=== MARKET SIGNALS ===
News Sentiment: {news_sentiment}
Social Sentiment: {social_bulls}% bullish
Risk Level: {risk_label} ({risk_score}/10)
Key Risks: {', '.join(key_risks)}

=== RECENT NEWS ===
{news_summary}

Write a professional analyst report. Respond with ONLY this JSON:
{{
    "recommendation": "BUY",
    "conviction": "High",
    "rec_emoji": "🟢",
    "price_target": 220.00,
    "upside_pct": 11.2,
    "time_horizon": "12 months",
    "thesis": "2-3 sentence investment thesis — the main reason for the call",
    "bull_case": "What happens if everything goes right (2 sentences)",
    "bear_case": "What happens if things go wrong (2 sentences)",
    "catalysts": ["catalyst 1", "catalyst 2", "catalyst 3"],
    "verdict_headline": "One punchy headline summarizing the call",
    "detailed_analysis": "4-5 sentence professional analysis covering business fundamentals, competitive position, and outlook"
}}

Rules:
- recommendation: BUY, HOLD, or SELL
- conviction: High, Medium, or Low
- rec_emoji: 🟢 BUY, 🟡 HOLD, 🔴 SELL
- price_target: realistic number based on current price and analyst target
- upside_pct: % upside from current price to target
- catalysts: exactly 3 specific upcoming catalysts
- Be direct, professional, and specific — like a real Goldman Sachs note"""

    try:
        response = llm.invoke(prompt)
        text = response.content.strip()
        if "```" in text:
            text = text.split("```")[1].replace("json","").strip()
        result = json.loads(text)
        print(f"✅ Analysis complete: {result['rec_emoji']} {result['recommendation']} | Target: ${result['price_target']}")
        return result
    except Exception as e:
        print(f"❌ Analyst agent error: {e}")
        return {
            "recommendation":   "HOLD",
            "conviction":       "Low",
            "rec_emoji":        "🟡",
            "price_target":     stock_data.get("current_price", 0),
            "upside_pct":       0,
            "time_horizon":     "12 months",
            "thesis":           "Insufficient data for strong recommendation.",
            "bull_case":        "Company could outperform if conditions improve.",
            "bear_case":        "Downside risk remains if headwinds persist.",
            "catalysts":        ["Earnings report", "Product launch", "Market conditions"],
            "verdict_headline": f"{company_name}: Wait for Better Entry Point",
            "detailed_analysis": "Analysis could not be completed with available data."
        }


# ── Test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    mock_stock = {
        "current_price":  198.45,
        "change_pct":     -1.2,
        "market_cap":     3_100_000_000_000,
        "pe_ratio":       32.4,
        "analyst_target": 225.0,
        "sector":         "Technology"
    }
    mock_news = [
        {"emoji": "🟢", "title": "Apple beats Q2 earnings estimates"},
        {"emoji": "🔴", "title": "Apple faces EU antitrust fine"},
        {"emoji": "🟢", "title": "iPhone 17 pre-orders break records"},
    ]
    mock_sentiment = {"verdict": "Bullish", "bull_pct": 68, "bear_pct": 32}
    mock_risk = {
        "overall_score": 4,
        "overall_label": "Low-Medium Risk",
        "key_risks": ["Valuation premium", "China exposure", "Regulatory pressure"]
    }

    result = generate_analysis(
        "Apple", "AAPL",
        mock_stock, mock_news,
        mock_sentiment, mock_risk
    )

    print(f"\n{'='*55}")
    print(f"🧠 ANALYST REPORT: APPLE")
    print(f"{'='*55}")
    print(f"\n{result['rec_emoji']} RECOMMENDATION: {result['recommendation']} ({result['conviction']} Conviction)")
    print(f"Price Target:  ${result['price_target']} ({result['upside_pct']:+.1f}%)")
    print(f"Time Horizon:  {result['time_horizon']}")
    print(f"\n📌 HEADLINE: {result['verdict_headline']}")
    print(f"\n💡 THESIS:\n{result['thesis']}")
    print(f"\n📈 BULL CASE:\n{result['bull_case']}")
    print(f"\n📉 BEAR CASE:\n{result['bear_case']}")
    print(f"\n⚡ CATALYSTS:")
    for c in result['catalysts']:
        print(f"  → {c}")
    print(f"\n📊 ANALYSIS:\n{result['detailed_analysis']}")