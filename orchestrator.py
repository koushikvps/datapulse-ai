# orchestrator.py
import os
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from agents.stock_agent import get_stock_data
from agents.news_agent import get_news, get_overall_news_sentiment
from agents.sentiment_agent import get_social_sentiment
from agents.risk_agent import assess_risk
from agents.analyst_agent import generate_analysis
import yfinance as yf

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile"
)

# ══════════════════════════════════════════════════════════════
# STATE — flows through every node
# ══════════════════════════════════════════════════════════════
class PulseState(TypedDict):
    # Input
    query:          str       # raw user input e.g. "Tesla" or "TSLA"
    ticker:         str       # resolved ticker e.g. "TSLA"
    company_name:   str       # full name e.g. "Tesla Inc."

    # Agent outputs
    stock_data:     dict
    news_articles:  list
    news_sentiment: dict
    social_sentiment: dict
    risk:           dict
    analysis:       dict

    # Status tracking
    status:         str
    completed:      list
    error:          str


# ══════════════════════════════════════════════════════════════
# NODE 0 — Resolver
# Converts "Tesla" → ticker "TSLA" + company name
# ══════════════════════════════════════════════════════════════
def resolver_node(state: PulseState) -> PulseState:
    print(f"\n🔎 RESOLVER: Looking up '{state['query']}'...")

    query = state["query"].strip().upper()

    # Try direct ticker first
    try:
        test = yf.Ticker(query)
        info = test.info
        name = info.get("longName") or info.get("shortName", "")
        if name and len(name) > 2:
            print(f"✅ Resolved: {query} → {name}")
            return {
                **state,
                "ticker":       query,
                "company_name": name,
                "status":       f"Resolved {query}",
                "completed":    []
            }
    except:
        pass

    # Ask LLM to resolve company name → ticker
    prompt = f"""What is the NASDAQ or NYSE stock ticker symbol for "{state['query']}"?

Respond with ONLY the ticker symbol, nothing else.
Examples: AAPL, TSLA, NVDA, MSFT, GOOGL, AMZN"""

    try:
        response  = llm.invoke(prompt)
        ticker    = response.content.strip().upper().replace(".", "")

        stock     = yf.Ticker(ticker)
        info      = stock.info
        comp_name = info.get("longName") or info.get("shortName", ticker)

        print(f"✅ Resolved: '{state['query']}' → {ticker} ({comp_name})")
        return {
            **state,
            "ticker":       ticker,
            "company_name": comp_name,
            "status":       f"Resolved to {ticker}",
            "completed":    []
        }
    except Exception as e:
        print(f"❌ Could not resolve: {e}")
        return {
            **state,
            "ticker":       query,
            "company_name": query,
            "status":       "Resolution failed — using raw input",
            "completed":    [],
            "error":        str(e)
        }


# ══════════════════════════════════════════════════════════════
# NODE 1 — Stock Node
# ══════════════════════════════════════════════════════════════
def stock_node(state: PulseState) -> PulseState:
    data = get_stock_data(state["ticker"])
    return {
        **state,
        "stock_data": data,
        "completed":  state.get("completed", []) + ["stock"],
        "status":     "Stock data fetched"
    }


# ══════════════════════════════════════════════════════════════
# NODE 2 — News Node
# ══════════════════════════════════════════════════════════════
def news_node(state: PulseState) -> PulseState:
    articles  = get_news(state["company_name"], state["ticker"])
    sentiment = get_overall_news_sentiment(articles)
    return {
        **state,
        "news_articles":  articles,
        "news_sentiment": sentiment,
        "completed":      state.get("completed", []) + ["news"],
        "status":         "News fetched and scored"
    }


# ══════════════════════════════════════════════════════════════
# NODE 3 — Social Sentiment Node
# ══════════════════════════════════════════════════════════════
def sentiment_node(state: PulseState) -> PulseState:
    sentiment = get_social_sentiment(state["company_name"], state["ticker"])
    return {
        **state,
        "social_sentiment": sentiment,
        "completed":        state.get("completed", []) + ["sentiment"],
        "status":           "Social sentiment analyzed"
    }


# ══════════════════════════════════════════════════════════════
# NODE 4 — Risk Node
# ══════════════════════════════════════════════════════════════
def risk_node(state: PulseState) -> PulseState:
    risk = assess_risk(
        state["company_name"],
        state["ticker"],
        state.get("stock_data", {}),
        state.get("news_articles", []),
        state.get("social_sentiment", {})
    )
    return {
        **state,
        "risk":      risk,
        "completed": state.get("completed", []) + ["risk"],
        "status":    "Risk assessed"
    }


# ══════════════════════════════════════════════════════════════
# NODE 5 — Analyst Node
# ══════════════════════════════════════════════════════════════
def analyst_node(state: PulseState) -> PulseState:
    analysis = generate_analysis(
        state["company_name"],
        state["ticker"],
        state.get("stock_data", {}),
        state.get("news_articles", []),
        state.get("social_sentiment", {}),
        state.get("risk", {})
    )
    return {
        **state,
        "analysis":  analysis,
        "completed": state.get("completed", []) + ["analyst"],
        "status":    "Analysis complete"
    }


# ══════════════════════════════════════════════════════════════
# BUILD GRAPH
# ══════════════════════════════════════════════════════════════
def build_pipeline():
    graph = StateGraph(PulseState)

    # Add all nodes
    graph.add_node("resolver",  resolver_node)
    graph.add_node("stock",     stock_node)
    graph.add_node("news",      news_node)
    graph.add_node("sentiment", sentiment_node)
    graph.add_node("risk",      risk_node)
    graph.add_node("analyst",   analyst_node)

    # Wire them in sequence
    graph.set_entry_point("resolver")
    graph.add_edge("resolver",  "stock")
    graph.add_edge("stock",     "news")
    graph.add_edge("news",      "sentiment")
    graph.add_edge("sentiment", "risk")
    graph.add_edge("risk",      "analyst")
    graph.add_edge("analyst",   END)

    return graph.compile()


# ══════════════════════════════════════════════════════════════
# MAIN FUNCTION — call this from app.py
# ══════════════════════════════════════════════════════════════
def run_datapulse(query: str) -> PulseState:
    print("\n" + "="*60)
    print(f"🚀 DATAPULSE AI — Analyzing: {query}")
    print("="*60)

    pipeline = build_pipeline()

    initial_state = PulseState(
        query=           query,
        ticker=          "",
        company_name=    "",
        stock_data=      {},
        news_articles=   [],
        news_sentiment=  {},
        social_sentiment={},
        risk=            {},
        analysis=        {},
        status=          "Starting...",
        completed=       [],
        error=           ""
    )

    result = pipeline.invoke(initial_state)

    print("\n" + "="*60)
    print(f"✅ DATAPULSE COMPLETE!")
    print(f"   Company:        {result['company_name']}")
    print(f"   Ticker:         {result['ticker']}")
    print(f"   Price:          ${result['stock_data'].get('current_price', 'N/A')}")
    print(f"   Recommendation: {result['analysis'].get('rec_emoji','')} {result['analysis'].get('recommendation','')}")
    print(f"   Risk:           {result['risk'].get('overall_emoji','')} {result['risk'].get('overall_label','')}")
    print(f"   Completed:      {result['completed']}")
    print("="*60)

    return result


# ══════════════════════════════════════════════════════════════
# TEST
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    result = run_datapulse("Apple")
    print(f"\n🎯 FINAL VERDICT: {result['analysis'].get('verdict_headline', '')}")