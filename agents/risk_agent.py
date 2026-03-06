# agents/risk_agent.py
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import json

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile"
)

def assess_risk(
    company_name: str,
    ticker: str,
    stock_data: dict,
    news_articles: list,
    sentiment: dict
) -> dict:
    """
    Assesses risk across 5 dimensions:
    1. Valuation Risk
    2. Market Risk
    3. News/Event Risk
    4. Sentiment Risk
    5. Technical Risk
    """
    print(f"\n⚠️ RISK AGENT: Assessing risk for {company_name}...")

    # Build context for LLM
    pe      = stock_data.get("pe_ratio", "N/A")
    chg_pct = stock_data.get("change_pct", 0)
    hi_52   = stock_data.get("week_52_high", 0)
    lo_52   = stock_data.get("week_52_low", 0)
    price   = stock_data.get("current_price", 0)
    neg_news = sum(1 for a in news_articles if a.get("sentiment") == "negative")
    bull_pct = sentiment.get("bull_pct", 50)

    # 52-week position (0% = at low, 100% = at high)
    if hi_52 and lo_52 and hi_52 != lo_52:
        position_52w = round((price - lo_52) / (hi_52 - lo_52) * 100, 1)
    else:
        position_52w = 50

    prompt = f"""You are a professional risk analyst at a top investment bank.

Company: {company_name} ({ticker})
Current Price: ${price}
P/E Ratio: {pe}
Today's Change: {chg_pct:+.2f}%
52-Week Range: ${lo_52} - ${hi_52}
Position in 52W Range: {position_52w}%
Negative News Count: {neg_news} out of {len(news_articles)} articles
Social Bull %: {bull_pct}%

Assess risk across exactly 5 dimensions. Respond with ONLY this JSON:
{{
    "overall_score": 6,
    "overall_label": "Medium Risk",
    "overall_emoji": "🟡",
    "dimensions": [
        {{
            "name": "Valuation Risk",
            "score": 7,
            "label": "High",
            "emoji": "🔴",
            "reason": "one sentence"
        }},
        {{
            "name": "Market Risk",
            "score": 5,
            "label": "Medium",
            "emoji": "🟡",
            "reason": "one sentence"
        }},
        {{
            "name": "News Risk",
            "score": 4,
            "label": "Low-Medium",
            "emoji": "🟡",
            "reason": "one sentence"
        }},
        {{
            "name": "Sentiment Risk",
            "score": 3,
            "label": "Low",
            "emoji": "🟢",
            "reason": "one sentence"
        }},
        {{
            "name": "Technical Risk",
            "score": 6,
            "label": "Medium",
            "emoji": "🟡",
            "reason": "one sentence"
        }}
    ],
    "key_risks": ["risk 1", "risk 2", "risk 3"],
    "risk_summary": "2-3 sentence overall risk assessment"
}}

Rules:
- overall_score: 1-10 (10 = extremely risky)
- overall_label: Low Risk / Medium Risk / High Risk / Very High Risk
- overall_emoji: 🟢 Low, 🟡 Medium, 🔴 High
- dimension scores: 1-10
- key_risks: exactly 3 specific risks"""

    try:
        response = llm.invoke(prompt)
        text = response.content.strip()
        if "```" in text:
            text = text.split("```")[1].replace("json","").strip()
        result = json.loads(text)
        print(f"✅ Risk assessed: {result['overall_emoji']} {result['overall_label']} ({result['overall_score']}/10)")
        return result
    except Exception as e:
        print(f"❌ Risk agent error: {e}")
        return {
            "overall_score": 5,
            "overall_label": "Medium Risk",
            "overall_emoji": "🟡",
            "dimensions": [],
            "key_risks": ["Data unavailable", "Analysis incomplete", "Manual review needed"],
            "risk_summary": "Risk assessment could not be completed automatically."
        }


# ── Test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    # Mock data for testing
    mock_stock = {
        "current_price": 198.45,
        "pe_ratio": 32.4,
        "change_pct": -1.2,
        "week_52_high": 237.23,
        "week_52_low": 164.08
    }
    mock_news = [
        {"sentiment": "positive"}, {"sentiment": "positive"},
        {"sentiment": "negative"}, {"sentiment": "neutral"}
    ]
    mock_sentiment = {"bull_pct": 62, "bear_pct": 38}

    result = assess_risk("Apple", "AAPL", mock_stock, mock_news, mock_sentiment)

    print(f"\n{'='*55}")
    print(f"⚠️  RISK ASSESSMENT: APPLE")
    print(f"{'='*55}")
    print(f"Overall: {result['overall_emoji']} {result['overall_label']} ({result['overall_score']}/10)")
    print(f"\nDimensions:")
    for d in result.get("dimensions", []):
        bar = "█" * d['score'] + "░" * (10 - d['score'])
        print(f"  {d['emoji']} {d['name']:<20} [{bar}] {d['score']}/10")
        print(f"     → {d['reason']}")
    print(f"\nKey Risks:")
    for r in result.get("key_risks", []):
        print(f"  ⚡ {r}")
    print(f"\nSummary: {result['risk_summary']}")