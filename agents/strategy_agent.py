# agents/strategy_agent.py
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os
import json

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile"
)

# ── Risk Profile → Strategy Mapping ──────────────────────────
RISK_PROFILES = {
    "🔴 Aggressive": {
        "label":       "Aggressive",
        "color":       "#ff4560",
        "description": "High risk, high reward. You're comfortable with large swings and short-term losses for maximum upside.",
        "strategies":  ["Momentum / Trend Following", "Buy the Dip"],
        "assets":      ["TSLA", "NVDA", "BTC", "SOL", "DOGE"],
        "time_horizon":"1–6 months",
        "allocation":  "80–100% in high-volatility assets",
        "stop_loss":   "10–15% stop loss recommended",
    },
    "🟠 Moderate": {
        "label":       "Moderate",
        "color":       "#fbbf24",
        "description": "Balanced risk and reward. You want growth but can handle moderate volatility.",
        "strategies":  ["RSI Oversold/Overbought", "Moving Average Crossover"],
        "assets":      ["AAPL", "MSFT", "GOOGL", "ETH", "AMZN"],
        "time_horizon":"6–18 months",
        "allocation":  "50–70% growth assets, 30–50% stable",
        "stop_loss":   "7–10% stop loss recommended",
    },
    "🟡 Low Risk": {
        "label":       "Low Risk",
        "color":       "#38bdf8",
        "description": "Capital preservation first. Slow and steady growth with minimal drawdowns.",
        "strategies":  ["Value Investing", "Moving Average Crossover"],
        "assets":      ["MSFT", "AAPL", "JNJ", "BRK-B", "SPY"],
        "time_horizon":"1–3 years",
        "allocation":  "30–50% growth assets, 50–70% defensive",
        "stop_loss":   "5% stop loss recommended",
    },
    "🟢 No Risk": {
        "label":       "No Risk",
        "color":       "#00d084",
        "description": "Capital safety above all. Focus on stable, dividend-paying assets with very low volatility.",
        "strategies":  ["Value Investing"],
        "assets":      ["SPY", "QQQ", "VTI", "SCHD", "BND"],
        "time_horizon":"3–5+ years",
        "allocation":  "100% in index funds / blue-chip dividend stocks",
        "stop_loss":   "No stop loss — buy and hold",
    },
}


def suggest_strategies_by_risk(risk_profile: str, ticker: str, backtest_results: dict, conditions: dict, asset_type: str = "stock") -> dict:
    """
    AI suggests the best strategies for a given risk profile
    based on current market conditions and backtest data.
    """
    print(f"\n🧠 STRATEGY AGENT: Generating {risk_profile} suggestions for {ticker}...")

    profile = RISK_PROFILES.get(risk_profile, RISK_PROFILES["🟠 Moderate"])
    bt      = backtest_results
    cd      = conditions

    prompt = f"""You are a senior portfolio manager and quant analyst.

A client with a "{profile['label']}" risk profile wants to invest in {ticker} ({'Cryptocurrency' if asset_type == 'crypto' else 'Stock'}).

=== CLIENT RISK PROFILE ===
Risk Level:     {profile['label']}
Description:    {profile['description']}
Time Horizon:   {profile['time_horizon']}
Allocation:     {profile['allocation']}
Stop Loss:      {profile['stop_loss']}
Recommended Strategies: {', '.join(profile['strategies'])}

=== CURRENT MARKET CONDITIONS ===
RSI:            {cd.get('rsi', 'N/A')}
Signal:         {cd.get('signal', 'N/A')}
Reason:         {cd.get('reason', 'N/A')}
Momentum:       {cd.get('momentum', 'N/A')}%
SMA 200:        {cd.get('sma200', 'N/A')}

=== BACKTEST PERFORMANCE ===
Best Strategy Tested: {bt.get('strategy', 'N/A')}
Return:         {bt.get('total_return', 0):+.2f}%
Win Rate:       {bt.get('win_rate', 0)}%
Max Drawdown:   -{bt.get('max_drawdown', 0)}%
Outperformed Market: {'YES' if bt.get('outperformed') else 'NO'}

Based on this client's risk profile and current market conditions, write a personalized strategy recommendation.
Respond ONLY with this JSON (no markdown, no extra text):
{{
    "overall_fit": "GREAT FIT",
    "fit_emoji": "🟢",
    "fit_score": 8,
    "primary_strategy": "RSI Oversold/Overbought",
    "primary_reason": "2 sentences why this is the best strategy for this risk profile right now",
    "secondary_strategy": "Value Investing",
    "secondary_reason": "1 sentence why this is a good backup strategy",
    "entry_advice": "Specific advice on when/how to enter a position right now",
    "exit_advice": "Specific advice on when/how to exit or take profits",
    "position_size": "How much of portfolio to allocate e.g. 5-10% of portfolio",
    "key_warning": "The single most important risk warning for this profile on this asset",
    "personalized_tip": "One highly specific tip tailored to this risk profile and this exact asset"
}}

Rules:
- overall_fit: GREAT FIT / GOOD FIT / RISKY FIT / NOT RECOMMENDED
- fit_emoji: 🟢 Great, 🟡 Good, 🟠 Risky, 🔴 Not Recommended
- fit_score: 1-10
- Be specific to the ticker, not generic
- Match advice strictly to the risk profile"""

    try:
        response = llm.invoke(prompt)
        text = response.content.strip()
        if "```" in text:
            text = text.split("```")[1].replace("json", "").strip()
        result = json.loads(text)
        result["profile_data"] = profile
        print(f"✅ Risk Profile Suggestion: {result['fit_emoji']} {result['overall_fit']}")
        return result
    except Exception as e:
        print(f"❌ Strategy agent error: {e}")
        return {
            "overall_fit":        "ANALYSIS INCOMPLETE",
            "fit_emoji":          "🟡",
            "fit_score":          5,
            "primary_strategy":   profile["strategies"][0],
            "primary_reason":     "Based on your risk profile, this strategy aligns with your goals.",
            "secondary_strategy": profile["strategies"][-1],
            "secondary_reason":   "A conservative backup option.",
            "entry_advice":       "Wait for a confirmed signal before entering.",
            "exit_advice":        "Set a stop loss and take profits at your target.",
            "position_size":      "5-10% of portfolio",
            "key_warning":        "Always use risk management. Never invest more than you can afford to lose.",
            "personalized_tip":   "Paper trade first to validate the strategy.",
            "profile_data":       profile,
        }


