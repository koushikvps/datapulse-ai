# top10.py — Robinhood-style Top 10 stock panel for DataPulse AI
import yfinance as yf
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# ── Static lists ──────────────────────────────────────────────
LARGE_CAP = [
    {"ticker": "AAPL",  "name": "Apple",     "rank": 1},
    {"ticker": "MSFT",  "name": "Microsoft", "rank": 2},
    {"ticker": "NVDA",  "name": "NVIDIA",    "rank": 3},
    {"ticker": "GOOGL", "name": "Alphabet",  "rank": 4},
    {"ticker": "AMZN",  "name": "Amazon",    "rank": 5},
]

TRENDING = [
    {"ticker": "TSLA",  "name": "Tesla",     "buzz": 9.4},
    {"ticker": "META",  "name": "Meta",      "buzz": 8.7},
    {"ticker": "PLTR",  "name": "Palantir",  "buzz": 8.2},
    {"ticker": "AMD",   "name": "AMD",       "buzz": 7.9},
    {"ticker": "HOOD",  "name": "Robinhood", "buzz": 7.5},
]


@st.cache_data(ttl=300)  # cache 5 minutes
def fetch_top10_data():
    """Fetch live price, change, sparkline for all 10 tickers."""
    all_stocks = LARGE_CAP + TRENDING
    results = []
    for s in all_stocks:
        try:
            t = yf.Ticker(s["ticker"])
            hist = t.history(period="1mo", interval="1d")
            if hist.empty:
                continue
            closes = hist["Close"].tolist()
            price  = closes[-1]
            prev   = closes[-2] if len(closes) > 1 else closes[0]
            chg_pct = ((price - prev) / prev) * 100 if prev else 0
            chg     = price - prev

            info = t.fast_info
            mktcap = getattr(info, "market_cap", 0) or 0

            results.append({
                "ticker":   s["ticker"],
                "name":     s["name"],
                "price":    price,
                "chg":      chg,
                "chg_pct":  chg_pct,
                "mktcap":   mktcap,
                "sparkline": closes[-20:],   # last 20 days
                "is_large_cap": "rank" in s,
                "rank":     s.get("rank"),
                "buzz":     s.get("buzz", round(6 + abs(chg_pct) * 0.4, 1)),
            })
        except Exception:
            pass
    return results


def _sparkline_svg(prices: list, up: bool) -> str:
    """Return a tiny inline SVG sparkline (60×28px)."""
    if not prices or len(prices) < 2:
        return ""
    W, H = 60, 28
    mn, mx = min(prices), max(prices)
    rng = mx - mn if mx != mn else 1
    pts = []
    for i, p in enumerate(prices):
        x = round(i / (len(prices) - 1) * W, 1)
        y = round(H - ((p - mn) / rng) * H, 1)
        pts.append(f"{x},{y}")
    color = "#00d084" if up else "#ff4560"
    poly  = " ".join(pts)
    # fill path (closed polygon down to baseline)
    fill_pts = [f"0,{H}"] + pts + [f"{W},{H}"]
    fill_poly = " ".join(fill_pts)
    fill_color = "rgba(0,208,132,0.15)" if up else "rgba(255,69,96,0.15)"
    return (
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'xmlns="http://www.w3.org/2000/svg" style="display:block;">'
        f'<polygon points="{fill_poly}" fill="{fill_color}"/>'
        f'<polyline points="{poly}" fill="none" stroke="{color}" stroke-width="1.8" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
        f'</svg>'
    )


def _fmt_mktcap(v: float) -> str:
    if v >= 1e12: return f"${v/1e12:.1f}T"
    if v >= 1e9:  return f"${v/1e9:.1f}B"
    if v >= 1e6:  return f"${v/1e6:.1f}M"
    return "—"


