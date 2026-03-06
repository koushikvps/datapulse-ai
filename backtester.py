# backtester.py
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_historical_data(ticker: str, period: str = "1y", asset_type: str = "stock") -> pd.DataFrame:
    """Fetch OHLCV historical data."""
    print(f"\n📊 BACKTESTER: Fetching {period} history for {ticker}...")
    try:
        symbol = f"{ticker}-USD" if asset_type == "crypto" else ticker
        df = yf.Ticker(symbol).history(period=period)
        if df.empty:
            raise ValueError(f"No data for {ticker}")
        df = df[["Open","High","Low","Close","Volume"]].copy()
        df.dropna(inplace=True)
        print(f"✅ Got {len(df)} candles")
        return df
    except Exception as e:
        print(f"❌ Data fetch error: {e}")
        return pd.DataFrame()


# ── INDICATORS ────────────────────────────────────────────────

def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    delta = df["Close"].diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss.replace(0, np.nan)
    df["RSI"] = 100 - (100 / (1 + rs))
    return df

def add_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
    df["SMA20"]  = df["Close"].rolling(20).mean()
    df["SMA50"]  = df["Close"].rolling(50).mean()
    df["SMA200"] = df["Close"].rolling(200).mean()
    df["EMA12"]  = df["Close"].ewm(span=12).mean()
    df["EMA26"]  = df["Close"].ewm(span=26).mean()
    return df

def add_momentum(df: pd.DataFrame, period: int = 10) -> pd.DataFrame:
    df["Momentum"] = df["Close"].pct_change(period) * 100
    return df

def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = add_rsi(df)
    df = add_moving_averages(df)
    df = add_momentum(df)
    return df


# ── STRATEGY SIGNAL GENERATORS ────────────────────────────────

def strategy_rsi(df: pd.DataFrame) -> pd.Series:
    """
    RSI Oversold/Overbought
    BUY  when RSI < 30 (oversold)
    SELL when RSI > 70 (overbought)
    """
    signals = pd.Series(0, index=df.index)
    signals[df["RSI"] < 30] = 1   # BUY
    signals[df["RSI"] > 70] = -1  # SELL
    return signals

def strategy_moving_average(df: pd.DataFrame) -> pd.Series:
    """
    Moving Average Crossover
    BUY  when SMA20 crosses above SMA50
    SELL when SMA20 crosses below SMA50
    """
    signals = pd.Series(0, index=df.index)
    for i in range(1, len(df)):
        prev_diff = df["SMA20"].iloc[i-1] - df["SMA50"].iloc[i-1]
        curr_diff = df["SMA20"].iloc[i]   - df["SMA50"].iloc[i]
        if prev_diff < 0 and curr_diff >= 0:
            signals.iloc[i] = 1   # Golden cross → BUY
        elif prev_diff > 0 and curr_diff <= 0:
            signals.iloc[i] = -1  # Death cross  → SELL
    return signals

def strategy_momentum(df: pd.DataFrame) -> pd.Series:
    """
    Momentum / Trend Following
    BUY  when 10-day momentum > +5%
    SELL when 10-day momentum < -5%
    """
    signals = pd.Series(0, index=df.index)
    signals[df["Momentum"] > 5]  = 1
    signals[df["Momentum"] < -5] = -1
    return signals

def strategy_value(df: pd.DataFrame) -> pd.Series:
    """
    Value Investing
    BUY  when price is > 20% below SMA200 (undervalued)
    SELL when price is > 20% above SMA200 (overvalued)
    """
    signals = pd.Series(0, index=df.index)
    ratio = (df["Close"] - df["SMA200"]) / df["SMA200"] * 100
    signals[ratio < -20] = 1
    signals[ratio >  20] = -1
    return signals

def strategy_buy_the_dip(df: pd.DataFrame) -> pd.Series:
    """
    Buy the Dip
    BUY  when price drops > 5% in 3 days AND RSI < 40
    SELL when price recovers > 5% from entry
    """
    signals  = pd.Series(0, index=df.index)
    ret_3day = df["Close"].pct_change(3) * 100
    signals[(ret_3day < -5) & (df["RSI"] < 40)] = 1
    signals[ret_3day > 5] = -1
    return signals


# ── BACKTESTER ENGINE ─────────────────────────────────────────

