# agents/news_agent.py
from duckduckgo_search import DDGS
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile"
)

def get_news(company_name: str, ticker: str, max_results: int = 8) -> list[dict]:
    """
    Fetches latest news for a company and scores
    each headline as positive, negative or neutral.
    """
    print(f"\n📰 NEWS AGENT: Fetching news for {company_name}...")

    try:
        query = f"{company_name} {ticker} stock news 2025"
        articles = []

        with DDGS() as ddgs:
            for r in ddgs.news(query, max_results=max_results):
                articles.append({
                    "title":  r.get("title", ""),
                    "url":    r.get("url", ""),
                    "source": r.get("source", ""),
                    "date":   r.get("date", ""),
                    "body":   r.get("body", "")
                })

        print(f"✅ Found {len(articles)} articles")

        # Score each headline with LLM
        scored = []
        for article in articles[:6]:
            score = score_headline(article["title"])
            scored.append({**article, **score})

        return scored

    except Exception as e:
        print(f"❌ News agent error: {e}")
        return []


def score_headline(headline: str) -> dict:
    """Score a headline as positive/negative/neutral with reasoning."""
    prompt = f"""Analyze this financial news headline and respond with ONLY a JSON object.

Headline: "{headline}"

Respond with exactly this format, no other text:
{{"sentiment": "positive", "score": 8, "emoji": "🟢", "reason": "one sentence reason"}}

Rules:
- sentiment must be: positive, negative, or neutral
- score: 1-10 (10 = very positive, 1 = very negative, 5 = neutral)
- emoji: 🟢 for positive, 🔴 for negative, 🟡 for neutral
- reason: one short sentence"""

    try:
        response = llm.invoke(prompt)
        import json
        text = response.content.strip()
        # Clean up response
        if "```" in text:
            text = text.split("```")[1].replace("json", "").strip()
        return json.loads(text)
    except:
        return {"sentiment": "neutral", "score": 5, "emoji": "🟡", "reason": "Unable to analyze"}


def get_overall_news_sentiment(articles: list[dict]) -> dict:
    """Calculate overall sentiment from all articles."""
    if not articles:
        return {"overall": "neutral", "score": 5, "summary": "No news found"}

    scores = [a.get("score", 5) for a in articles]
    avg    = sum(scores) / len(scores)

    if avg >= 7:
        overall = "Bullish"
        emoji   = "🟢"
    elif avg <= 4:
        overall = "Bearish"
        emoji   = "🔴"
    else:
        overall = "Neutral"
        emoji   = "🟡"

    positive = sum(1 for a in articles if a.get("sentiment") == "positive")
    negative = sum(1 for a in articles if a.get("sentiment") == "negative")
    neutral  = sum(1 for a in articles if a.get("sentiment") == "neutral")

    return {
        "overall":   overall,
        "emoji":     emoji,
        "score":     round(avg, 1),
        "positive":  positive,
        "negative":  negative,
        "neutral":   neutral,
        "total":     len(articles)
    }


# ── Test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    articles = get_news("Apple", "AAPL")
    sentiment = get_overall_news_sentiment(articles)

    print(f"\n{'='*55}")
    print(f"📰 NEWS RESULTS FOR APPLE")
    print(f"{'='*55}")
    for a in articles[:5]:
        print(f"\n{a.get('emoji','🟡')} [{a.get('sentiment','?').upper()}] Score: {a.get('score',5)}/10")
        print(f"   {a['title'][:70]}")
        print(f"   Reason: {a.get('reason','')}")

    print(f"\n{'='*55}")
    print(f"OVERALL SENTIMENT: {sentiment['emoji']} {sentiment['overall']}")
    print(f"Average Score:     {sentiment['score']}/10")
    print(f"Positive: {sentiment['positive']} | Negative: {sentiment['negative']} | Neutral: {sentiment['neutral']}")