def render_top10(on_select_callback):
    """
    Render the Robinhood-style Top 10 panel.
    on_select_callback(ticker: str) is called when a card is clicked.
    """
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;">
      <div style="font-family:'DM Mono',monospace;font-size:11px;color:#a78bfa;
                  text-transform:uppercase;letter-spacing:2px;">
        ▸ Top 10 — 5 Large Cap · 5 Trending
      </div>
      <div style="font-family:'DM Mono',monospace;font-size:10px;color:#334155;">
        Live · auto-refreshes every 5 min
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Loading market data..."):
        stocks = fetch_top10_data()

    if not stocks:
        st.warning("Could not load market data right now.")
        return

    large_cap = [s for s in stocks if s["is_large_cap"]]
    trending  = [s for s in stocks if not s["is_large_cap"]]

    # ── Section labels ────────────────────────────────────────
    def section_label(txt, color):
        st.markdown(
            f"<div style='font-family:DM Mono,monospace;font-size:10px;color:{color};"
            f"text-transform:uppercase;letter-spacing:2px;margin:0 0 10px;'>"
            f"{txt}</div>",
            unsafe_allow_html=True
        )

    # ── Render one row of stock cards ─────────────────────────
    def render_row(row_stocks, label, label_color, id_prefix):
        section_label(label, label_color)
        cols = st.columns(5)
        for i, s in enumerate(row_stocks):
            up        = s["chg_pct"] >= 0
            chg_color = "#00d084" if up else "#ff4560"
            chg_sign  = "+" if up else ""
            spark_svg = _sparkline_svg(s["sparkline"], up)
            price_str = f"${s['price']:,.2f}"
            rank_badge = (
                f"<span style='background:rgba(0,208,132,0.12);border:1px solid rgba(0,208,132,0.25);"
                f"border-radius:5px;padding:1px 6px;font-size:9px;color:#00d084;'>#{s['rank']}</span>"
                if s.get("rank") else ""
            )
            buzz_bar_w = min(int(s["buzz"] * 10), 100)

            card_html = f"""
            <div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:14px;
                        padding:14px 16px;margin-bottom:4px;position:relative;overflow:hidden;">
              <!-- top row: ticker + badge -->
              <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:2px;">
                <div style="font-family:'Manrope',sans-serif;font-weight:800;font-size:15px;
                            color:#e2e8f0;">{s['ticker']}</div>
                {rank_badge}
              </div>
              <!-- name -->
              <div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;
                          margin-bottom:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                {s['name']}
              </div>
              <!-- sparkline -->
              <div style="margin-bottom:8px;">{spark_svg}</div>
              <!-- price -->
              <div style="font-family:'Manrope',sans-serif;font-weight:800;font-size:16px;
                          color:#e2e8f0;margin-bottom:2px;">{price_str}</div>
              <!-- change -->
              <div style="font-family:'DM Mono',monospace;font-size:11px;color:{chg_color};
                          margin-bottom:8px;">{chg_sign}{s['chg_pct']:.2f}%</div>
              <!-- mktcap + buzz row -->
              <div style="display:flex;align-items:center;justify-content:space-between;">
                <div style="font-family:'DM Mono',monospace;font-size:9px;color:#334155;">
                  {_fmt_mktcap(s['mktcap'])}
                </div>
                <div style="display:flex;align-items:center;gap:4px;">
                  <div style="width:28px;height:3px;background:#1e2d3d;border-radius:2px;">
                    <div style="width:{buzz_bar_w}%;height:3px;background:#a78bfa;border-radius:2px;"></div>
                  </div>
                  <span style="font-family:'DM Mono',monospace;font-size:9px;color:#a78bfa;">
                    {s['buzz']:.1f}
                  </span>
                </div>
              </div>
            </div>
            """
            with cols[i]:
                st.markdown(card_html, unsafe_allow_html=True)
                # The real click button — styled to look like a subtle overlay
                st.markdown('<div class="dp-top10-btn">', unsafe_allow_html=True)
                if st.button(f"Analyze {s['ticker']}", key=f"{id_prefix}_btn_{s['ticker']}",
                             use_container_width=True):
                    on_select_callback(s["ticker"])
                st.markdown('</div>', unsafe_allow_html=True)

    render_row(large_cap, "🏆 Large Cap — Top 5 by Market Cap", "#00d084", "lc")
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    render_row(trending, "🔥 Trending — Most Buzzed Right Now", "#fb923c", "tr")
    st.markdown("<hr style='border-color:#1e2d3d;margin:24px 0 20px;'>", unsafe_allow_html=True)