def run_backtest(
    df: pd.DataFrame,
    signals: pd.Series,
    initial_capital: float = 10000.0
) -> dict:
    """
    Simulates trading based on signals.
    Returns full performance metrics.
    """
    capital   = initial_capital
    position  = 0.0       # shares held
    entry_price = 0.0
    trades    = []
    equity    = []
    wins      = 0
    losses    = 0

    for i in range(len(df)):
        price  = df["Close"].iloc[i]
        signal = signals.iloc[i]
        date   = df.index[i]

        # BUY signal — go all in
        if signal == 1 and position == 0 and capital > 0:
            position    = capital / price
            entry_price = price
            capital     = 0

        # SELL signal — close position
        elif signal == -1 and position > 0:
            capital  = position * price
            pnl      = (price - entry_price) / entry_price * 100
            trades.append({
                "date":       str(date.date()),
                "entry":      round(entry_price, 4),
                "exit":       round(price, 4),
                "pnl_pct":    round(pnl, 2),
                "result":     "WIN" if pnl > 0 else "LOSS"
            })
            if pnl > 0:
                wins += 1
            else:
                losses += 1
            position    = 0
            entry_price = 0

        # Track equity curve
        total_value = capital + (position * price)
        equity.append({"date": str(date.date()), "value": round(total_value, 2)})

    # Close any open position at last price
    if position > 0:
        final_price = df["Close"].iloc[-1]
        capital = position * final_price

    # ── Performance Metrics ──
    final_value    = capital
    total_return   = (final_value - initial_capital) / initial_capital * 100
    total_trades   = wins + losses
    win_rate       = (wins / total_trades * 100) if total_trades > 0 else 0

    # Buy & Hold benchmark
    bh_return = (df["Close"].iloc[-1] - df["Close"].iloc[0]) / df["Close"].iloc[0] * 100

    # Max Drawdown
    equity_vals = [e["value"] for e in equity]
    peak        = initial_capital
    max_dd      = 0
    for val in equity_vals:
        if val > peak:
            peak = val
        dd = (peak - val) / peak * 100
        if dd > max_dd:
            max_dd = dd

    # Best and worst trade
    best_trade  = max((t["pnl_pct"] for t in trades), default=0)
    worst_trade = min((t["pnl_pct"] for t in trades), default=0)

    return {
        "initial_capital":  initial_capital,
        "final_value":      round(final_value, 2),
        "total_return":     round(total_return, 2),
        "bh_return":        round(bh_return, 2),
        "outperformed":     total_return > bh_return,
        "total_trades":     total_trades,
        "wins":             wins,
        "losses":           losses,
        "win_rate":         round(win_rate, 1),
        "max_drawdown":     round(max_dd, 2),
        "best_trade":       round(best_trade, 2),
        "worst_trade":      round(worst_trade, 2),
        "equity_curve":     equity[-100:],   # last 100 points for chart
        "recent_trades":    trades[-10:],    # last 10 trades
        "price_history":    [round(p, 4) for p in df["Close"].tolist()],
        "dates":            [str(d.date()) for d in df.index],
    }


# ── CURRENT CONDITIONS SCORER ─────────────────────────────────

