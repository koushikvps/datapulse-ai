# agents/stock_agent.py
import yfinance as yf
import pandas as pd
from datetime import datetime

def get_stock_data(ticker: str) -> dict:
    """
    Fetches real-time stock data for a given ticker.
    Returns price, change, volume, and key stats.
    """
    print(f"\n📈 STOCK AGENT: Fetching data for {ticker}...")

    try:
        stock = yf.Ticker(ticker)
        info  = stock.info

        # Current price data
        current_price  = info.get("currentPrice") or info.get("regularMarketPrice", 0)
        previous_close = info.get("previousClose", 0)
        change         = current_price - previous_close
        change_pct     = (change / previous_close * 100) if previous_close else 0

        # Company info
        company_name = info.get("longName", ticker)
        sector       = info.get("sector", "Unknown")
        industry     = info.get("industry", "Unknown")
        market_cap   = info.get("marketCap", 0)
        volume       = info.get("volume", 0)

        # Key financial metrics
        pe_ratio     = info.get("trailingPE", None)
        week_52_high = info.get("fiftyTwoWeekHigh", 0)
        week_52_low  = info.get("fiftyTwoWeekLow", 0)
        analyst_target = info.get("targetMeanPrice", None)

        # Historical data for sparkline (last 30 days)
        hist = stock.history(period="1mo")
        price_history = hist["Close"].tolist() if not hist.empty else []

        result = {
            "ticker":          ticker.upper(),
            "company_name":    company_name,
            "sector":          sector,
            "industry":        industry,
            "current_price":   round(current_price, 2),
            "previous_close":  round(previous_close, 2),
            "change":          round(change, 2),
            "change_pct":      round(change_pct, 2),
            "volume":          volume,
            "market_cap":      market_cap,
            "pe_ratio":        round(pe_ratio, 2) if pe_ratio else None,
            "week_52_high":    round(week_52_high, 2),
            "week_52_low":     round(week_52_low, 2),
            "analyst_target":  round(analyst_target, 2) if analyst_target else None,
            "price_history":   [round(p, 2) for p in price_history],
            "last_updated":    datetime.now().strftime("%H:%M:%S"),
            "status":          "success"
        }

        print(f"✅ Stock data fetched: {company_name} @ ${current_price}")
        return result

    except Exception as e:
        print(f"❌ Stock agent error: {e}")
        return {
            "ticker":  ticker.upper(),
            "status":  "error",
            "error":   str(e)
        }

def format_market_cap(market_cap: int) -> str:
    """Format market cap to readable string."""
    if market_cap >= 1_000_000_000_000:
        return f"${market_cap/1_000_000_000_000:.1f}T"
    elif market_cap >= 1_000_000_000:
        return f"${market_cap/1_000_000_000:.1f}B"
    elif market_cap >= 1_000_000:
        return f"${market_cap/1_000_000:.1f}M"
    return f"${market_cap:,}"

# ── Test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    # Test with a few tickers
    for ticker in ["AAPL", "TSLA", "NVDA"]:
        data = get_stock_data(ticker)
        if data["status"] == "success":
            print(f"\n{'='*50}")
            print(f"Company:      {data['company_name']}")
            print(f"Price:        ${data['current_price']}")
            print(f"Change:       {data['change_pct']:+.2f}%")
            print(f"Market Cap:   {format_market_cap(data['market_cap'])}")
            print(f"52W Range:    ${data['week_52_low']} - ${data['week_52_high']}")
            print(f"P/E Ratio:    {data['pe_ratio']}")
            print(f"Price Hist:   {len(data['price_history'])} data points")

# ── ADD THIS to agents/stock_agent.py ─────────────────────

def get_crypto_data(symbol: str) -> dict:
    """
    Fetches real-time crypto data using yfinance.
    BTC → BTC-USD, ETH → ETH-USD etc.
    """
    print(f"\n🪙 CRYPTO AGENT: Fetching data for {symbol}...")

    try:
        # yfinance uses BTC-USD format for crypto
        ticker_symbol = f"{symbol.upper()}-USD"
        crypto = yf.Ticker(ticker_symbol)
        info   = crypto.info

        current_price  = info.get("regularMarketPrice") or info.get("currentPrice", 0)
        previous_close = info.get("regularMarketPreviousClose") or info.get("previousClose", 0)
        change         = current_price - previous_close
        change_pct     = (change / previous_close * 100) if previous_close else 0
        market_cap     = info.get("marketCap", 0)
        volume         = info.get("regularMarketVolume") or info.get("volume", 0)
        name           = info.get("name") or info.get("shortName") or symbol.upper()

        # Extra crypto-specific fields
        circulating_supply = info.get("circulatingSupply", None)
        total_supply       = info.get("totalSupply", None)
        week_52_high       = info.get("fiftyTwoWeekHigh", 0)
        week_52_low        = info.get("fiftyTwoWeekLow", 0)

        # Historical price (30 days)
        hist          = crypto.history(period="1mo")
        price_history = hist["Close"].tolist() if not hist.empty else []

        result = {
            "ticker":            symbol.upper(),
            "company_name":      name,
            "sector":            "Cryptocurrency",
            "industry":          "Digital Assets",
            "current_price":     round(current_price, 4),
            "previous_close":    round(previous_close, 4),
            "change":            round(change, 4),
            "change_pct":        round(change_pct, 2),
            "volume":            volume,
            "market_cap":        market_cap,
            "pe_ratio":          None,
            "week_52_high":      round(week_52_high, 4),
            "week_52_low":       round(week_52_low, 4),
            "analyst_target":    None,
            "circulating_supply": circulating_supply,
            "total_supply":      total_supply,
            "price_history":     [round(p, 4) for p in price_history],
            "last_updated":      datetime.now().strftime("%H:%M:%S"),
            "asset_type":        "crypto",
            "status":            "success"
        }

        print(f"✅ Crypto data fetched: {name} @ ${current_price:,.4f}")
        return result

    except Exception as e:
        print(f"❌ Crypto agent error: {e}")
        return {
            "ticker":  symbol.upper(),
            "status":  "error",
            "error":   str(e)
        }