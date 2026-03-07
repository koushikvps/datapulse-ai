# app.py — DataPulse AI · Clean Single Page
import streamlit as st
import plotly.graph_objects as pgo
from orchestrator import run_datapulse
from agents.stock_agent import format_market_cap
from backtester import run_strategy_analysis, STRATEGIES
from agents.strategy_agent import generate_strategy_verdict, suggest_strategies_by_risk, RISK_PROFILES

st.set_page_config(page_title="DataPulse AI", page_icon="📡", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;600;700;800&display=swap');
:root {
    --bg:#07090f; --bg2:#0d1117; --bg3:#131920;
    --bd:#1e2d3d; --bd2:#253347;
    --text:#e2e8f0; --muted:#64748b; --dim:#334155;
    --green:#00d084; --red:#ff4560; --blue:#38bdf8;
    --gold:#fbbf24; --purp:#a78bfa; --oran:#fb923c;
}
*,*::before,*::after{box-sizing:border-box;}
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stVerticalBlock"]{
    background:var(--bg)!important; color:var(--text)!important; font-family:'Manrope',sans-serif!important;
}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stSidebar"]{display:none!important;}
.block-container{padding:0!important; max-width:100%!important;}
::-webkit-scrollbar{width:4px;} ::-webkit-scrollbar-thumb{background:var(--bd2);border-radius:2px;}

/* ── ALL buttons: solid dark by default ── */
[data-testid="stButton"]>button{
    background:#131920!important; color:#e2e8f0!important;
    border:1.5px solid #253347!important; border-radius:12px!important;
    font-family:'Manrope',sans-serif!important; font-weight:700!important;
    font-size:14px!important; padding:12px 20px!important; width:100%!important;
    transition:all 0.15s ease!important; cursor:pointer!important;
}
[data-testid="stButton"]>button:hover{
    border-color:var(--green)!important; color:var(--green)!important;
    background:#0d1117!important;
}