def generate_strategy_verdict(ticker, strategy_name, backtest, conditions, asset_type="stock"):
    """AI verdict on a specific backtest result."""
    print(f"\n🧠 STRATEGY AGENT: Writing verdict for {strategy_name} on {ticker}...")
    bt = backtest
    cd = conditions

    prompt = f"""You are a quantitative analyst at a top hedge fund.

=== STRATEGY BACKTEST RESULTS ===
Asset:          {ticker} ({'Cryptocurrency' if asset_type == 'crypto' else 'Stock'})
Strategy:       {strategy_name}
Total Return:   {bt['total_return']:+.2f}%
Buy & Hold:     {bt['bh_return']:+.2f}%
Outperformed:   {'YES' if bt['outperformed'] else 'NO'}
Win Rate:       {bt['win_rate']}%
Total Trades:   {bt['total_trades']}
Max Drawdown:   -{bt['max_drawdown']}%
Best Trade:     +{bt['best_trade']}%
Worst Trade:    {bt['worst_trade']}%

=== CURRENT MARKET CONDITIONS ===
Signal Right Now: {cd['signal']}
Reason:           {cd['reason']}
RSI:              {cd.get('rsi', 'N/A')}
Momentum:         {cd.get('momentum', 'N/A')}%

Respond ONLY with this JSON:
{{
    "overall_verdict": "STRONG STRATEGY",
    "verdict_emoji": "🟢",
    "confidence": "High",
    "action_now": "EXECUTE",
    "action_emoji": "🟢",
    "strategy_score": 8,
    "summary": "2-3 sentence assessment of how well this strategy works for this asset",
    "current_opportunity": "1-2 sentences about whether NOW is a good time to use it",
    "risk_warning": "1 sentence about the main risk of this strategy on this asset",
    "pro_tip": "1 sentence pro tip for using this strategy better"
}}

Rules:
- overall_verdict: STRONG STRATEGY / DECENT STRATEGY / WEAK STRATEGY / AVOID
- verdict_emoji: 🟢 Strong, 🟡 Decent, 🔴 Weak/Avoid
- action_now: EXECUTE / WAIT / AVOID
- action_emoji: 🟢 Execute, 🟡 Wait, 🔴 Avoid
- strategy_score: 1-10"""

    try:
        response = llm.invoke(prompt)
        text = response.content.strip()
        if "```" in text:
            text = text.split("```")[1].replace("json", "").strip()
        result = json.loads(text)
        print(f"✅ Verdict: {result['verdict_emoji']} {result['overall_verdict']}")
        return result
    except Exception as e:
        print(f"❌ Strategy agent error: {e}")
        return {
            "overall_verdict": "ANALYSIS INCOMPLETE",
            "verdict_emoji":   "🟡",
            "confidence":      "Low",
            "action_now":      "WAIT",
            "action_emoji":    "🟡",
            "strategy_score":  5,
            "summary":         "Could not complete strategy analysis.",
            "current_opportunity": "Insufficient data for current assessment.",
            "risk_warning":    "Always use stop losses.",
            "pro_tip":         "Test strategies on paper before live trading."
        }