def score_current_conditions(df: pd.DataFrame, strategy_name: str) -> dict:
    """
    Scores whether RIGHT NOW is a good time
    to use this strategy on this asset.
    """
    latest = df.iloc[-1]
    rsi    = latest.get("RSI", 50)
    sma20  = latest.get("SMA20", 0)
    sma50  = latest.get("SMA50", 0)
    sma200 = latest.get("SMA200", 0)
    price  = latest["Close"]
    mom    = latest.get("Momentum", 0)

    score  = 5   # neutral start
    signal = "NEUTRAL"
    reason = ""

    if strategy_name == "RSI Oversold/Overbought":
        if rsi < 30:
            score = 9; signal = "STRONG BUY"
            reason = f"RSI at {rsi:.1f} — deeply oversold, strong buy signal"
        elif rsi < 40:
            score = 7; signal = "BUY"
            reason = f"RSI at {rsi:.1f} — approaching oversold territory"
        elif rsi > 70:
            score = 2; signal = "SELL"
            reason = f"RSI at {rsi:.1f} — overbought, consider taking profits"
        elif rsi > 60:
            score = 3; signal = "CAUTION"
            reason = f"RSI at {rsi:.1f} — elevated, watch for reversal"
        else:
            score = 5; signal = "NEUTRAL"
            reason = f"RSI at {rsi:.1f} — neutral zone, no clear signal"

    elif strategy_name == "Moving Average Crossover":
        if sma20 > sma50 and price > sma200:
            score = 8; signal = "BUY"
            reason = "Golden cross active — SMA20 above SMA50, price above SMA200"
        elif sma20 < sma50 and price < sma200:
            score = 2; signal = "SELL"
            reason = "Death cross active — SMA20 below SMA50, bearish trend"
        else:
            score = 5; signal = "NEUTRAL"
            reason = "Moving averages mixed — wait for clearer crossover"

    elif strategy_name == "Momentum / Trend Following":
        if mom > 10:
            score = 9; signal = "STRONG BUY"
            reason = f"Strong momentum +{mom:.1f}% — trend is your friend"
        elif mom > 5:
            score = 7; signal = "BUY"
            reason = f"Positive momentum +{mom:.1f}% — uptrend in place"
        elif mom < -10:
            score = 1; signal = "STRONG SELL"
            reason = f"Negative momentum {mom:.1f}% — strong downtrend"
        elif mom < -5:
            score = 3; signal = "SELL"
            reason = f"Declining momentum {mom:.1f}% — caution advised"
        else:
            score = 5; signal = "NEUTRAL"
            reason = f"Momentum at {mom:.1f}% — no strong directional bias"

    elif strategy_name == "Value Investing":
        if sma200 > 0:
            dev = (price - sma200) / sma200 * 100
            if dev < -20:
                score = 9; signal = "STRONG BUY"
                reason = f"Trading {abs(dev):.1f}% below 200-day MA — significant undervaluation"
            elif dev < -10:
                score = 7; signal = "BUY"
                reason = f"Trading {abs(dev):.1f}% below 200-day MA — potential value opportunity"
            elif dev > 20:
                score = 2; signal = "OVERVALUED"
                reason = f"Trading {dev:.1f}% above 200-day MA — stretched valuation"
            else:
                score = 5; signal = "FAIR VALUE"
                reason = f"Trading near 200-day MA — fairly valued at current levels"

    elif strategy_name == "Buy the Dip":
        ret_3 = df["Close"].pct_change(3).iloc[-1] * 100
        if ret_3 < -5 and rsi < 40:
            score = 9; signal = "DIP CONFIRMED"
            reason = f"Price down {abs(ret_3):.1f}% in 3 days with RSI {rsi:.1f} — classic dip setup"
        elif ret_3 < -3:
            score = 6; signal = "POSSIBLE DIP"
            reason = f"Price down {abs(ret_3):.1f}% — watch for further confirmation"
        else:
            score = 4; signal = "NO DIP YET"
            reason = f"No significant dip detected — wait for better entry"

    return {
        "score":  score,
        "signal": signal,
        "reason": reason,
        "rsi":    round(rsi, 1) if rsi else None,
        "sma20":  round(sma20, 2) if sma20 else None,
        "sma50":  round(sma50, 2) if sma50 else None,
        "sma200": round(sma200, 2) if sma200 else None,
        "momentum": round(mom, 2) if mom else None,
    }


# ── MAIN ENTRY POINT ──────────────────────────────────────────

STRATEGIES = {
    "RSI Oversold/Overbought":    strategy_rsi,
    "Moving Average Crossover":   strategy_moving_average,
    "Momentum / Trend Following": strategy_momentum,
    "Value Investing":            strategy_value,
    "Buy the Dip":                strategy_buy_the_dip,
}

def run_strategy_analysis(
    ticker:        str,
    strategy_name: str,
    period:        str = "1y",
    asset_type:    str = "stock",
    initial_capital: float = 10000.0
) -> dict:
    """
    Full strategy analysis:
    1. Fetch historical data
    2. Add indicators
    3. Generate signals
    4. Backtest
    5. Score current conditions
    """
    print(f"\n🎯 STRATEGY ENGINE: {strategy_name} on {ticker} ({period})")

    df = get_historical_data(ticker, period, asset_type)
    if df.empty:
        return {"error": "Could not fetch data"}

    df = add_all_indicators(df)
    df.dropna(inplace=True)

    if len(df) < 20:
        return {"error": "Not enough data for analysis"}

    strategy_fn  = STRATEGIES[strategy_name]
    signals      = strategy_fn(df)
    backtest     = run_backtest(df, signals, initial_capital)
    conditions   = score_current_conditions(df, strategy_name)

    return {
        "ticker":        ticker,
        "strategy":      strategy_name,
        "period":        period,
        "asset_type":    asset_type,
        "backtest":      backtest,
        "conditions":    conditions,
        "data_points":   len(df),
    }


# ── TEST ──────────────────────────────────────────────────────
if __name__ == "__main__":
    result = run_strategy_analysis("AAPL", "RSI Oversold/Overbought", "1y", "stock")
    bt = result["backtest"]
    cd = result["conditions"]

    print(f"\n{'='*55}")
    print(f"🎯 STRATEGY: RSI on AAPL (1 Year)")
    print(f"{'='*55}")
    print(f"Total Return:    {bt['total_return']:+.2f}%")
    print(f"Buy & Hold:      {bt['bh_return']:+.2f}%")
    print(f"Outperformed:    {'✅ YES' if bt['outperformed'] else '❌ NO'}")
    print(f"Win Rate:        {bt['win_rate']}%")
    print(f"Total Trades:    {bt['total_trades']}")
    print(f"Max Drawdown:    -{bt['max_drawdown']}%")
    print(f"\nCurrent Signal:  {cd['signal']}")
    print(f"Reason:          {cd['reason']}")