/* ── Input ── */
[data-testid="stTextInput"] input{
    background:#131920!important; border:1.5px solid #253347!important;
    border-radius:10px!important; color:#e2e8f0!important;
    font-family:'DM Mono',monospace!important; font-size:15px!important; padding:13px 16px!important;
}
[data-testid="stTextInput"] input:focus{border-color:#00d084!important; box-shadow:0 0 0 3px rgba(0,208,132,0.15)!important; outline:none!important;}
[data-testid="stTextInput"] input::placeholder{color:#334155!important;}
[data-testid="stTextInput"] label{display:none!important;}

/* ── Selectbox ── */
[data-testid="stSelectbox"]>div>div{
    background:#131920!important; border:1.5px solid #253347!important;
    border-radius:10px!important; color:#e2e8f0!important; font-family:'DM Mono',monospace!important;
}
[data-testid="stSelectbox"] label{display:none!important;}

/* ── Spinner ── */
[data-testid="stSpinner"] p{color:#00d084!important; font-family:'DM Mono',monospace!important;}

/* ═══════════════════════════════════
   CARD BUTTON STYLES — each class targets a unique key
   ═══════════════════════════════════ */

/* Stock/Crypto toggle */
[data-testid="stButton"][id="tog_stock"]>button{
    background:#131920!important; border:1.5px solid #253347!important; color:#64748b!important;
    border-radius:10px!important; padding:10px 0!important;
}
[data-testid="stButton"][id="tog_crypto"]>button{
    background:#131920!important; border:1.5px solid #253347!important; color:#64748b!important;
    border-radius:10px!important; padding:10px 0!important;
}
[data-testid="stButton"][id="tog_stock_active"]>button{
    background:#00d084!important; color:#07090f!important; border:none!important;
    border-radius:10px!important; padding:10px 0!important; font-weight:800!important;
}
[data-testid="stButton"][id="tog_crypto_active"]>button{
    background:#fbbf24!important; color:#07090f!important; border:none!important;
    border-radius:10px!important; padding:10px 0!important; font-weight:800!important;
}

/* Action cards */
[data-testid="stButton"][id="card_analyze"]>button{
    background:#0d1117!important; border:2px solid #253347!important; color:#e2e8f0!important;
    border-radius:14px!important; padding:24px 20px!important; text-align:left!important;
    height:130px!important; font-size:16px!important; font-weight:800!important;
}
[data-testid="stButton"][id="card_analyze"]>button:hover{
    border-color:#00d084!important; background:rgba(0,208,132,0.04)!important; color:#e2e8f0!important;
}
[data-testid="stButton"][id="card_analyze_active"]>button{
    background:rgba(0,208,132,0.06)!important; border:2px solid #00d084!important;
    color:#e2e8f0!important; border-radius:14px!important; padding:24px 20px!important;
    text-align:left!important; height:130px!important; font-size:16px!important; font-weight:800!important;
}
[data-testid="stButton"][id="card_strategy"]>button{
    background:#0d1117!important; border:2px solid #253347!important; color:#e2e8f0!important;
    border-radius:14px!important; padding:24px 20px!important; text-align:left!important;
    height:130px!important; font-size:16px!important; font-weight:800!important;
}
[data-testid="stButton"][id="card_strategy"]>button:hover{
    border-color:#a78bfa!important; background:rgba(167,139,250,0.04)!important; color:#e2e8f0!important;
}
[data-testid="stButton"][id="card_strategy_active"]>button{
    background:rgba(167,139,250,0.06)!important; border:2px solid #a78bfa!important;
    color:#e2e8f0!important; border-radius:14px!important; padding:24px 20px!important;
    text-align:left!important; height:130px!important; font-size:16px!important; font-weight:800!important;
}

/* Run / action button */
[data-testid="stButton"][id="btn_run_analyze"]>button,
[data-testid="stButton"][id="btn_run_backtest"]>button,
[data-testid="stButton"][id="btn_run_risk"]>button{
    background:#00d084!important; color:#07090f!important; border:none!important;
    font-weight:800!important; font-size:15px!important; border-radius:10px!important;
    padding:14px!important;
}
[data-testid="stButton"][id="btn_run_analyze"]>button:hover,
[data-testid="stButton"][id="btn_run_backtest"]>button:hover,
[data-testid="stButton"][id="btn_run_risk"]>button:hover{
    background:#00f097!important; color:#07090f!important;
    box-shadow:0 0 20px rgba(0,208,132,0.35)!important;
}
[data-testid="stButton"][id="btn_run_backtest"]>button{background:#a78bfa!important;}
[data-testid="stButton"][id="btn_run_backtest"]>button:hover{background:#c4b5fd!important; box-shadow:0 0 20px rgba(167,139,250,0.35)!important;}

/* Strategy mode cards */
[data-testid="stButton"][id="mode_backtest"]>button{
    background:#131920!important; border:2px solid #253347!important; color:#64748b!important;
    border-radius:12px!important; padding:16px!important; height:90px!important; font-size:14px!important;
}
[data-testid="stButton"][id="mode_backtest"]>button:hover{border-color:#a78bfa!important; color:#a78bfa!important; background:#0d1117!important;}
[data-testid="stButton"][id="mode_backtest_active"]>button{
    background:rgba(167,139,250,0.1)!important; border:2px solid #a78bfa!important;
    color:#a78bfa!important; border-radius:12px!important; padding:16px!important;
    height:90px!important; font-size:14px!important; font-weight:800!important;
}
[data-testid="stButton"][id="mode_risk"]>button{
    background:#131920!important; border:2px solid #253347!important; color:#64748b!important;
    border-radius:12px!important; padding:16px!important; height:90px!important; font-size:14px!important;
}
[data-testid="stButton"][id="mode_risk"]>button:hover{border-color:#fbbf24!important; color:#fbbf24!important; background:#0d1117!important;}
[data-testid="stButton"][id="mode_risk_active"]>button{
    background:rgba(251,191,36,0.1)!important; border:2px solid #fbbf24!important;
    color:#fbbf24!important; border-radius:12px!important; padding:16px!important;
    height:90px!important; font-size:14px!important; font-weight:800!important;
}

/* Risk profile cards */
[data-testid="stButton"][id="rp_0"]>button{background:#131920!important; border:2px solid #253347!important; color:#e2e8f0!important; border-radius:13px!important; padding:18px 12px!important; height:120px!important;}
[data-testid="stButton"][id="rp_0"]>button:hover{border-color:#ff4560!important; background:rgba(255,69,96,0.05)!important;}
[data-testid="stButton"][id="rp_0_active"]>button{background:rgba(255,69,96,0.08)!important; border:2px solid #ff4560!important; color:#e2e8f0!important; border-radius:13px!important; padding:18px 12px!important; height:120px!important; font-weight:800!important;}

[data-testid="stButton"][id="rp_1"]>button{background:#131920!important; border:2px solid #253347!important; color:#e2e8f0!important; border-radius:13px!important; padding:18px 12px!important; height:120px!important;}
[data-testid="stButton"][id="rp_1"]>button:hover{border-color:#fb923c!important; background:rgba(251,146,60,0.05)!important;}
[data-testid="stButton"][id="rp_1_active"]>button{background:rgba(251,146,60,0.08)!important; border:2px solid #fb923c!important; color:#e2e8f0!important; border-radius:13px!important; padding:18px 12px!important; height:120px!important; font-weight:800!important;}

[data-testid="stButton"][id="rp_2"]>button{background:#131920!important; border:2px solid #253347!important; color:#e2e8f0!important; border-radius:13px!important; padding:18px 12px!important; height:120px!important;}
[data-testid="stButton"][id="rp_2"]>button:hover{border-color:#38bdf8!important; background:rgba(56,189,248,0.05)!important;}
[data-testid="stButton"][id="rp_2_active"]>button{background:rgba(56,189,248,0.08)!important; border:2px solid #38bdf8!important; color:#e2e8f0!important; border-radius:13px!important; padding:18px 12px!important; height:120px!important; font-weight:800!important;}

[data-testid="stButton"][id="rp_3"]>button{background:#131920!important; border:2px solid #253347!important; color:#e2e8f0!important; border-radius:13px!important; padding:18px 12px!important; height:120px!important;}
[data-testid="stButton"][id="rp_3"]>button:hover{border-color:#00d084!important; background:rgba(0,208,132,0.05)!important;}
[data-testid="stButton"][id="rp_3_active"]>button{background:rgba(0,208,132,0.08)!important; border:2px solid #00d084!important; color:#e2e8f0!important; border-radius:13px!important; padding:18px 12px!important; height:120px!important; font-weight:800!important;}

[data-testid="stButton"][id="btn_run_risk"]>button{background:#fbbf24!important; color:#07090f!important;}
[data-testid="stButton"][id="btn_run_risk"]>button:hover{background:#fcd34d!important;}
</style>
""", unsafe_allow_html=True)

# ── session state ──────────────────────────────────────────
for k, v in {"asset_type":"stock","action":None,"strategy_mode":"backtest",
              "risk_profile":"🟠 Moderate","result":None,"strategy_result":None}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── NAVBAR ──────────────────────────────────────────────────
st.markdown("""
<div style="background:#0d1117;border-bottom:1px solid #1e2d3d;padding:0 44px;height:56px;display:flex;align-items:center;justify-content:space-between;">
  <div style="display:flex;align-items:center;gap:12px;">
    <div style="width:32px;height:32px;background:linear-gradient(135deg,#00d084,#38bdf8);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;">📡</div>
    <span style="font-family:'Manrope',sans-serif;font-weight:800;font-size:20px;letter-spacing:-0.5px;color:#e2e8f0;">Data<span style="color:#00d084;">Pulse</span><span style="font-size:12px;color:#64748b;font-weight:400;margin-left:8px;">AI</span></span>
  </div>
  <div style="display:flex;align-items:center;gap:7px;">
    <div style="width:6px;height:6px;border-radius:50%;background:#00d084;box-shadow:0 0 7px #00d084;"></div>
    <span style="font-family:'DM Mono',monospace;font-size:11px;color:#64748b;">5 agents · Llama 3.3 70B · LangGraph</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='padding:40px 48px 0;'>", unsafe_allow_html=True)

# ── HERO ────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-bottom:28px;">
  <div style="font-family:'Manrope',sans-serif;font-size:46px;font-weight:800;color:#e2e8f0;letter-spacing:-1.5px;line-height:1.1;margin-bottom:10px;">
    AI intelligence on<br><span style="color:#00d084;">stocks &amp; crypto.</span>
  </div>
  <div style="font-size:15px;color:#64748b;">Enter any ticker · Choose what you want to do · Results in seconds.</div>
</div>
""", unsafe_allow_html=True)

# ── ASSET TOGGLE — pure buttons, no floating HTML ───────────
at = st.session_state.asset_type
_, tc1, tc2, _ = st.columns([3, 1, 1, 3])
with tc1:
    if at == "stock":
        if st.button("📈  Stock", key="tog_stock_active"):
            pass  # already active
    else:
        if st.button("📈  Stock", key="tog_stock"):
            st.session_state.asset_type = "stock"
            st.rerun()
with tc2:
    if at == "crypto":
        if st.button("🪙  Crypto", key="tog_crypto_active"):
            pass
    else:
        if st.button("🪙  Crypto", key="tog_crypto"):
            st.session_state.asset_type = "crypto"
            st.rerun()

asset_type  = st.session_state.asset_type
placeholder = "AAPL · Tesla · NVIDIA · Microsoft..." if asset_type == "stock" else "BTC · ETH · SOL · DOGE · XRP..."

# ── SEARCH ──────────────────────────────────────────────────
_, sc_col, _ = st.columns([1, 4, 1])
with sc_col:
    query = st.text_input("q", placeholder=placeholder, key="main_query", label_visibility="collapsed")

picks = ["AAPL","TSLA","NVDA","MSFT","GOOGL","AMZN","META"] if asset_type=="stock" else ["BTC","ETH","SOL","DOGE","XRP","ADA","AVAX"]
chips = "<div style='display:flex;justify-content:center;gap:7px;margin:10px 0 28px;flex-wrap:wrap;'>"
for t in picks:
    chips += f"<span style='background:#131920;border:1px solid #253347;border-radius:7px;padding:4px 11px;font-family:DM Mono,monospace;font-size:12px;color:#64748b;'>{t}</span>"
chips += "</div>"
st.markdown(chips, unsafe_allow_html=True)

# ── ACTION CARDS — native buttons with emoji+text ───────────
st.markdown("<div style='font-family:DM Mono,monospace;font-size:11px;color:#a78bfa;text-transform:uppercase;letter-spacing:2px;margin-bottom:12px;'>▸ What would you like to do?</div>", unsafe_allow_html=True)

act = st.session_state.action
ac1, ac2 = st.columns(2)

with ac1:
    key_a = "card_analyze_active" if act=="analyze" else "card_analyze"
    label_a = "📡  Analyze Asset\n\n5 AI agents · Live price · News · Sentiment · Risk · Buy/Hold/Sell"
    if st.button(label_a, key=key_a):
        st.session_state.action = "analyze"
        st.session_state.result = None
        st.rerun()

with ac2:
    key_s = "card_strategy_active" if act=="strategy" else "card_strategy"
    label_s = "⚡  Strategy & Backtest\n\nBacktest strategies · Risk Profile Advisor · AI picks for you"
    if st.button(label_s, key=key_s):
        st.session_state.action = "strategy"
        st.session_state.strategy_result = None
        st.rerun()

st.markdown("<hr style='border-color:#1e2d3d;margin:28px 0;'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# ANALYZE FLOW
# ════════════════════════════════════════════════════════════
if st.session_state.action == "analyze":
    st.markdown("<div style='font-family:DM Mono,monospace;font-size:11px;color:#00d084;text-transform:uppercase;letter-spacing:2px;margin-bottom:16px;'>▸ Analyze — real-time AI report</div>", unsafe_allow_html=True)

    _, btn_col, _ = st.columns([2, 2, 2])
    with btn_col:
        run_analyze = st.button("🚀  Run AI Analysis", key="btn_run_analyze", use_container_width=True)

    if run_analyze:
        if not query.strip():
            st.warning("⚠️ Please enter a ticker above!")
        else:
            prog = st.empty()
            def show_prog(done, active):
                agents = [("🔎","Resolver"),("📈","Stock"),("📰","News"),("💬","Sentiment"),("⚠️","Risk"),("🧠","Analyst")]
                h = "<div style='display:flex;gap:8px;flex-wrap:wrap;margin:16px 0;'>"
                for icon, name in agents:
                    if name in done:
                        s = "background:rgba(0,208,132,0.12);border:1px solid #00d084;color:#00d084;"; p = "✓ "
                    elif name == active:
                        s = "background:rgba(56,189,248,0.12);border:1px solid #38bdf8;color:#38bdf8;"; p = "⟳ "
                    else:
                        s = "background:#131920;border:1px solid #1e2d3d;color:#334155;"; p = "○ "
                    h += f"<div style='{s}border-radius:20px;padding:5px 14px;font-family:DM Mono,monospace;font-size:12px;'>{icon} {p}{name}</div>"
                h += "</div>"
                return h

            prog.markdown(show_prog([], "Resolver"), unsafe_allow_html=True)
            with st.spinner(f"Analyzing {query.strip()}..."):
                try:
                    prog.markdown(show_prog(["Resolver"], "Stock"), unsafe_allow_html=True)
                    result = run_datapulse(query.strip(), asset_type=asset_type)
                    prog.markdown(show_prog(["Resolver","Stock","News","Sentiment","Risk","Analyst"],""), unsafe_allow_html=True)
                    st.session_state.result = result
                except Exception as e:
                    st.error(f"❌ {e}")

    result = st.session_state.result
    if result:
        stock    = result.get("stock_data", {})
        news     = result.get("news_articles", [])
        news_s   = result.get("news_sentiment", {})
        social   = result.get("social_sentiment", {})
        risk     = result.get("risk", {})
        analysis = result.get("analysis", {})
        company  = result.get("company_name", query)
        ticker   = result.get("ticker", "")
        price      = stock.get("current_price", 0)
        chg        = stock.get("change", 0)
        chg_pct    = stock.get("change_pct", 0)
        mktcap     = format_market_cap(stock.get("market_cap", 0))
        rec        = analysis.get("recommendation", "HOLD")
        rec_emoji  = analysis.get("rec_emoji", "🟡")
        target     = analysis.get("price_target", price)
        upside     = analysis.get("upside_pct", 0)
        risk_score = risk.get("overall_score", 5)
        risk_label = risk.get("overall_label", "Medium")
        risk_emoji = risk.get("overall_emoji", "🟡")
        bull_pct   = social.get("bull_pct", 50)
        bear_pct   = social.get("bear_pct", 50)
        chg_color  = "#00d084" if chg >= 0 else "#ff4560"
        chg_sign   = "+" if chg >= 0 else ""
        a_color    = "#fbbf24" if asset_type=="crypto" else "#00d084"
        price_fmt  = f"{price:,.4f}" if asset_type=="crypto" and price < 1 else f"{price:,.2f}"

        st.markdown(f"""
        <div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:16px;padding:22px 28px;margin-bottom:18px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
          <div>
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
              <div style="font-family:'Manrope',sans-serif;font-size:26px;font-weight:800;color:#e2e8f0;">{company}</div>
              <div style="border:1px solid {a_color}44;border-radius:10px;padding:2px 9px;font-family:'DM Mono',monospace;font-size:11px;color:{a_color};">{'🪙 Crypto' if asset_type=='crypto' else '📈 Stock'}</div>
            </div>
            <div style="font-family:'DM Mono',monospace;font-size:12px;color:#64748b;">{ticker} · {stock.get('sector','—')} · {stock.get('industry','—')}</div>
          </div>
          <div style="display:flex;align-items:baseline;gap:10px;">
            <div style="font-family:'Manrope',sans-serif;font-size:38px;font-weight:800;color:#e2e8f0;letter-spacing:-1px;">${price_fmt}</div>
            <div style="font-family:'DM Mono',monospace;font-size:15px;color:{chg_color};">{chg_sign}{chg:.2f} ({chg_sign}{chg_pct:.2f}%)</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        mc1,mc2,mc3,mc4 = st.columns(4)
        rec_bg = "rgba(0,208,132,0.07)" if rec=="BUY" else ("rgba(255,69,96,0.07)" if rec=="SELL" else "rgba(251,191,36,0.07)")
        rec_bd = "#00d084" if rec=="BUY" else ("#ff4560" if rec=="SELL" else "#fbbf24")
        for col,icon,lbl,val,sub,bg,bd in [
            (mc1,"📈","Recommendation",f"{rec_emoji} {rec}",f"Target ${target:,.2f} ({chg_sign}{upside:.1f}%)",rec_bg,rec_bd),
            (mc2,"⚠️","Risk Level",f"{risk_emoji} {risk_score}/10",risk_label,"#131920","#253347"),
            (mc3,"💬","Social Mood",f"{'🟢' if bull_pct>55 else '🔴' if bull_pct<45 else '🟡'} {bull_pct}% Bulls",f"{bear_pct}% Bears","#131920","#253347"),
            (mc4,"🏢","Market Cap",mktcap,f"Vol: {stock.get('volume',0):,.0f}","#131920","#253347"),
        ]:
            with col:
                st.markdown(f"""<div style="background:{bg};border:1px solid {bd};border-radius:13px;padding:18px 20px;height:106px;margin-bottom:18px;">
                  <div style="font-size:11px;font-family:'DM Mono',monospace;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:7px;">{icon} {lbl}</div>
                  <div style="font-family:'Manrope',sans-serif;font-size:22px;font-weight:800;color:#e2e8f0;line-height:1;">{val}</div>
                  <div style="font-size:11px;color:#64748b;margin-top:5px;font-family:'DM Mono',monospace;">{sub}</div>
                </div>""", unsafe_allow_html=True)

        pc1,pc2 = st.columns([3,2])
        with pc1:
            st.markdown("<div style='font-family:DM Mono,monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;'>📈 30-day price chart</div>", unsafe_allow_html=True)
            ph = stock.get("price_history",[])
            if ph:
                lc = "#00d084" if ph[-1]>=ph[0] else "#ff4560"
                fig=pgo.Figure(); fig.add_trace(pgo.Scatter(y=ph,mode="lines",line=dict(color=lc,width=2.5),fill="tozeroy",fillcolor=f"rgba({'0,208,132' if lc=='#00d084' else '255,69,96'},0.07)",hovertemplate="$%{y:,.2f}<extra></extra>"))
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=190,margin=dict(l=0,r=0,t=4,b=0),xaxis=dict(showgrid=False,showticklabels=False,zeroline=False),yaxis=dict(showgrid=True,gridcolor="rgba(30,45,61,0.7)",tickfont=dict(color="#64748b",size=10,family="DM Mono"),zeroline=False),showlegend=False)
                st.plotly_chart(fig,use_container_width=True,config={"displayModeBar":False})
            lo52=stock.get("week_52_low",0); hi52=stock.get("week_52_high",0)
            if hi52 and lo52 and hi52!=lo52:
                pos=min(max((price-lo52)/(hi52-lo52)*100,2),98)
                st.markdown(f"""<div style="background:#131920;border:1px solid #1e2d3d;border-radius:10px;padding:12px 16px;margin-top:4px;">
                  <div style="display:flex;justify-content:space-between;margin-bottom:7px;"><span style="font-family:'DM Mono',monospace;font-size:11px;color:#64748b;">52W LOW ${lo52:,.2f}</span><span style="font-family:'DM Mono',monospace;font-size:11px;color:#64748b;">52W HIGH ${hi52:,.2f}</span></div>
                  <div style="background:#1e2d3d;border-radius:4px;height:5px;position:relative;"><div style="background:linear-gradient(90deg,#ff4560,#fbbf24,#00d084);border-radius:4px;height:5px;width:100%;"></div><div style="position:absolute;top:-4px;left:{pos:.1f}%;width:13px;height:13px;background:white;border-radius:50%;border:2px solid #0d1117;transform:translateX(-50%);"></div></div>
                  <div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;text-align:center;margin-top:5px;">At {pos:.0f}% of 52-week range</div>
                </div>""", unsafe_allow_html=True)
        with pc2:
            st.markdown(f"<div style='font-family:DM Mono,monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;'>📰 news · {news_s.get('emoji','🟡')} {news_s.get('overall','Neutral')} {news_s.get('score',5)}/10</div>", unsafe_allow_html=True)
            for a in news[:6]:
                sc2="#00d084" if a.get("sentiment")=="positive" else("#ff4560" if a.get("sentiment")=="negative" else "#fbbf24")
                st.markdown(f"""<a href="{a.get('url','#')}" target="_blank" style="text-decoration:none;">
                  <div style="background:#131920;border:1px solid #1e2d3d;border-left:3px solid {sc2};border-radius:0 9px 9px 0;padding:9px 13px;margin-bottom:6px;">
                    <div style="font-size:12px;color:#e2e8f0;font-weight:500;line-height:1.4;margin-bottom:2px;">{a.get('emoji','🟡')} {a.get('title','')[:68]}</div>
                    <div style="display:flex;justify-content:space-between;"><span style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;">{a.get('source','')}</span><span style="font-family:'DM Mono',monospace;font-size:10px;color:{sc2};">{a.get('score',5)}/10</span></div>
                  </div></a>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        rs1,rs2=st.columns([3,2])
        with rs1:
            st.markdown(f"<div style='font-family:DM Mono,monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;'>⚠️ risk breakdown · {risk_emoji} {risk_label}</div>", unsafe_allow_html=True)
            dims=risk.get("dimensions",[])
            if dims:
                fig2=pgo.Figure(); fig2.add_trace(pgo.Bar(x=[d["score"] for d in dims],y=[d["name"] for d in dims],orientation="h",marker=dict(color=["#ff4560" if d["score"]>=7 else "#fbbf24" if d["score"]>=5 else "#00d084" for d in dims],opacity=0.85),text=[f"{d['score']}/10" for d in dims],textposition="outside",textfont=dict(color="#94a3b8",size=11,family="DM Mono"),hovertemplate="%{y}: %{x}/10<extra></extra>"))
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=190,margin=dict(l=0,r=40,t=0,b=0),xaxis=dict(range=[0,13],showgrid=False,showticklabels=False,zeroline=False),yaxis=dict(tickfont=dict(color="#94a3b8",size=11,family="DM Mono"),zeroline=False),showlegend=False,bargap=0.35)
                st.plotly_chart(fig2,use_container_width=True,config={"displayModeBar":False})
            for r_item in risk.get("key_risks",[]):
                st.markdown(f"<div style='background:rgba(255,69,96,0.07);border:1px solid rgba(255,69,96,0.18);border-radius:8px;padding:7px 13px;margin-bottom:5px;font-size:13px;color:#e2e8f0;'>⚡ {r_item}</div>", unsafe_allow_html=True)
        with rs2:
            st.markdown("<div style='font-family:DM Mono,monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;'>💬 social sentiment</div>", unsafe_allow_html=True)
            fig3=pgo.Figure(pgo.Pie(values=[bull_pct,bear_pct],labels=["Bulls 🟢","Bears 🔴"],hole=0.68,marker=dict(colors=["#00d084","#ff4560"]),textinfo="none",hovertemplate="%{label}: %{value}%<extra></extra>"))
            fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)",height=170,margin=dict(l=0,r=0,t=0,b=0),showlegend=True,legend=dict(font=dict(color="#94a3b8",size=11,family="DM Mono"),bgcolor="rgba(0,0,0,0)"),annotations=[dict(text=f"<b>{bull_pct}%</b><br>Bulls",x=0.5,y=0.5,font=dict(size=15,color="#e2e8f0",family="Manrope"),showarrow=False)])
            st.plotly_chart(fig3,use_container_width=True,config={"displayModeBar":False})
            buzz=social.get("buzz_score",5); themes=social.get("key_themes",[])
            th_html=""
            if themes:
                th_html="<div style='display:flex;flex-wrap:wrap;gap:5px;margin-top:8px;'>"
                for t in themes:
                    th_html+=f"<span style='background:rgba(56,189,248,0.1);border:1px solid rgba(56,189,248,0.2);border-radius:14px;padding:3px 10px;font-size:11px;color:#38bdf8;font-family:DM Mono,monospace;'>{t}</span>"
                th_html+="</div>"
            st.markdown(f"""<div style="background:#131920;border:1px solid #1e2d3d;border-radius:10px;padding:13px 16px;">
              <div style="display:flex;justify-content:space-between;margin-bottom:7px;"><span style="font-family:'DM Mono',monospace;font-size:11px;color:#64748b;">Buzz</span><span style="font-family:'DM Mono',monospace;font-size:11px;color:#00d084;font-weight:700;">{buzz}/10</span></div>
              <div style="background:#1e2d3d;border-radius:4px;height:4px;margin-bottom:10px;"><div style="background:#00d084;border-radius:4px;height:4px;width:{buzz*10}%;"></div></div>
              <div style="font-size:12px;color:#94a3b8;line-height:1.6;">{social.get('summary','')}</div>{th_html}
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        rec_bg2="rgba(0,208,132,0.05)" if rec=="BUY" else("rgba(255,69,96,0.05)" if rec=="SELL" else "rgba(251,191,36,0.05)")
        rec_bd2="rgba(0,208,132,0.28)" if rec=="BUY" else("rgba(255,69,96,0.28)" if rec=="SELL" else "rgba(251,191,36,0.28)")
        rec_col="#00d084" if rec=="BUY" else("#ff4560" if rec=="SELL" else "#fbbf24")
        st.markdown(f"""<div style="background:{rec_bg2};border:1px solid {rec_bd2};border-radius:16px;padding:26px 30px;margin-bottom:18px;">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:18px;flex-wrap:wrap;gap:12px;">
            <div><div style="font-family:'DM Mono',monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:5px;">🧠 AI analyst report</div><div style="font-family:'Manrope',sans-serif;font-size:21px;font-weight:800;color:#e2e8f0;">{analysis.get('verdict_headline','')}</div></div>
            <div style="text-align:right;"><div style="font-family:'Manrope',sans-serif;font-size:34px;font-weight:900;color:{rec_col};">{rec_emoji} {rec}</div><div style="font-family:'DM Mono',monospace;font-size:12px;color:#64748b;">Target ${target:,.2f} · {analysis.get('time_horizon','12mo')}</div></div>
          </div>
          <div style="font-size:14px;color:#e2e8f0;line-height:1.8;border-left:3px solid {rec_col};padding-left:14px;">{analysis.get('thesis','')}</div>
        </div>""", unsafe_allow_html=True)

        ab,as_,ac2 = st.columns(3)
        with ab:
            st.markdown(f"<div style='background:rgba(0,208,132,0.05);border:1px solid rgba(0,208,132,0.2);border-radius:13px;padding:18px;'><div style='font-family:DM Mono,monospace;font-size:10px;color:#00d084;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>📈 Bull Case</div><div style='font-size:13px;color:#e2e8f0;line-height:1.7;'>{analysis.get('bull_case','')}</div></div>", unsafe_allow_html=True)
        with as_:
            st.markdown(f"<div style='background:rgba(255,69,96,0.05);border:1px solid rgba(255,69,96,0.2);border-radius:13px;padding:18px;'><div style='font-family:DM Mono,monospace;font-size:10px;color:#ff4560;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>📉 Bear Case</div><div style='font-size:13px;color:#e2e8f0;line-height:1.7;'>{analysis.get('bear_case','')}</div></div>", unsafe_allow_html=True)
        with ac2:
            ch="<div style='background:#131920;border:1px solid #253347;border-radius:13px;padding:18px;'><div style='font-family:DM Mono,monospace;font-size:10px;color:#38bdf8;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;'>⚡ Catalysts</div>"
            for cat in analysis.get("catalysts",[]):
                ch+=f"<div style='font-size:12px;color:#e2e8f0;padding:5px 0;border-bottom:1px solid #1e2d3d;line-height:1.5;'>→ {cat}</div>"
            ch+="</div>"
            st.markdown(ch, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""<div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:13px;padding:22px 26px;">
          <div style="font-family:'DM Mono',monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;">📊 detailed analysis</div>
          <div style="font-size:14px;color:#94a3b8;line-height:1.9;">{analysis.get('detailed_analysis','')}</div>
        </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# STRATEGY FLOW
# ════════════════════════════════════════════════════════════
elif st.session_state.action == "strategy":
    st.markdown("<div style='font-family:DM Mono,monospace;font-size:11px;color:#a78bfa;text-transform:uppercase;letter-spacing:2px;margin-bottom:16px;'>▸ Strategy engine — backtest & risk profile</div>", unsafe_allow_html=True)

    # Mode selector — two buttons styled as cards
    mode = st.session_state.strategy_mode
    m1, m2, _ = st.columns([2, 2, 2])
    with m1:
        mk1 = "mode_backtest_active" if mode=="backtest" else "mode_backtest"
        if st.button("📊  Backtest a Strategy\nTest on real historical data", key=mk1):
            st.session_state.strategy_mode = "backtest"
            st.session_state.strategy_result = None
            st.rerun()
    with m2:
        mk2 = "mode_risk_active" if mode=="risk" else "mode_risk"
        if st.button("🎯  Risk Profile Advisor\nAI picks strategy for you", key=mk2):
            st.session_state.strategy_mode = "risk"
            st.session_state.strategy_result = None
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── BACKTEST ──
    if mode == "backtest":
        st.markdown("<div style='background:#0d1117;border:1px solid #253347;border-radius:14px;padding:22px 26px;margin-bottom:16px;'>", unsafe_allow_html=True)
        bc1,bc2,bc3 = st.columns(3)
        with bc1:
            s_asset    = st.selectbox("Asset", ["📈 Stock","🪙 Crypto"], key="bt_asset")
        with bc2:
            s_strategy = st.selectbox("Strategy", list(STRATEGIES.keys()), key="bt_strategy")
        with bc3:
            s_period   = st.selectbox("Period", ["3mo","6mo","1y","2y"], index=2, key="bt_period")
        st.markdown("</div>", unsafe_allow_html=True)

        sinfo = {
            "RSI Oversold/Overbought":    ("📉","Buy RSI<30 · Sell RSI>70 · Mean-reversion","Sideways markets","#38bdf8"),
            "Moving Average Crossover":   ("📊","Golden Cross buy · Death Cross sell","Trending markets","#00d084"),
            "Momentum / Trend Following": ("🚀","Buy +5% momentum · Sell -5% momentum","Bull & bear runs","#a78bfa"),
            "Value Investing":            ("💎","Buy 20% below 200MA · Sell 20% above","Long-term investors","#fbbf24"),
            "Buy the Dip":                ("🎯","Buy 5% drop in 3d + RSI<40 · Panic sell-offs","Volatile assets & crypto","#ff4560"),
        }
        si = sinfo.get(s_strategy, ("📊","","","#00d084"))
        st.markdown(f"""<div style="background:#131920;border:1px solid {si[3]}44;border-radius:11px;padding:14px 20px;margin-bottom:16px;display:flex;align-items:center;gap:14px;">
          <div style="font-size:26px;flex-shrink:0;">{si[0]}</div>
          <div><div style="font-weight:700;font-size:15px;color:#e2e8f0;margin-bottom:3px;">{s_strategy}</div>
          <div style="font-size:12px;color:#64748b;">{si[1]} · <span style="color:{si[3]};">Best for: {si[2]}</span></div></div>
        </div>""", unsafe_allow_html=True)

        run_bt = st.button("⚡  Run Backtest", key="btn_run_backtest", use_container_width=True)

        if run_bt:
            if not query.strip():
                st.warning("⚠️ Enter a ticker in the search box above!")
            else:
                ticker_clean = query.strip().upper()
                asset_clean  = "crypto" if "Crypto" in s_asset else "stock"
                with st.spinner(f"Running {s_strategy} on {ticker_clean}..."):
                    try:
                        res = run_strategy_analysis(ticker_clean, s_strategy, s_period, asset_clean)
                        if "error" in res:
                            st.error(f"❌ {res['error']}")
                        else:
                            bt      = res["backtest"]
                            cd      = res["conditions"]
                            verdict = generate_strategy_verdict(ticker_clean, s_strategy, bt, cd, asset_clean)
                            st.session_state.strategy_result = {"type":"backtest","bt":bt,"cd":cd,"verdict":verdict,"ticker":ticker_clean,"strategy":s_strategy,"period":s_period}
                    except Exception as e:
                        st.error(f"❌ {e}")

        sr = st.session_state.strategy_result
        if sr and sr.get("type") == "backtest":
            bt=sr["bt"]; cd=sr["cd"]; verdict=sr["verdict"]
            total_ret=bt["total_return"]; bh_ret=bt["bh_return"]; outperform=bt["outperformed"]
            win_rate=bt["win_rate"]; max_dd=bt["max_drawdown"]; n_trades=bt["total_trades"]; final_val=bt["final_value"]
            v_color="#00d084" if verdict.get("verdict_emoji")=="🟢" else("#ff4560" if verdict.get("verdict_emoji")=="🔴" else "#fbbf24")
            ret_color="#00d084" if total_ret>=0 else "#ff4560"; bh_color="#00d084" if bh_ret>=0 else "#ff4560"
            ret_sign="+" if total_ret>=0 else ""; bh_sign="+" if bh_ret>=0 else ""

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""<div style="background:#0d1117;border:1px solid {v_color};border-radius:14px;padding:22px 28px;margin-bottom:20px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
              <div><div style="font-family:'DM Mono',monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:5px;">⚡ {sr['strategy']} · {sr['ticker']} · {sr['period']}</div><div style="font-family:'Manrope',sans-serif;font-size:22px;font-weight:800;color:#e2e8f0;">{verdict.get('overall_verdict','')}</div></div>
              <div style="text-align:right;"><div style="font-family:'Manrope',sans-serif;font-size:30px;font-weight:900;color:{v_color};">{verdict.get('verdict_emoji','')} {verdict.get('strategy_score',5)}/10</div><div style="font-family:'DM Mono',monospace;font-size:12px;color:#64748b;">{verdict.get('confidence','Medium')} Confidence</div></div>
            </div>""", unsafe_allow_html=True)

            bm1,bm2,bm3,bm4,bm5 = st.columns(5)
            beat_color = "#00d084" if outperform else "#ff4560"
            beat_text  = "✅ Beat market" if outperform else "❌ Underperformed"
            beat_badge = f"<div style='font-size:10px;margin-top:4px;font-family:DM Mono,monospace;color:{beat_color};'>{beat_text}</div>"
            for col,lbl,val,sub,color,extra in [
                (bm1,"Strategy Return",f"{ret_sign}{total_ret:.1f}%","From $10,000",ret_color,beat_badge),
                (bm2,"Buy & Hold",f"{bh_sign}{bh_ret:.1f}%","Benchmark",bh_color,""),
                (bm3,"Win Rate",f"{win_rate:.0f}%",f"{n_trades} trades","#38bdf8",""),
                (bm4,"Max Drawdown",f"-{max_dd:.1f}%","Peak→Trough","#ff4560",""),
                (bm5,"Final Value",f"${final_val:,.0f}","From $10,000","#a78bfa",""),
            ]:
                with col:
                    st.markdown(f"""<div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:13px;padding:16px;margin-bottom:16px;text-align:center;">
                      <div style="font-size:10px;font-family:'DM Mono',monospace;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:7px;">{lbl}</div>
                      <div style="font-family:'Manrope',sans-serif;font-size:24px;font-weight:800;color:{color};line-height:1;">{val}</div>
                      <div style="font-size:10px;color:#64748b;margin-top:4px;font-family:'DM Mono',monospace;">{sub}</div>{extra}
                    </div>""", unsafe_allow_html=True)

            eq1,eq2 = st.columns([3,2])
            with eq1:
                st.markdown("<div style='font-family:DM Mono,monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;'>📈 equity curve vs buy &amp; hold</div>", unsafe_allow_html=True)
                eq_data=bt.get("equity_curve",[]); prices=bt.get("price_history",[])
                if eq_data and prices:
                    eq_vals=[e["value"] for e in eq_data]; eq_dates=[e["date"] for e in eq_data]
                    start=prices[max(0,len(prices)-len(eq_vals))]
                    bh_vals=[10000*(p/start) for p in prices[max(0,len(prices)-len(eq_vals)):]]
                    fig_eq=pgo.Figure()
                    fig_eq.add_trace(pgo.Scatter(y=eq_vals,x=eq_dates,mode="lines",name="Strategy",line=dict(color="#a78bfa",width=2.5),hovertemplate="Strategy: $%{y:,.0f}<extra></extra>"))
                    fig_eq.add_trace(pgo.Scatter(y=bh_vals[:len(eq_vals)],x=eq_dates,mode="lines",name="Buy & Hold",line=dict(color="#64748b",width=1.5,dash="dot"),hovertemplate="B&H: $%{y:,.0f}<extra></extra>"))
                    fig_eq.add_hline(y=10000,line_dash="dash",line_color="#334155",line_width=1)
                    fig_eq.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=230,margin=dict(l=0,r=0,t=4,b=0),xaxis=dict(showgrid=False,tickfont=dict(color="#64748b",size=10,family="DM Mono")),yaxis=dict(showgrid=True,gridcolor="rgba(30,45,61,0.7)",tickfont=dict(color="#64748b",size=10,family="DM Mono"),tickprefix="$",zeroline=False),legend=dict(font=dict(color="#94a3b8",size=11,family="DM Mono"),bgcolor="rgba(0,0,0,0)",x=0,y=1),hovermode="x unified")
                    st.plotly_chart(fig_eq,use_container_width=True,config={"displayModeBar":False})
            with eq2:
                st.markdown("<div style='font-family:DM Mono,monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;'>🎯 current signal</div>", unsafe_allow_html=True)
                sig=cd.get("signal","NEUTRAL"); sig_color="#00d084" if "BUY" in sig or "DIP" in sig else("#ff4560" if "SELL" in sig else "#fbbf24"); sig_score=cd.get("score",5)
                st.markdown(f"""<div style="background:#131920;border:1px solid {sig_color}55;border-radius:13px;padding:18px;margin-bottom:12px;">
                  <div style="font-family:'Manrope',sans-serif;font-size:22px;font-weight:900;color:{sig_color};margin-bottom:7px;">{sig}</div>
                  <div style="font-size:12px;color:#e2e8f0;line-height:1.6;margin-bottom:12px;">{cd.get('reason','')}</div>
                  <div style="background:#1e2d3d;border-radius:4px;height:5px;"><div style="background:{sig_color};border-radius:4px;height:5px;width:{sig_score*10}%;"></div></div>
                </div>""", unsafe_allow_html=True)
                ind_html="<div style='background:#131920;border:1px solid #1e2d3d;border-radius:11px;padding:14px;'>"
                for name,val2,suffix in [("RSI",cd.get("rsi"),""),("SMA 20",cd.get("sma20"),"$"),("SMA 50",cd.get("sma50"),"$"),("SMA 200",cd.get("sma200"),"$"),("Momentum",cd.get("momentum"),"%")]:
                    if val2 is not None:
                        ind_html+=f"<div style='display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #1e2d3d;'><span style='font-family:DM Mono,monospace;font-size:11px;color:#64748b;'>{name}</span><span style='font-family:DM Mono,monospace;font-size:11px;color:#e2e8f0;font-weight:600;'>{suffix}{val2}</span></div>"
                ind_html+="</div>"
                st.markdown(ind_html, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            a_color="#00d084" if verdict.get("action_now")=="EXECUTE" else("#ff4560" if verdict.get("action_now")=="AVOID" else "#fbbf24")
            st.markdown(f"""<div style="background:rgba(167,139,250,0.05);border:1px solid rgba(167,139,250,0.22);border-radius:14px;padding:24px 28px;margin-bottom:18px;">
              <div style="font-family:'DM Mono',monospace;font-size:11px;color:#a78bfa;text-transform:uppercase;letter-spacing:2px;margin-bottom:14px;">🧠 AI quant verdict</div>
              <div style="display:flex;gap:20px;flex-wrap:wrap;align-items:flex-start;margin-bottom:16px;">
                <div style="background:#131920;border:1.5px solid {a_color};border-radius:11px;padding:14px 20px;text-align:center;flex-shrink:0;">
                  <div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;margin-bottom:5px;">ACTION NOW</div>
                  <div style="font-family:'Manrope',sans-serif;font-size:22px;font-weight:900;color:{a_color};">{verdict.get('action_emoji','')} {verdict.get('action_now','WAIT')}</div>
                </div>
                <div style="flex:1;min-width:180px;">
                  <div style="font-size:14px;color:#e2e8f0;line-height:1.8;margin-bottom:10px;">{verdict.get('summary','')}</div>
                  <div style="font-size:13px;color:#64748b;line-height:1.7;">{verdict.get('current_opportunity','')}</div>
                </div>
              </div>
              <div style="display:flex;gap:10px;flex-wrap:wrap;">
                <div style="flex:1;background:rgba(255,69,96,0.07);border:1px solid rgba(255,69,96,0.18);border-radius:9px;padding:12px 16px;min-width:160px;">
                  <div style="font-family:'DM Mono',monospace;font-size:10px;color:#ff4560;margin-bottom:5px;text-transform:uppercase;">⚠️ Risk Warning</div>
                  <div style="font-size:12px;color:#e2e8f0;line-height:1.6;">{verdict.get('risk_warning','')}</div>
                </div>
                <div style="flex:1;background:rgba(56,189,248,0.07);border:1px solid rgba(56,189,248,0.18);border-radius:9px;padding:12px 16px;min-width:160px;">
                  <div style="font-family:'DM Mono',monospace;font-size:10px;color:#38bdf8;margin-bottom:5px;text-transform:uppercase;">💡 Pro Tip</div>
                  <div style="font-size:12px;color:#e2e8f0;line-height:1.6;">{verdict.get('pro_tip','')}</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

            trades=bt.get("recent_trades",[])
            if trades:
                st.markdown("<div style='font-family:DM Mono,monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:12px;'>📋 recent trades</div>", unsafe_allow_html=True)
                st.markdown("""<div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:13px;overflow:hidden;">
                  <div style="display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr 1fr;padding:9px 18px;background:#131920;border-bottom:1px solid #1e2d3d;">
                    <div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;text-transform:uppercase;">Date</div>
                    <div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;text-transform:uppercase;">Entry</div>
                    <div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;text-transform:uppercase;">Exit</div>
                    <div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;text-transform:uppercase;">P&amp;L</div>
                    <div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;text-transform:uppercase;">Result</div>
                  </div>""", unsafe_allow_html=True)
                for trade in reversed(trades):
                    pnl=trade.get("pnl_pct",0); tc="#00d084" if pnl>=0 else "#ff4560"; tsign="+" if pnl>=0 else ""; tres=trade.get("result","")
                    st.markdown(f"""<div style="display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr 1fr;padding:10px 18px;border-bottom:1px solid #1e2d3d;font-family:'DM Mono',monospace;font-size:12px;">
                      <div style="color:#64748b;">{trade.get('date','')}</div><div style="color:#e2e8f0;">${trade.get('entry',0):,.2f}</div><div style="color:#e2e8f0;">${trade.get('exit',0):,.2f}</div>
                      <div style="color:{tc};font-weight:700;">{tsign}{pnl:.2f}%</div><div style="color:{tc};">{'✅' if tres=='WIN' else '❌'} {tres}</div>
                    </div>""", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    # ── RISK PROFILE ──
    else:
        PROFILE_META = {
            "🔴 Aggressive": {"color":"#ff4560","idx":0,"short":"High risk · High reward","time":"1–6 months"},
            "🟠 Moderate":   {"color":"#fb923c","idx":1,"short":"Balanced risk & growth","time":"6–18 months"},
            "🟡 Low Risk":   {"color":"#38bdf8","idx":2,"short":"Capital preservation","time":"1–3 years"},
            "🟢 No Risk":    {"color":"#00d084","idx":3,"short":"Safety above all","time":"3–5+ years"},
        }

        st.markdown("<div style='font-family:DM Mono,monospace;font-size:11px;color:#fbbf24;text-transform:uppercase;letter-spacing:2px;margin-bottom:14px;'>Step 1 — Select your risk profile</div>", unsafe_allow_html=True)

        sel = st.session_state.risk_profile
        rp_cols = st.columns(4)

        for rp_key, rp_data in RISK_PROFILES.items():
            pm  = PROFILE_META[rp_key]
            i   = pm["idx"]
            pc  = pm["color"]
            is_sel = sel == rp_key
            key_id = f"rp_{i}_active" if is_sel else f"rp_{i}"
            chk = "✓ " if is_sel else ""
            label = f"{chk}{rp_key.split()[0]} {rp_data['label']}\n{pm['short']}\n{pm['time']}"
            with rp_cols[i]:
                if st.button(label, key=key_id):
                    st.session_state.risk_profile = rp_key
                    st.session_state.strategy_result = None
                    st.rerun()

        # Profile details card
        sp  = RISK_PROFILES[sel]
        sc  = PROFILE_META[sel]["color"]
        st.markdown(f"""<div style="background:#0d1117;border:1px solid {sc}44;border-radius:13px;padding:16px 22px;margin:14px 0 20px;">
          <div style="font-family:'DM Mono',monospace;font-size:10px;color:{sc};text-transform:uppercase;margin-bottom:10px;">Selected: {sp['label']} profile</div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:14px;">
            <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;margin-bottom:4px;text-transform:uppercase;">Time Horizon</div><div style="font-size:13px;color:#e2e8f0;font-weight:700;">{sp['time_horizon']}</div></div>
            <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;margin-bottom:4px;text-transform:uppercase;">Allocation</div><div style="font-size:13px;color:#e2e8f0;font-weight:700;">{sp['allocation']}</div></div>
            <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;margin-bottom:4px;text-transform:uppercase;">Stop Loss</div><div style="font-size:13px;color:#e2e8f0;font-weight:700;">{sp['stop_loss']}</div></div>
            <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;margin-bottom:4px;text-transform:uppercase;">Best Strategies</div><div style="font-size:13px;color:{sc};font-weight:700;">{' · '.join(sp['strategies'])}</div></div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div style='font-family:DM Mono,monospace;font-size:11px;color:#fbbf24;text-transform:uppercase;letter-spacing:2px;margin-bottom:12px;'>Step 2 — Configure & run</div>", unsafe_allow_html=True)

        rc1,rc2 = st.columns(2)
        with rc1:
            rp_asset  = st.selectbox("Asset Type", ["📈 Stock","🪙 Crypto"], key="rp_asset")
        with rc2:
            rp_period = st.selectbox("Backtest Period", ["3mo","6mo","1y","2y"], index=2, key="rp_period")

        sugg_html=f"<div style='margin:10px 0 14px;'><span style='font-family:DM Mono,monospace;font-size:11px;color:#64748b;'>Suggested for {sp['label']}: </span>"
        for asset in sp["assets"]:
            sugg_html+=f"<span style='background:#131920;border:1px solid {sc}33;border-radius:7px;padding:3px 9px;font-family:DM Mono,monospace;font-size:11px;color:{sc};margin-left:5px;'>{asset}</span>"
        sugg_html+="</div>"
        st.markdown(sugg_html, unsafe_allow_html=True)

        run_risk = st.button("🎯  Get My Personalized Strategy", key="btn_run_risk", use_container_width=True)

        if run_risk:
            if not query.strip():
                st.warning("⚠️ Enter a ticker in the search box above!")
            else:
                rp_ticker_clean = query.strip().upper()
                rp_asset_clean  = "crypto" if "Crypto" in rp_asset else "stock"
                strategy_to_test = sp["strategies"][0]
                with st.spinner(f"Building {sp['label']} strategy for {rp_ticker_clean}..."):
                    try:
                        res = run_strategy_analysis(rp_ticker_clean, strategy_to_test, rp_period, rp_asset_clean)
                        if "error" in res:
                            st.error(f"❌ {res['error']}")
                        else:
                            bt=res["backtest"]; cd=res["conditions"]
                            suggestion=suggest_strategies_by_risk(sel,rp_ticker_clean,{**bt,"strategy":strategy_to_test},cd,rp_asset_clean)
                            st.session_state.strategy_result={"type":"risk","bt":bt,"cd":cd,"suggestion":suggestion,"ticker":rp_ticker_clean,"profile_data":sp,"sc":sc}
                    except Exception as e:
                        st.error(f"❌ {e}")

        sr = st.session_state.strategy_result
        if sr and sr.get("type") == "risk":
            suggestion=sr["suggestion"]; bt=sr["bt"]; cd=sr["cd"]; sp2=sr["profile_data"]; sc2=sr["sc"]
            fit_color="#00d084" if suggestion.get("fit_emoji")=="🟢" else("#fb923c" if suggestion.get("fit_emoji")=="🟠" else("#ff4560" if suggestion.get("fit_emoji")=="🔴" else "#fbbf24"))

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""<div style="background:#0d1117;border:1px solid {fit_color}55;border-radius:14px;padding:22px 28px;margin-bottom:20px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
              <div><div style="font-family:'DM Mono',monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:5px;">🎯 {sp2['label']} Profile · {sr['ticker']}</div><div style="font-family:'Manrope',sans-serif;font-size:22px;font-weight:800;color:#e2e8f0;">{suggestion.get('overall_fit','')}</div></div>
              <div style="text-align:right;"><div style="font-family:'Manrope',sans-serif;font-size:38px;font-weight:900;color:{fit_color};">{suggestion.get('fit_emoji','')} {suggestion.get('fit_score',5)}/10</div><div style="font-family:'DM Mono',monospace;font-size:12px;color:#64748b;">Strategy-Profile Fit Score</div></div>
            </div>""", unsafe_allow_html=True)

            ps1,ps2 = st.columns(2)
            with ps1:
                st.markdown(f"""<div style="background:#131920;border:1.5px solid {sc2};border-radius:13px;padding:18px;margin-bottom:14px;">
                  <div style="font-family:'DM Mono',monospace;font-size:10px;color:{sc2};text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">⭐ Primary Strategy</div>
                  <div style="font-family:'Manrope',sans-serif;font-size:17px;font-weight:800;color:#e2e8f0;margin-bottom:8px;">{suggestion.get('primary_strategy','')}</div>
                  <div style="font-size:13px;color:#94a3b8;line-height:1.7;">{suggestion.get('primary_reason','')}</div>
                </div>""", unsafe_allow_html=True)
            with ps2:
                st.markdown(f"""<div style="background:#131920;border:1px solid #253347;border-radius:13px;padding:18px;margin-bottom:14px;">
                  <div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">🔄 Backup Strategy</div>
                  <div style="font-family:'Manrope',sans-serif;font-size:17px;font-weight:800;color:#e2e8f0;margin-bottom:8px;">{suggestion.get('secondary_strategy','')}</div>
                  <div style="font-size:13px;color:#94a3b8;line-height:1.7;">{suggestion.get('secondary_reason','')}</div>
                </div>""", unsafe_allow_html=True)

            a1,a2,a3,a4 = st.columns(4)
            for col,lbl,val,color in [(a1,"📥 Entry",suggestion.get("entry_advice",""),"#00d084"),(a2,"📤 Exit",suggestion.get("exit_advice",""),"#38bdf8"),(a3,"💼 Position Size",suggestion.get("position_size",""),sc2),(a4,"⚠️ Key Warning",suggestion.get("key_warning",""),"#ff4560")]:
                with col:
                    st.markdown(f"""<div style="background:#131920;border:1px solid #253347;border-radius:11px;padding:14px;margin-bottom:14px;">
                      <div style="font-family:'DM Mono',monospace;font-size:10px;color:{color};text-transform:uppercase;letter-spacing:1px;margin-bottom:7px;">{lbl}</div>
                      <div style="font-size:12px;color:#e2e8f0;line-height:1.6;">{val}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown(f"""<div style="background:rgba(167,139,250,0.05);border:1px solid rgba(167,139,250,0.2);border-radius:11px;padding:16px 20px;margin-bottom:16px;display:flex;gap:12px;align-items:flex-start;">
              <div style="font-size:20px;flex-shrink:0;">💡</div>
              <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#a78bfa;text-transform:uppercase;margin-bottom:5px;">Personalized Tip — {sp2['label']}</div>
              <div style="font-size:13px;color:#e2e8f0;line-height:1.7;">{suggestion.get('personalized_tip','')}</div></div>
            </div>""", unsafe_allow_html=True)

            strategy_tested = sp2["strategies"][0]
            st.markdown(f"""<div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:13px;padding:18px 22px;">
              <div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:12px;">📊 backtest summary — {strategy_tested}</div>
              <div style="display:flex;gap:20px;flex-wrap:wrap;">
                <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;margin-bottom:3px;">Return</div><div style="font-size:18px;font-weight:800;color:{'#00d084' if bt['total_return']>=0 else '#ff4560'};">{'+'if bt['total_return']>=0 else ''}{bt['total_return']:.1f}%</div></div>
                <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;margin-bottom:3px;">Buy &amp; Hold</div><div style="font-size:18px;font-weight:800;color:{'#00d084' if bt['bh_return']>=0 else '#ff4560'};">{'+'if bt['bh_return']>=0 else ''}{bt['bh_return']:.1f}%</div></div>
                <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;margin-bottom:3px;">Win Rate</div><div style="font-size:18px;font-weight:800;color:#38bdf8;">{bt['win_rate']:.0f}%</div></div>
                <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;margin-bottom:3px;">Max Drawdown</div><div style="font-size:18px;font-weight:800;color:#ff4560;">-{bt['max_drawdown']:.1f}%</div></div>
                <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;margin-bottom:3px;">Signal</div><div style="font-size:16px;font-weight:800;color:{'#00d084' if 'BUY' in cd.get('signal','') else '#ff4560' if 'SELL' in cd.get('signal','') else '#fbbf24'};">{cd.get('signal','NEUTRAL')}</div></div>
              </div>
            </div>""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center;padding:24px 0 16px;margin-top:20px;border-top:1px solid #1e2d3d;">
  <div style="font-family:'DM Mono',monospace;font-size:12px;color:#64748b;">Built by <strong style="color:#e2e8f0;">Paddy</strong> · DataPulse AI · 5 Agents · Strategy Engine · Risk Profiles · Llama 3.3 70B · 100% Free</div>
  <div style="font-family:'DM Mono',monospace;font-size:11px;color:#334155;margin-top:5px;">⚠️ Educational purposes only · Not financial advice</div>
</div>
""", unsafe_allow_html=True)