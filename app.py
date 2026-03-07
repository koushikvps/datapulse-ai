# app.py — DataPulse AI · Clean UI
# KEY INSIGHT: The ONLY reliable Streamlit button styling is:
# wrap button in <div class="cls">, inject <style>.cls button{...}</style>
# This works because the class is on the markdown div ABOVE the stButton div,
# and CSS child selectors still target the button inside.

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
html,body,[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stVerticalBlock"]{
    background:#07090f!important;color:#e2e8f0!important;font-family:'Manrope',sans-serif!important;
}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stSidebar"]{display:none!important;}
.block-container{padding:0!important;max-width:100%!important;}
*{box-sizing:border-box;}

/* ── Solid visible base for ALL buttons — never transparent ── */
[data-testid="stButton"]>button{
    background:#131920!important;color:#94a3b8!important;
    border:1.5px solid #253347!important;border-radius:10px!important;
    font-family:'Manrope',sans-serif!important;font-weight:600!important;
    font-size:14px!important;padding:11px 18px!important;
    width:100%!important;transition:all 0.15s!important;
}
[data-testid="stButton"]>button:hover{
    border-color:#38bdf8!important;color:#38bdf8!important;background:#0d1117!important;
}

/* Inputs */
[data-testid="stTextInput"] input{background:#0d1117!important;border:1.5px solid #253347!important;border-radius:10px!important;color:#e2e8f0!important;font-family:'DM Mono',monospace!important;font-size:15px!important;padding:13px 16px!important;}
[data-testid="stTextInput"] input:focus{border-color:#00d084!important;box-shadow:0 0 0 3px rgba(0,208,132,0.15)!important;outline:none!important;}
[data-testid="stTextInput"] input::placeholder{color:#334155!important;}
[data-testid="stTextInput"] label{display:none!important;}
[data-testid="stSelectbox"]>div>div{background:#0d1117!important;border:1.5px solid #253347!important;border-radius:10px!important;color:#e2e8f0!important;font-family:'DM Mono',monospace!important;}
[data-testid="stSelectbox"] label{color:#64748b!important;font-family:'DM Mono',monospace!important;font-size:11px!important;text-transform:uppercase!important;letter-spacing:1px!important;}
[data-testid="stSpinner"] p{color:#00d084!important;font-family:'DM Mono',monospace!important;}
::-webkit-scrollbar{width:4px;} ::-webkit-scrollbar-thumb{background:#253347;border-radius:2px;}

/* ── Named class styles — injected via mk_btn helper ── */
.dp-stock-on [data-testid="stButton"]>button{background:#00d084!important;color:#07090f!important;border-color:#00d084!important;font-weight:800!important;}
.dp-crypto-on [data-testid="stButton"]>button{background:#fbbf24!important;color:#07090f!important;border-color:#fbbf24!important;font-weight:800!important;}
.dp-stock-off [data-testid="stButton"]>button:hover{border-color:#00d084!important;color:#00d084!important;}
.dp-crypto-off [data-testid="stButton"]>button:hover{border-color:#fbbf24!important;color:#fbbf24!important;}

.dp-act-analyze-on [data-testid="stButton"]>button{background:rgba(0,208,132,0.08)!important;color:#00d084!important;border:2px solid #00d084!important;font-weight:800!important;font-size:14px!important;padding:18px 22px!important;border-radius:12px!important;white-space:normal!important;height:auto!important;text-align:left!important;line-height:1.5!important;}
.dp-act-analyze-off [data-testid="stButton"]>button{background:#0d1117!important;color:#94a3b8!important;border:2px solid #1e2d3d!important;font-size:14px!important;padding:18px 22px!important;border-radius:12px!important;white-space:normal!important;height:auto!important;text-align:left!important;line-height:1.5!important;}
.dp-act-analyze-off [data-testid="stButton"]>button:hover{border-color:#00d084!important;color:#00d084!important;background:rgba(0,208,132,0.04)!important;}

.dp-act-strategy-on [data-testid="stButton"]>button{background:rgba(167,139,250,0.08)!important;color:#a78bfa!important;border:2px solid #a78bfa!important;font-weight:800!important;font-size:14px!important;padding:18px 22px!important;border-radius:12px!important;white-space:normal!important;height:auto!important;text-align:left!important;line-height:1.5!important;}
.dp-act-strategy-off [data-testid="stButton"]>button{background:#0d1117!important;color:#94a3b8!important;border:2px solid #1e2d3d!important;font-size:14px!important;padding:18px 22px!important;border-radius:12px!important;white-space:normal!important;height:auto!important;text-align:left!important;line-height:1.5!important;}
.dp-act-strategy-off [data-testid="stButton"]>button:hover{border-color:#a78bfa!important;color:#a78bfa!important;background:rgba(167,139,250,0.04)!important;}

.dp-mode-bt-on [data-testid="stButton"]>button{background:rgba(167,139,250,0.1)!important;color:#a78bfa!important;border:2px solid #a78bfa!important;font-weight:800!important;padding:13px 20px!important;border-radius:10px!important;}
.dp-mode-bt-off [data-testid="stButton"]>button{background:#0d1117!important;color:#64748b!important;border:2px solid #1e2d3d!important;padding:13px 20px!important;border-radius:10px!important;}
.dp-mode-bt-off [data-testid="stButton"]>button:hover{border-color:#a78bfa!important;color:#a78bfa!important;}

.dp-mode-rp-on [data-testid="stButton"]>button{background:rgba(251,191,36,0.1)!important;color:#fbbf24!important;border:2px solid #fbbf24!important;font-weight:800!important;padding:13px 20px!important;border-radius:10px!important;}
.dp-mode-rp-off [data-testid="stButton"]>button{background:#0d1117!important;color:#64748b!important;border:2px solid #1e2d3d!important;padding:13px 20px!important;border-radius:10px!important;}
.dp-mode-rp-off [data-testid="stButton"]>button:hover{border-color:#fbbf24!important;color:#fbbf24!important;}

.dp-rp-red-on [data-testid="stButton"]>button{background:rgba(255,69,96,0.1)!important;color:#ff4560!important;border:2px solid #ff4560!important;font-weight:800!important;border-radius:12px!important;padding:16px 10px!important;white-space:normal!important;height:auto!important;line-height:1.6!important;}
.dp-rp-red-off [data-testid="stButton"]>button{background:#0d1117!important;color:#94a3b8!important;border:2px solid #1e2d3d!important;border-radius:12px!important;padding:16px 10px!important;white-space:normal!important;height:auto!important;line-height:1.6!important;}
.dp-rp-red-off [data-testid="stButton"]>button:hover{border-color:#ff4560!important;color:#ff4560!important;}

.dp-rp-oran-on [data-testid="stButton"]>button{background:rgba(251,146,60,0.1)!important;color:#fb923c!important;border:2px solid #fb923c!important;font-weight:800!important;border-radius:12px!important;padding:16px 10px!important;white-space:normal!important;height:auto!important;line-height:1.6!important;}
.dp-rp-oran-off [data-testid="stButton"]>button{background:#0d1117!important;color:#94a3b8!important;border:2px solid #1e2d3d!important;border-radius:12px!important;padding:16px 10px!important;white-space:normal!important;height:auto!important;line-height:1.6!important;}
.dp-rp-oran-off [data-testid="stButton"]>button:hover{border-color:#fb923c!important;color:#fb923c!important;}

.dp-rp-blue-on [data-testid="stButton"]>button{background:rgba(56,189,248,0.1)!important;color:#38bdf8!important;border:2px solid #38bdf8!important;font-weight:800!important;border-radius:12px!important;padding:16px 10px!important;white-space:normal!important;height:auto!important;line-height:1.6!important;}
.dp-rp-blue-off [data-testid="stButton"]>button{background:#0d1117!important;color:#94a3b8!important;border:2px solid #1e2d3d!important;border-radius:12px!important;padding:16px 10px!important;white-space:normal!important;height:auto!important;line-height:1.6!important;}
.dp-rp-blue-off [data-testid="stButton"]>button:hover{border-color:#38bdf8!important;color:#38bdf8!important;}

.dp-rp-grn-on [data-testid="stButton"]>button{background:rgba(0,208,132,0.1)!important;color:#00d084!important;border:2px solid #00d084!important;font-weight:800!important;border-radius:12px!important;padding:16px 10px!important;white-space:normal!important;height:auto!important;line-height:1.6!important;}
.dp-rp-grn-off [data-testid="stButton"]>button{background:#0d1117!important;color:#94a3b8!important;border:2px solid #1e2d3d!important;border-radius:12px!important;padding:16px 10px!important;white-space:normal!important;height:auto!important;line-height:1.6!important;}
.dp-rp-grn-off [data-testid="stButton"]>button:hover{border-color:#00d084!important;color:#00d084!important;}

.dp-cta-green [data-testid="stButton"]>button{background:#00d084!important;color:#07090f!important;border:none!important;font-weight:800!important;font-size:15px!important;padding:14px!important;border-radius:10px!important;}
.dp-cta-green [data-testid="stButton"]>button:hover{background:#00f097!important;box-shadow:0 0 20px rgba(0,208,132,0.35)!important;}
.dp-cta-purple [data-testid="stButton"]>button{background:#a78bfa!important;color:#07090f!important;border:none!important;font-weight:800!important;font-size:15px!important;padding:14px!important;border-radius:10px!important;}
.dp-cta-purple [data-testid="stButton"]>button:hover{background:#c4b5fd!important;box-shadow:0 0 20px rgba(167,139,250,0.35)!important;}
.dp-cta-gold [data-testid="stButton"]>button{background:#fbbf24!important;color:#07090f!important;border:none!important;font-weight:800!important;font-size:15px!important;padding:14px!important;border-radius:10px!important;}
.dp-cta-gold [data-testid="stButton"]>button:hover{background:#fcd34d!important;box-shadow:0 0 20px rgba(251,191,36,0.3)!important;}
</style>
""", unsafe_allow_html=True)


def mk_btn(label: str, cls: str, key: str) -> bool:
    st.markdown(f'<div class="{cls}">', unsafe_allow_html=True)
    r = st.button(label, key=key, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    return r


# Session state
for k, v in {"asset_type":"stock","action":None,"strategy_mode":"backtest",
              "risk_profile":"🟠 Moderate","result":None,"strategy_result":None}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── NAVBAR ──
st.markdown("""
<div style="background:#0d1117;border-bottom:1px solid #1e2d3d;padding:0 48px;height:56px;
            display:flex;align-items:center;justify-content:space-between;">
  <div style="display:flex;align-items:center;gap:12px;">
    <div style="width:32px;height:32px;background:linear-gradient(135deg,#00d084,#38bdf8);
                border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;">📡</div>
    <span style="font-family:'Manrope',sans-serif;font-weight:800;font-size:20px;letter-spacing:-0.5px;color:#e2e8f0;">
      Data<span style="color:#00d084;">Pulse</span>
      <span style="font-size:12px;color:#64748b;font-weight:400;margin-left:8px;">AI</span>
    </span>
  </div>
  <div style="display:flex;align-items:center;gap:7px;">
    <div style="width:6px;height:6px;border-radius:50%;background:#00d084;box-shadow:0 0 7px #00d084;"></div>
    <span style="font-family:'DM Mono',monospace;font-size:11px;color:#64748b;">5 agents · Llama 3.3 70B · LangGraph</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='padding:44px 56px 0;'>", unsafe_allow_html=True)

# ── HERO ──
st.markdown("""
<div style="text-align:center;margin-bottom:32px;">
  <div style="font-family:'Manrope',sans-serif;font-size:46px;font-weight:800;color:#e2e8f0;
              letter-spacing:-1.5px;line-height:1.1;margin-bottom:10px;">
    AI intelligence on<br><span style="color:#00d084;">stocks &amp; crypto.</span>
  </div>
  <div style="font-size:15px;color:#64748b;">Enter any ticker · Choose what you want · Results in seconds.</div>
</div>
""", unsafe_allow_html=True)

# ── ASSET TOGGLE ──
at = st.session_state.asset_type
_, t1, t2, _ = st.columns([3, 1, 1, 3])
with t1:
    if mk_btn("📈  Stock", "dp-stock-on" if at=="stock" else "dp-stock-off", "tog_s"):
        if at != "stock": st.session_state.asset_type="stock"; st.rerun()
with t2:
    if mk_btn("🪙  Crypto", "dp-crypto-on" if at=="crypto" else "dp-crypto-off", "tog_c"):
        if at != "crypto": st.session_state.asset_type="crypto"; st.rerun()

asset_type = st.session_state.asset_type
ph_text = "AAPL · Tesla · NVIDIA · Microsoft..." if asset_type=="stock" else "BTC · ETH · SOL · DOGE · XRP..."

st.markdown("<div style='height:18px;'></div>", unsafe_allow_html=True)
_, sc, _ = st.columns([1, 4, 1])
with sc:
    query = st.text_input("q", placeholder=ph_text, key="main_query", label_visibility="collapsed")

picks = ["AAPL","TSLA","NVDA","MSFT","GOOGL","AMZN","META"] if asset_type=="stock" else ["BTC","ETH","SOL","DOGE","XRP","ADA","AVAX"]
st.markdown(
    "<div style='display:flex;justify-content:center;gap:7px;margin:10px 0 30px;flex-wrap:wrap;'>" +
    "".join(f"<span style='background:#131920;border:1px solid #253347;border-radius:7px;padding:4px 11px;font-family:DM Mono,monospace;font-size:12px;color:#64748b;'>{t}</span>" for t in picks) +
    "</div>", unsafe_allow_html=True)

# ── ACTION CARDS ──
st.markdown("<div style='font-family:DM Mono,monospace;font-size:11px;color:#a78bfa;text-transform:uppercase;letter-spacing:2px;margin-bottom:16px;'>▸ What would you like to do?</div>", unsafe_allow_html=True)

act = st.session_state.action
ac1, ac2 = st.columns(2)
with ac1:
    lbl_a = "✦  Analyze Asset  ·  Active\n5 agents · Price · News · Sentiment · Risk · AI Report" if act=="analyze" else "📡  Analyze Asset\n5 agents · Price · News · Sentiment · Risk · AI Report"
    if mk_btn(lbl_a, "dp-act-analyze-on" if act=="analyze" else "dp-act-analyze-off", "act_analyze"):
        st.session_state.action="analyze"; st.session_state.result=None; st.rerun()
with ac2:
    lbl_s = "✦  Strategy & Backtest  ·  Active\nBacktest strategies · Risk Profile Advisor · AI picks" if act=="strategy" else "⚡  Strategy & Backtest\nBacktest strategies · Risk Profile Advisor · AI picks"
    if mk_btn(lbl_s, "dp-act-strategy-on" if act=="strategy" else "dp-act-strategy-off", "act_strategy"):
        st.session_state.action="strategy"; st.session_state.strategy_result=None; st.rerun()

st.markdown("<hr style='border-color:#1e2d3d;margin:28px 0;'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# ANALYZE FLOW
# ════════════════════════════════════════════════════════════
if st.session_state.action == "analyze":
    st.markdown("<div style='font-family:DM Mono,monospace;font-size:11px;color:#00d084;text-transform:uppercase;letter-spacing:2px;margin-bottom:20px;'>▸ Analyze — real-time AI report</div>", unsafe_allow_html=True)
    _, btn_col, _ = st.columns([2, 2, 2])
    with btn_col:
        run_analyze = mk_btn("🚀  Run AI Analysis", "dp-cta-green", "btn_analyze")

    if run_analyze:
        if not query.strip():
            st.warning("⚠️ Enter a ticker above first!")
        else:
            prog = st.empty()
            def show_prog(done, active):
                agents = [("🔎","Resolver"),("📈","Stock"),("📰","News"),("💬","Sentiment"),("⚠️","Risk"),("🧠","Analyst")]
                h = "<div style='display:flex;gap:8px;flex-wrap:wrap;margin:14px 0;'>"
                for icon, name in agents:
                    if name in done:   s="background:rgba(0,208,132,0.12);border:1px solid #00d084;color:#00d084;"; p="✓ "
                    elif name==active: s="background:rgba(56,189,248,0.12);border:1px solid #38bdf8;color:#38bdf8;"; p="⟳ "
                    else:              s="background:#131920;border:1px solid #1e2d3d;color:#334155;"; p="○ "
                    h += f"<div style='{s}border-radius:20px;padding:5px 14px;font-family:DM Mono,monospace;font-size:12px;'>{icon} {p}{name}</div>"
                return h + "</div>"
            prog.markdown(show_prog([],"Resolver"), unsafe_allow_html=True)
            with st.spinner(f"Analyzing {query.strip()}..."):
                try:
                    result = run_datapulse(query.strip(), asset_type=asset_type)
                    prog.markdown(show_prog(["Resolver","Stock","News","Sentiment","Risk","Analyst"],""), unsafe_allow_html=True)
                    st.session_state.result = result
                except Exception as e:
                    st.error(f"❌ {e}")

    result = st.session_state.result
    if result:
        stock=result.get("stock_data",{}); news=result.get("news_articles",[])
        news_s=result.get("news_sentiment",{}); social=result.get("social_sentiment",{})
        risk=result.get("risk",{}); analysis=result.get("analysis",{})
        company=result.get("company_name",query); ticker=result.get("ticker","")
        price=stock.get("current_price",0); chg=stock.get("change",0); chg_pct=stock.get("change_pct",0)
        mktcap=format_market_cap(stock.get("market_cap",0))
        rec=analysis.get("recommendation","HOLD"); rec_emoji=analysis.get("rec_emoji","🟡")
        target=analysis.get("price_target",price); upside=analysis.get("upside_pct",0)
        risk_score=risk.get("overall_score",5); risk_label=risk.get("overall_label","Medium"); risk_emoji=risk.get("overall_emoji","🟡")
        bull_pct=social.get("bull_pct",50); bear_pct=social.get("bear_pct",50)
        chg_color="#00d084" if chg>=0 else "#ff4560"; chg_sign="+" if chg>=0 else ""
        a_color="#fbbf24" if asset_type=="crypto" else "#00d084"
        price_fmt=f"{price:,.4f}" if asset_type=="crypto" and price<1 else f"{price:,.2f}"

        st.markdown(f"""<div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:16px;padding:22px 28px;margin-bottom:20px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
          <div>
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px;">
              <div style="font-family:'Manrope',sans-serif;font-size:26px;font-weight:800;color:#e2e8f0;">{company}</div>
              <span style="border:1px solid {a_color}44;border-radius:8px;padding:2px 9px;font-family:'DM Mono',monospace;font-size:11px;color:{a_color};">{'🪙 Crypto' if asset_type=='crypto' else '📈 Stock'}</span>
            </div>
            <div style="font-family:'DM Mono',monospace;font-size:12px;color:#64748b;">{ticker} · {stock.get('sector','—')} · {stock.get('industry','—')}</div>
          </div>
          <div style="display:flex;align-items:baseline;gap:10px;">
            <div style="font-family:'Manrope',sans-serif;font-size:38px;font-weight:800;color:#e2e8f0;letter-spacing:-1px;">${price_fmt}</div>
            <div style="font-family:'DM Mono',monospace;font-size:15px;color:{chg_color};">{chg_sign}{chg:.2f} ({chg_sign}{chg_pct:.2f}%)</div>
          </div>
        </div>""", unsafe_allow_html=True)

        mc1,mc2,mc3,mc4=st.columns(4)
        rec_bg="rgba(0,208,132,0.07)" if rec=="BUY" else("rgba(255,69,96,0.07)" if rec=="SELL" else "rgba(251,191,36,0.07)")
        rec_bd="#00d084" if rec=="BUY" else("#ff4560" if rec=="SELL" else "#fbbf24")
        for col,icon,lbl,val,sub,bg,bd in [(mc1,"📈","Recommendation",f"{rec_emoji} {rec}",f"Target ${target:,.2f} ({chg_sign}{upside:.1f}%)",rec_bg,rec_bd),(mc2,"⚠️","Risk Level",f"{risk_emoji} {risk_score}/10",risk_label,"#131920","#253347"),(mc3,"💬","Social Mood",f"{'🟢' if bull_pct>55 else '🔴' if bull_pct<45 else '🟡'} {bull_pct}% Bulls",f"{bear_pct}% Bears","#131920","#253347"),(mc4,"🏢","Market Cap",mktcap,f"Vol: {stock.get('volume',0):,.0f}","#131920","#253347")]:
            with col:
                st.markdown(f"""<div style="background:{bg};border:1px solid {bd};border-radius:13px;padding:18px 20px;height:108px;margin-bottom:20px;">
                  <div style="font-size:10px;font-family:'DM Mono',monospace;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:7px;">{icon} {lbl}</div>
                  <div style="font-family:'Manrope',sans-serif;font-size:21px;font-weight:800;color:#e2e8f0;line-height:1;">{val}</div>
                  <div style="font-size:11px;color:#64748b;margin-top:5px;font-family:'DM Mono',monospace;">{sub}</div>
                </div>""", unsafe_allow_html=True)

        p1,p2=st.columns([3,2])
        with p1:
            st.markdown("<div style='font-family:DM Mono,monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;'>📈 30-day price</div>", unsafe_allow_html=True)
            ph=stock.get("price_history",[])
            if ph:
                lc="#00d084" if ph[-1]>=ph[0] else "#ff4560"
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
        with p2:
            st.markdown(f"<div style='font-family:DM Mono,monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;'>📰 news · {news_s.get('emoji','🟡')} {news_s.get('overall','Neutral')} {news_s.get('score',5)}/10</div>", unsafe_allow_html=True)
            for a in news[:6]:
                sc_="#00d084" if a.get("sentiment")=="positive" else("#ff4560" if a.get("sentiment")=="negative" else "#fbbf24")
                st.markdown(f"""<a href="{a.get('url','#')}" target="_blank" style="text-decoration:none;"><div style="background:#131920;border:1px solid #1e2d3d;border-left:3px solid {sc_};border-radius:0 9px 9px 0;padding:9px 13px;margin-bottom:6px;"><div style="font-size:12px;color:#e2e8f0;font-weight:500;line-height:1.4;margin-bottom:2px;">{a.get('emoji','🟡')} {a.get('title','')[:68]}</div><div style="display:flex;justify-content:space-between;"><span style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;">{a.get('source','')}</span><span style="font-family:'DM Mono',monospace;font-size:10px;color:{sc_};">{a.get('score',5)}/10</span></div></div></a>""", unsafe_allow_html=True)

        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        r1,r2=st.columns([3,2])
        with r1:
            st.markdown(f"<div style='font-family:DM Mono,monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;'>⚠️ risk · {risk_emoji} {risk_label}</div>", unsafe_allow_html=True)
            dims=risk.get("dimensions",[])
            if dims:
                fig2=pgo.Figure(); fig2.add_trace(pgo.Bar(x=[d["score"] for d in dims],y=[d["name"] for d in dims],orientation="h",marker=dict(color=["#ff4560" if d["score"]>=7 else "#fbbf24" if d["score"]>=5 else "#00d084" for d in dims],opacity=0.85),text=[f"{d['score']}/10" for d in dims],textposition="outside",textfont=dict(color="#94a3b8",size=11,family="DM Mono"),hovertemplate="%{y}: %{x}/10<extra></extra>"))
                fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=190,margin=dict(l=0,r=40,t=0,b=0),xaxis=dict(range=[0,13],showgrid=False,showticklabels=False,zeroline=False),yaxis=dict(tickfont=dict(color="#94a3b8",size=11,family="DM Mono"),zeroline=False),showlegend=False,bargap=0.35)
                st.plotly_chart(fig2,use_container_width=True,config={"displayModeBar":False})
            for ri in risk.get("key_risks",[]): st.markdown(f"<div style='background:rgba(255,69,96,0.07);border:1px solid rgba(255,69,96,0.18);border-radius:8px;padding:7px 13px;margin-bottom:5px;font-size:13px;color:#e2e8f0;'>⚡ {ri}</div>", unsafe_allow_html=True)
        with r2:
            st.markdown("<div style='font-family:DM Mono,monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;'>💬 social sentiment</div>", unsafe_allow_html=True)
            fig3=pgo.Figure(pgo.Pie(values=[bull_pct,bear_pct],labels=["Bulls 🟢","Bears 🔴"],hole=0.68,marker=dict(colors=["#00d084","#ff4560"]),textinfo="none",hovertemplate="%{label}: %{value}%<extra></extra>"))
            fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)",height=170,margin=dict(l=0,r=0,t=0,b=0),showlegend=True,legend=dict(font=dict(color="#94a3b8",size=11,family="DM Mono"),bgcolor="rgba(0,0,0,0)"),annotations=[dict(text=f"<b>{bull_pct}%</b><br>Bulls",x=0.5,y=0.5,font=dict(size=15,color="#e2e8f0",family="Manrope"),showarrow=False)])
            st.plotly_chart(fig3,use_container_width=True,config={"displayModeBar":False})
            buzz=social.get("buzz_score",5); themes=social.get("key_themes",[])
            th="".join(f"<span style='background:rgba(56,189,248,0.1);border:1px solid rgba(56,189,248,0.2);border-radius:14px;padding:3px 10px;font-size:11px;color:#38bdf8;font-family:DM Mono,monospace;'>{t}</span>" for t in themes) if themes else ""
            st.markdown(f"""<div style="background:#131920;border:1px solid #1e2d3d;border-radius:10px;padding:13px 16px;">
              <div style="display:flex;justify-content:space-between;margin-bottom:7px;"><span style="font-family:'DM Mono',monospace;font-size:11px;color:#64748b;">Buzz Score</span><span style="font-family:'DM Mono',monospace;font-size:11px;color:#00d084;font-weight:700;">{buzz}/10</span></div>
              <div style="background:#1e2d3d;border-radius:4px;height:4px;margin-bottom:10px;"><div style="background:#00d084;border-radius:4px;height:4px;width:{buzz*10}%;"></div></div>
              <div style="font-size:12px;color:#94a3b8;line-height:1.6;margin-bottom:8px;">{social.get('summary','')}</div>
              <div style="display:flex;flex-wrap:wrap;gap:5px;">{th}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        rec_bg2="rgba(0,208,132,0.05)" if rec=="BUY" else("rgba(255,69,96,0.05)" if rec=="SELL" else "rgba(251,191,36,0.05)")
        rec_bd2="rgba(0,208,132,0.28)" if rec=="BUY" else("rgba(255,69,96,0.28)" if rec=="SELL" else "rgba(251,191,36,0.28)")
        rec_col="#00d084" if rec=="BUY" else("#ff4560" if rec=="SELL" else "#fbbf24")
        st.markdown(f"""<div style="background:{rec_bg2};border:1px solid {rec_bd2};border-radius:16px;padding:26px 30px;margin-bottom:18px;">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;flex-wrap:wrap;gap:12px;">
            <div><div style="font-family:'DM Mono',monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:5px;">🧠 AI analyst report</div><div style="font-family:'Manrope',sans-serif;font-size:20px;font-weight:800;color:#e2e8f0;">{analysis.get('verdict_headline','')}</div></div>
            <div style="text-align:right;"><div style="font-family:'Manrope',sans-serif;font-size:32px;font-weight:900;color:{rec_col};">{rec_emoji} {rec}</div><div style="font-family:'DM Mono',monospace;font-size:12px;color:#64748b;">Target ${target:,.2f} · {analysis.get('time_horizon','12mo')}</div></div>
          </div>
          <div style="font-size:14px;color:#e2e8f0;line-height:1.8;border-left:3px solid {rec_col};padding-left:14px;">{analysis.get('thesis','')}</div>
        </div>""", unsafe_allow_html=True)
        ab,as_,ac_=st.columns(3)
        with ab: st.markdown(f"<div style='background:rgba(0,208,132,0.05);border:1px solid rgba(0,208,132,0.2);border-radius:13px;padding:18px;'><div style='font-family:DM Mono,monospace;font-size:10px;color:#00d084;text-transform:uppercase;margin-bottom:8px;'>📈 Bull Case</div><div style='font-size:13px;color:#e2e8f0;line-height:1.7;'>{analysis.get('bull_case','')}</div></div>", unsafe_allow_html=True)
        with as_: st.markdown(f"<div style='background:rgba(255,69,96,0.05);border:1px solid rgba(255,69,96,0.2);border-radius:13px;padding:18px;'><div style='font-family:DM Mono,monospace;font-size:10px;color:#ff4560;text-transform:uppercase;margin-bottom:8px;'>📉 Bear Case</div><div style='font-size:13px;color:#e2e8f0;line-height:1.7;'>{analysis.get('bear_case','')}</div></div>", unsafe_allow_html=True)
        with ac_:
            ch="<div style='background:#131920;border:1px solid #253347;border-radius:13px;padding:18px;'><div style='font-family:DM Mono,monospace;font-size:10px;color:#38bdf8;text-transform:uppercase;margin-bottom:8px;'>⚡ Catalysts</div>"
            for cat in analysis.get("catalysts",[]): ch+=f"<div style='font-size:12px;color:#e2e8f0;padding:5px 0;border-bottom:1px solid #1e2d3d;line-height:1.5;'>→ {cat}</div>"
            st.markdown(ch+"</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        st.markdown(f"""<div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:13px;padding:22px 26px;">
          <div style="font-family:'DM Mono',monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;">📊 detailed analysis</div>
          <div style="font-size:14px;color:#94a3b8;line-height:1.9;">{analysis.get('detailed_analysis','')}</div>
        </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# STRATEGY FLOW
# ════════════════════════════════════════════════════════════
elif st.session_state.action == "strategy":
    st.markdown("<div style='font-family:DM Mono,monospace;font-size:11px;color:#a78bfa;text-transform:uppercase;letter-spacing:2px;margin-bottom:20px;'>▸ Strategy engine — backtest &amp; risk profile</div>", unsafe_allow_html=True)

    mode=st.session_state.strategy_mode
    m1,m2,_=st.columns([2,2,2])
    with m1:
        if mk_btn("📊  Backtest a Strategy","dp-mode-bt-on" if mode=="backtest" else "dp-mode-bt-off","sel_bt"):
            st.session_state.strategy_mode="backtest"; st.session_state.strategy_result=None; st.rerun()
    with m2:
        if mk_btn("🎯  Risk Profile Advisor","dp-mode-rp-on" if mode=="risk" else "dp-mode-rp-off","sel_rp"):
            st.session_state.strategy_mode="risk"; st.session_state.strategy_result=None; st.rerun()
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    if mode=="backtest":
        st.markdown("<div style='background:#0d1117;border:1px solid #253347;border-radius:14px;padding:24px 28px;margin-bottom:16px;'>", unsafe_allow_html=True)
        b1,b2,b3=st.columns(3)
        with b1: s_asset=st.selectbox("Asset Type",["📈 Stock","🪙 Crypto"],key="bt_asset")
        with b2: s_strategy=st.selectbox("Strategy",list(STRATEGIES.keys()),key="bt_strategy")
        with b3: s_period=st.selectbox("Time Period",["3mo","6mo","1y","2y"],index=2,key="bt_period")
        st.markdown("</div>", unsafe_allow_html=True)

        SINFO={"RSI Oversold/Overbought":("📉","Buy RSI<30 · Sell RSI>70 · Mean-reversion","Sideways markets","#38bdf8"),"Moving Average Crossover":("📊","Buy Golden Cross · Sell Death Cross","Trending markets","#00d084"),"Momentum / Trend Following":("🚀","Buy momentum >+5% · Sell <-5%","Bull & bear runs","#a78bfa"),"Value Investing":("💎","Buy 20% below 200MA · Sell 20% above","Long-term investors","#fbbf24"),"Buy the Dip":("🎯","Buy 5% drop in 3d + RSI<40","Volatile assets & crypto","#ff4560")}
        si=SINFO.get(s_strategy,("📊","","","#00d084"))
        st.markdown(f"""<div style="background:#131920;border:1px solid {si[3]}33;border-radius:11px;padding:14px 20px;margin-bottom:20px;display:flex;align-items:center;gap:14px;">
          <div style="font-size:28px;flex-shrink:0;">{si[0]}</div>
          <div><div style="font-weight:700;font-size:15px;color:#e2e8f0;margin-bottom:4px;">{s_strategy}</div>
          <div style="font-size:12px;color:#64748b;">{si[1]}<span style="color:{si[3]};margin-left:8px;">· Best for: {si[2]}</span></div></div>
        </div>""", unsafe_allow_html=True)

        _,btn_col,_=st.columns([2,2,2])
        with btn_col: run_bt=mk_btn("⚡  Run Backtest","dp-cta-purple","btn_run_bt")

        if run_bt:
            if not query.strip(): st.warning("⚠️ Enter a ticker above!")
            else:
                tc=query.strip().upper(); ac2="crypto" if "Crypto" in s_asset else "stock"
                with st.spinner(f"Running {s_strategy} on {tc}..."):
                    try:
                        res=run_strategy_analysis(tc,s_strategy,s_period,ac2)
                        if "error" in res: st.error(f"❌ {res['error']}")
                        else:
                            bt=res["backtest"]; cd=res["conditions"]
                            verdict=generate_strategy_verdict(tc,s_strategy,bt,cd,ac2)
                            st.session_state.strategy_result={"type":"backtest","bt":bt,"cd":cd,"verdict":verdict,"ticker":tc,"strategy":s_strategy,"period":s_period}
                    except Exception as e: st.error(f"❌ {e}")

        sr=st.session_state.strategy_result
        if sr and sr.get("type")=="backtest":
            bt=sr["bt"]; cd=sr["cd"]; verdict=sr["verdict"]
            tr=bt["total_return"]; bhr=bt["bh_return"]; op=bt["outperformed"]
            wr=bt["win_rate"]; mdd=bt["max_drawdown"]; nt=bt["total_trades"]; fv=bt["final_value"]
            vc="#00d084" if verdict.get("verdict_emoji")=="🟢" else("#ff4560" if verdict.get("verdict_emoji")=="🔴" else "#fbbf24")
            rc="#00d084" if tr>=0 else "#ff4560"; bc="#00d084" if bhr>=0 else "#ff4560"
            rs="+" if tr>=0 else ""; bs="+" if bhr>=0 else ""
            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
            st.markdown(f"""<div style="background:#0d1117;border:1px solid {vc};border-radius:14px;padding:22px 28px;margin-bottom:20px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
              <div><div style="font-family:'DM Mono',monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:5px;">⚡ {sr['strategy']} · {sr['ticker']} · {sr['period']}</div><div style="font-family:'Manrope',sans-serif;font-size:22px;font-weight:800;color:#e2e8f0;">{verdict.get('overall_verdict','')}</div></div>
              <div style="text-align:right;"><div style="font-family:'Manrope',sans-serif;font-size:30px;font-weight:900;color:{vc};">{verdict.get('verdict_emoji','')} {verdict.get('strategy_score',5)}/10</div><div style="font-family:'DM Mono',monospace;font-size:12px;color:#64748b;">{verdict.get('confidence','Medium')} Confidence</div></div>
            </div>""", unsafe_allow_html=True)

            bm1,bm2,bm3,bm4,bm5=st.columns(5)
            beat_c="#00d084" if op else "#ff4560"; beat_t="✅ Beat market" if op else "❌ Underperformed"
            beat=f"<div style='font-size:10px;margin-top:4px;font-family:DM Mono,monospace;color:{beat_c};'>{beat_t}</div>"
            for col,lbl,val,sub,color,extra in [(bm1,"Strategy Return",f"{rs}{tr:.1f}%","From $10,000",rc,beat),(bm2,"Buy & Hold",f"{bs}{bhr:.1f}%","Benchmark",bc,""),(bm3,"Win Rate",f"{wr:.0f}%",f"{nt} trades","#38bdf8",""),(bm4,"Max Drawdown",f"-{mdd:.1f}%","Peak→Trough","#ff4560",""),(bm5,"Final Value",f"${fv:,.0f}","From $10,000","#a78bfa","")]:
                with col:
                    st.markdown(f"""<div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:13px;padding:16px;margin-bottom:16px;text-align:center;">
                      <div style="font-size:10px;font-family:'DM Mono',monospace;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:7px;">{lbl}</div>
                      <div style="font-family:'Manrope',sans-serif;font-size:24px;font-weight:800;color:{color};line-height:1;">{val}</div>
                      <div style="font-size:10px;color:#64748b;margin-top:4px;font-family:'DM Mono',monospace;">{sub}</div>{extra}
                    </div>""", unsafe_allow_html=True)

            eq1,eq2=st.columns([3,2])
            with eq1:
                st.markdown("<div style='font-family:DM Mono,monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;'>📈 equity curve vs buy &amp; hold</div>", unsafe_allow_html=True)
                eq_data=bt.get("equity_curve",[]); prices=bt.get("price_history",[])
                if eq_data and prices:
                    ev=[e["value"] for e in eq_data]; ed=[e["date"] for e in eq_data]
                    st2=prices[max(0,len(prices)-len(ev))]; bhv=[10000*(p/st2) for p in prices[max(0,len(prices)-len(ev)):]]
                    feq=pgo.Figure()
                    feq.add_trace(pgo.Scatter(y=ev,x=ed,mode="lines",name="Strategy",line=dict(color="#a78bfa",width=2.5),hovertemplate="Strategy: $%{y:,.0f}<extra></extra>"))
                    feq.add_trace(pgo.Scatter(y=bhv[:len(ev)],x=ed,mode="lines",name="Buy & Hold",line=dict(color="#64748b",width=1.5,dash="dot"),hovertemplate="B&H: $%{y:,.0f}<extra></extra>"))
                    feq.add_hline(y=10000,line_dash="dash",line_color="#334155",line_width=1)
                    feq.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",height=230,margin=dict(l=0,r=0,t=4,b=0),xaxis=dict(showgrid=False,tickfont=dict(color="#64748b",size=10,family="DM Mono")),yaxis=dict(showgrid=True,gridcolor="rgba(30,45,61,0.7)",tickfont=dict(color="#64748b",size=10,family="DM Mono"),tickprefix="$",zeroline=False),legend=dict(font=dict(color="#94a3b8",size=11,family="DM Mono"),bgcolor="rgba(0,0,0,0)",x=0,y=1),hovermode="x unified")
                    st.plotly_chart(feq,use_container_width=True,config={"displayModeBar":False})
            with eq2:
                sig=cd.get("signal","NEUTRAL"); sig_c="#00d084" if "BUY" in sig or "DIP" in sig else("#ff4560" if "SELL" in sig else "#fbbf24"); sig_s=cd.get("score",5)
                st.markdown(f"""<div style="font-family:DM Mono,monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:10px;">🎯 current signal</div>
                <div style="background:#131920;border:1px solid {sig_c}44;border-radius:13px;padding:18px;margin-bottom:12px;">
                  <div style="font-family:'Manrope',sans-serif;font-size:22px;font-weight:900;color:{sig_c};margin-bottom:7px;">{sig}</div>
                  <div style="font-size:12px;color:#e2e8f0;line-height:1.6;margin-bottom:12px;">{cd.get('reason','')}</div>
                  <div style="background:#1e2d3d;border-radius:4px;height:5px;"><div style="background:{sig_c};border-radius:4px;height:5px;width:{sig_s*10}%;"></div></div>
                </div>""", unsafe_allow_html=True)
                ih="<div style='background:#131920;border:1px solid #1e2d3d;border-radius:11px;padding:14px;'>"
                for n2,v2,sfx in [("RSI",cd.get("rsi"),""),("SMA 20",cd.get("sma20"),"$"),("SMA 50",cd.get("sma50"),"$"),("SMA 200",cd.get("sma200"),"$"),("Momentum",cd.get("momentum"),"%")]:
                    if v2 is not None: ih+=f"<div style='display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #1e2d3d;'><span style='font-family:DM Mono,monospace;font-size:11px;color:#64748b;'>{n2}</span><span style='font-family:DM Mono,monospace;font-size:11px;color:#e2e8f0;font-weight:600;'>{sfx}{v2}</span></div>"
                st.markdown(ih+"</div>", unsafe_allow_html=True)

            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
            a_c="#00d084" if verdict.get("action_now")=="EXECUTE" else("#ff4560" if verdict.get("action_now")=="AVOID" else "#fbbf24")
            st.markdown(f"""<div style="background:rgba(167,139,250,0.05);border:1px solid rgba(167,139,250,0.22);border-radius:14px;padding:24px 28px;margin-bottom:18px;">
              <div style="font-family:'DM Mono',monospace;font-size:11px;color:#a78bfa;text-transform:uppercase;letter-spacing:2px;margin-bottom:14px;">🧠 AI quant verdict</div>
              <div style="display:flex;gap:20px;flex-wrap:wrap;align-items:flex-start;margin-bottom:16px;">
                <div style="background:#131920;border:1.5px solid {a_c};border-radius:11px;padding:14px 20px;text-align:center;flex-shrink:0;"><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;margin-bottom:5px;">ACTION NOW</div><div style="font-family:'Manrope',sans-serif;font-size:22px;font-weight:900;color:{a_c};">{verdict.get('action_emoji','')} {verdict.get('action_now','WAIT')}</div></div>
                <div style="flex:1;min-width:180px;"><div style="font-size:14px;color:#e2e8f0;line-height:1.8;margin-bottom:10px;">{verdict.get('summary','')}</div><div style="font-size:13px;color:#64748b;line-height:1.7;">{verdict.get('current_opportunity','')}</div></div>
              </div>
              <div style="display:flex;gap:10px;flex-wrap:wrap;">
                <div style="flex:1;background:rgba(255,69,96,0.07);border:1px solid rgba(255,69,96,0.18);border-radius:9px;padding:12px 16px;min-width:160px;"><div style="font-family:'DM Mono',monospace;font-size:10px;color:#ff4560;margin-bottom:5px;text-transform:uppercase;">⚠️ Risk Warning</div><div style="font-size:12px;color:#e2e8f0;line-height:1.6;">{verdict.get('risk_warning','')}</div></div>
                <div style="flex:1;background:rgba(56,189,248,0.07);border:1px solid rgba(56,189,248,0.18);border-radius:9px;padding:12px 16px;min-width:160px;"><div style="font-family:'DM Mono',monospace;font-size:10px;color:#38bdf8;margin-bottom:5px;text-transform:uppercase;">💡 Pro Tip</div><div style="font-size:12px;color:#e2e8f0;line-height:1.6;">{verdict.get('pro_tip','')}</div></div>
              </div>
            </div>""", unsafe_allow_html=True)

            trades=bt.get("recent_trades",[])
            if trades:
                st.markdown("<div style='font-family:DM Mono,monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:12px;'>📋 recent trades</div>", unsafe_allow_html=True)
                st.markdown("""<div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:13px;overflow:hidden;"><div style="display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr 1fr;padding:9px 18px;background:#131920;border-bottom:1px solid #1e2d3d;"><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;text-transform:uppercase;">Date</div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;text-transform:uppercase;">Entry</div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;text-transform:uppercase;">Exit</div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;text-transform:uppercase;">P&amp;L</div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;text-transform:uppercase;">Result</div></div>""", unsafe_allow_html=True)
                for trade in reversed(trades):
                    pnl=trade.get("pnl_pct",0); tc2="#00d084" if pnl>=0 else "#ff4560"; ts2="+" if pnl>=0 else ""; tr2=trade.get("result","")
                    st.markdown(f"""<div style="display:grid;grid-template-columns:1.5fr 1fr 1fr 1fr 1fr;padding:10px 18px;border-bottom:1px solid #1e2d3d;font-family:'DM Mono',monospace;font-size:12px;"><div style="color:#64748b;">{trade.get('date','')}</div><div style="color:#e2e8f0;">${trade.get('entry',0):,.2f}</div><div style="color:#e2e8f0;">${trade.get('exit',0):,.2f}</div><div style="color:{tc2};font-weight:700;">{ts2}{pnl:.2f}%</div><div style="color:{tc2};">{'✅' if tr2=='WIN' else '❌'} {tr2}</div></div>""", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    else:  # RISK PROFILE
        RP_META={"🔴 Aggressive":{"color":"#ff4560","idx":0,"on":"dp-rp-red-on","off":"dp-rp-red-off","short":"High risk · High reward","time":"1–6 months"},"🟠 Moderate":{"color":"#fb923c","idx":1,"on":"dp-rp-oran-on","off":"dp-rp-oran-off","short":"Balanced risk & growth","time":"6–18 months"},"🟡 Low Risk":{"color":"#38bdf8","idx":2,"on":"dp-rp-blue-on","off":"dp-rp-blue-off","short":"Capital preservation","time":"1–3 years"},"🟢 No Risk":{"color":"#00d084","idx":3,"on":"dp-rp-grn-on","off":"dp-rp-grn-off","short":"Safety above all","time":"3–5+ years"}}
        st.markdown("<div style='font-family:DM Mono,monospace;font-size:11px;color:#fbbf24;text-transform:uppercase;letter-spacing:2px;margin-bottom:16px;'>Step 1 — Select your risk profile</div>", unsafe_allow_html=True)

        sel=st.session_state.risk_profile
        rp_cols=st.columns(4)
        for rp_key,rp_data in RISK_PROFILES.items():
            pm=RP_META[rp_key]; i=pm["idx"]; is_sel=sel==rp_key
            chk="✓  " if is_sel else ""
            label=f"{chk}{rp_key.split()[0]}  {rp_data['label']}\n{pm['short']}\n{pm['time']}"
            with rp_cols[i]:
                if mk_btn(label, pm["on"] if is_sel else pm["off"], f"rp_{i}"):
                    st.session_state.risk_profile=rp_key; st.session_state.strategy_result=None; st.rerun()

        sp=RISK_PROFILES[sel]; sc_=RP_META[sel]["color"]
        st.markdown(f"""<div style="background:#0d1117;border:1px solid {sc_}44;border-radius:13px;padding:16px 22px;margin:14px 0 20px;">
          <div style="font-family:'DM Mono',monospace;font-size:10px;color:{sc_};text-transform:uppercase;margin-bottom:10px;">Selected: {sp['label']} profile</div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:14px;">
            <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;margin-bottom:4px;text-transform:uppercase;">Time Horizon</div><div style="font-size:13px;color:#e2e8f0;font-weight:700;">{sp['time_horizon']}</div></div>
            <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;margin-bottom:4px;text-transform:uppercase;">Allocation</div><div style="font-size:13px;color:#e2e8f0;font-weight:700;">{sp['allocation']}</div></div>
            <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;margin-bottom:4px;text-transform:uppercase;">Stop Loss</div><div style="font-size:13px;color:#e2e8f0;font-weight:700;">{sp['stop_loss']}</div></div>
            <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;margin-bottom:4px;text-transform:uppercase;">Best Strategies</div><div style="font-size:13px;color:{sc_};font-weight:700;">{' · '.join(sp['strategies'])}</div></div>
          </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div style='font-family:DM Mono,monospace;font-size:11px;color:#fbbf24;text-transform:uppercase;letter-spacing:2px;margin-bottom:14px;'>Step 2 — Configure &amp; run</div>", unsafe_allow_html=True)
        rc1,rc2=st.columns(2)
        with rc1: rp_asset=st.selectbox("Asset Type",["📈 Stock","🪙 Crypto"],key="rp_asset")
        with rc2: rp_period=st.selectbox("Backtest Period",["3mo","6mo","1y","2y"],index=2,key="rp_period")
        sugg="<div style='margin:10px 0 16px;'><span style='font-family:DM Mono,monospace;font-size:11px;color:#64748b;'>Suggested: </span>"
        for asset in sp["assets"]: sugg+=f"<span style='background:#131920;border:1px solid {sc_}33;border-radius:7px;padding:3px 9px;font-family:DM Mono,monospace;font-size:11px;color:{sc_};margin-left:5px;'>{asset}</span>"
        st.markdown(sugg+"</div>", unsafe_allow_html=True)

        _,btn_col2,_=st.columns([2,2,2])
        with btn_col2: run_risk=mk_btn("🎯  Get My Personalized Strategy","dp-cta-gold","btn_run_risk")

        if run_risk:
            if not query.strip(): st.warning("⚠️ Enter a ticker above!")
            else:
                rt=query.strip().upper(); ra="crypto" if "Crypto" in rp_asset else "stock"; stt=sp["strategies"][0]
                with st.spinner(f"Building {sp['label']} strategy for {rt}..."):
                    try:
                        res=run_strategy_analysis(rt,stt,rp_period,ra)
                        if "error" in res: st.error(f"❌ {res['error']}")
                        else:
                            bt_=res["backtest"]; cd_=res["conditions"]
                            sug=suggest_strategies_by_risk(sel,rt,{**bt_,"strategy":stt},cd_,ra)
                            st.session_state.strategy_result={"type":"risk","bt":bt_,"cd":cd_,"suggestion":sug,"ticker":rt,"profile_data":sp,"sc":sc_}
                    except Exception as e: st.error(f"❌ {e}")

        sr=st.session_state.strategy_result
        if sr and sr.get("type")=="risk":
            sug=sr["suggestion"]; bt_=sr["bt"]; cd_=sr["cd"]; sp2=sr["profile_data"]; sc2=sr["sc"]
            fc="#00d084" if sug.get("fit_emoji")=="🟢" else("#fb923c" if sug.get("fit_emoji")=="🟠" else("#ff4560" if sug.get("fit_emoji")=="🔴" else "#fbbf24"))
            st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
            st.markdown(f"""<div style="background:#0d1117;border:1px solid {fc}55;border-radius:14px;padding:22px 28px;margin-bottom:20px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
              <div><div style="font-family:'DM Mono',monospace;font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:5px;">🎯 {sp2['label']} Profile · {sr['ticker']}</div><div style="font-family:'Manrope',sans-serif;font-size:22px;font-weight:800;color:#e2e8f0;">{sug.get('overall_fit','')}</div></div>
              <div style="text-align:right;"><div style="font-family:'Manrope',sans-serif;font-size:38px;font-weight:900;color:{fc};">{sug.get('fit_emoji','')} {sug.get('fit_score',5)}/10</div><div style="font-family:'DM Mono',monospace;font-size:12px;color:#64748b;">Strategy-Profile Fit Score</div></div>
            </div>""", unsafe_allow_html=True)
            ps1,ps2=st.columns(2)
            with ps1: st.markdown(f"""<div style="background:#131920;border:1.5px solid {sc2};border-radius:13px;padding:18px;margin-bottom:14px;"><div style="font-family:'DM Mono',monospace;font-size:10px;color:{sc2};text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">⭐ Primary Strategy</div><div style="font-family:'Manrope',sans-serif;font-size:17px;font-weight:800;color:#e2e8f0;margin-bottom:8px;">{sug.get('primary_strategy','')}</div><div style="font-size:13px;color:#94a3b8;line-height:1.7;">{sug.get('primary_reason','')}</div></div>""", unsafe_allow_html=True)
            with ps2: st.markdown(f"""<div style="background:#131920;border:1px solid #253347;border-radius:13px;padding:18px;margin-bottom:14px;"><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px;">🔄 Backup Strategy</div><div style="font-family:'Manrope',sans-serif;font-size:17px;font-weight:800;color:#e2e8f0;margin-bottom:8px;">{sug.get('secondary_strategy','')}</div><div style="font-size:13px;color:#94a3b8;line-height:1.7;">{sug.get('secondary_reason','')}</div></div>""", unsafe_allow_html=True)
            a1,a2,a3,a4=st.columns(4)
            for col,lbl,val,color in [(a1,"📥 Entry",sug.get("entry_advice",""),"#00d084"),(a2,"📤 Exit",sug.get("exit_advice",""),"#38bdf8"),(a3,"💼 Position Size",sug.get("position_size",""),sc2),(a4,"⚠️ Key Warning",sug.get("key_warning",""),"#ff4560")]:
                with col: st.markdown(f"""<div style="background:#131920;border:1px solid #253347;border-radius:11px;padding:14px;margin-bottom:14px;"><div style="font-family:'DM Mono',monospace;font-size:10px;color:{color};text-transform:uppercase;letter-spacing:1px;margin-bottom:7px;">{lbl}</div><div style="font-size:12px;color:#e2e8f0;line-height:1.6;">{val}</div></div>""", unsafe_allow_html=True)
            st.markdown(f"""<div style="background:rgba(167,139,250,0.05);border:1px solid rgba(167,139,250,0.2);border-radius:11px;padding:16px 20px;margin-bottom:16px;display:flex;gap:12px;align-items:flex-start;">
              <div style="font-size:20px;flex-shrink:0;">💡</div>
              <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#a78bfa;text-transform:uppercase;margin-bottom:5px;">Personalized Tip — {sp2['label']}</div><div style="font-size:13px;color:#e2e8f0;line-height:1.7;">{sug.get('personalized_tip','')}</div></div>
            </div>""", unsafe_allow_html=True)
            stt2=sp2["strategies"][0]
            st.markdown(f"""<div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:13px;padding:18px 22px;">
              <div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;text-transform:uppercase;letter-spacing:2px;margin-bottom:12px;">📊 backtest summary — {stt2}</div>
              <div style="display:flex;gap:20px;flex-wrap:wrap;">
                <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;margin-bottom:3px;">Return</div><div style="font-size:18px;font-weight:800;color:{'#00d084' if bt_['total_return']>=0 else '#ff4560'};">{'+'if bt_['total_return']>=0 else ''}{bt_['total_return']:.1f}%</div></div>
                <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;margin-bottom:3px;">Buy &amp; Hold</div><div style="font-size:18px;font-weight:800;color:{'#00d084' if bt_['bh_return']>=0 else '#ff4560'};">{'+'if bt_['bh_return']>=0 else ''}{bt_['bh_return']:.1f}%</div></div>
                <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;margin-bottom:3px;">Win Rate</div><div style="font-size:18px;font-weight:800;color:#38bdf8;">{bt_['win_rate']:.0f}%</div></div>
                <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;margin-bottom:3px;">Max Drawdown</div><div style="font-size:18px;font-weight:800;color:#ff4560;">-{bt_['max_drawdown']:.1f}%</div></div>
                <div><div style="font-family:'DM Mono',monospace;font-size:10px;color:#64748b;margin-bottom:3px;">Signal</div><div style="font-size:16px;font-weight:800;color:{'#00d084' if 'BUY' in cd_.get('signal','') else '#ff4560' if 'SELL' in cd_.get('signal','') else '#fbbf24'};">{cd_.get('signal','NEUTRAL')}</div></div>
              </div>
            </div>""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("""<div style="text-align:center;padding:24px 0 16px;margin-top:20px;border-top:1px solid #1e2d3d;">
  <div style="font-family:'DM Mono',monospace;font-size:12px;color:#64748b;">Built by <strong style="color:#e2e8f0;">Paddy</strong> · DataPulse AI · 5 Agents · Strategy Engine · Risk Profiles · Llama 3.3 70B · 100% Free</div>
  <div style="font-family:'DM Mono',monospace;font-size:11px;color:#334155;margin-top:5px;">⚠️ Educational purposes only · Not financial advice</div>
</div>""", unsafe_allow_html=True)