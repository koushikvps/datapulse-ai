# app.py — DataPulse AI Dashboard
import streamlit as st
import plotly.graph_objects as pgo
from orchestrator import run_datapulse
from agents.stock_agent import format_market_cap

st.set_page_config(
    page_title="DataPulse AI",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg:        #07090f;
    --bg2:       #0d1117;
    --bg3:       #131920;
    --bg4:       #1a2332;
    --border:    #1e2d3d;
    --border2:   #253347;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --dim:       #334155;
    --green:     #00d084;
    --green-dim: rgba(0,208,132,0.1);
    --red:       #ff4560;
    --red-dim:   rgba(255,69,96,0.1);
    --blue:      #38bdf8;
    --blue-dim:  rgba(56,189,248,0.1);
    --gold:      #fbbf24;
    --gold-dim:  rgba(251,191,36,0.1);
}

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Manrope', sans-serif !important;
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stSidebar"] { display: none !important; }

.block-container { padding: 0 !important; max-width: 100% !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 2px; }

[data-testid="stTextInput"] input {
    background: var(--bg3) !important;
    border: 1.5px solid var(--border2) !important;
    border-radius: 10px !important;
    color: var(--text) !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 15px !important;
    padding: 14px 18px !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: var(--green) !important;
    box-shadow: 0 0 0 3px rgba(0,208,132,0.15) !important;
}
[data-testid="stTextInput"] input::placeholder { color: var(--dim) !important; }
[data-testid="stTextInput"] label { display: none !important; }

[data-testid="stButton"] button {
    background: var(--green) !important;
    color: #07090f !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 800 !important;
    font-size: 15px !important;
    padding: 14px 32px !important;
    transition: all 0.2s !important;
}
[data-testid="stButton"] button:hover {
    background: #00f097 !important;
    box-shadow: 0 0 24px rgba(0,208,132,0.4) !important;
    transform: translateY(-1px) !important;
}
</style>
""", unsafe_allow_html=True)

# ── NAVBAR ────────────────────────────────────────────────────
st.markdown("""
<div style="background:var(--bg2); border-bottom:1px solid var(--border); padding:0 40px; height:60px; display:flex; align-items:center; justify-content:space-between;">
    <div style="display:flex; align-items:center; gap:14px;">
        <div style="width:36px; height:36px; background:linear-gradient(135deg,#00d084,#38bdf8); border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:18px;">📡</div>
        <span style="font-family:'Manrope',sans-serif; font-weight:800; font-size:22px; letter-spacing:-0.5px;">Data<span style="color:var(--green);">Pulse</span> <span style="font-size:14px; color:var(--muted); font-weight:400;">AI</span></span>
    </div>
    <div style="display:flex; align-items:center; gap:8px;">
        <div style="width:7px; height:7px; border-radius:50%; background:var(--green); box-shadow:0 0 8px var(--green);"></div>
        <span style="font-family:'DM Mono',monospace; font-size:12px; color:var(--muted);">5 agents online · Llama 3.3 70B · LangGraph</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── HERO + SEARCH ─────────────────────────────────────────────
st.markdown("<div style='padding:40px 48px 0;'>", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; margin-bottom:32px;">
    <div style="font-family:'Manrope',sans-serif; font-size:44px; font-weight:800; color:var(--text); letter-spacing:-1px; line-height:1.1; margin-bottom:10px;">
        Real-time AI intelligence<br><span style="color:var(--green);">on any stock.</span>
    </div>
    <div style="font-size:16px; color:var(--muted);">Type a company or ticker. 5 AI agents analyze it in real time.</div>
</div>
""", unsafe_allow_html=True)

col_inp, col_btn = st.columns([5, 1])
with col_inp:
    query = st.text_input("q", placeholder="Apple  ·  TSLA  ·  NVIDIA  ·  Amazon  ·  Microsoft...", label_visibility="collapsed")
with col_btn:
    analyze = st.button("Analyze 🚀", use_container_width=True)

# Quick tickers
tickers_html = "<div style='display:flex; justify-content:center; gap:8px; margin-top:12px; flex-wrap:wrap;'>"
for t in ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN", "META"]:
    tickers_html += f"<div style='background:var(--bg3); border:1px solid var(--border); border-radius:8px; padding:5px 12px; font-family:DM Mono,monospace; font-size:12px; color:var(--muted);'>{t}</div>"
tickers_html += "</div>"
st.markdown(tickers_html, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ── RUN ANALYSIS ──────────────────────────────────────────────
if analyze and query.strip():
    st.markdown("<div style='padding:32px 48px;'>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:var(--border); margin-bottom:28px;'>", unsafe_allow_html=True)

    # Progress tracker
    st.markdown("<div style='font-family:DM Mono,monospace; font-size:11px; color:var(--green); letter-spacing:2px; text-transform:uppercase; margin-bottom:12px;'>▶ agents running</div>", unsafe_allow_html=True)
    prog = st.empty()

    def show_progress(done, active):
        agents = [("🔎","Resolver"),("📈","Stock"),("📰","News"),("💬","Sentiment"),("⚠️","Risk"),("🧠","Analyst")]
        html = "<div style='display:flex; gap:8px; flex-wrap:wrap; margin-bottom:20px;'>"
        for icon, name in agents:
            if name in done:
                s = "background:var(--green-dim); border:1px solid var(--green); color:var(--green);"; p = "✓ "
            elif name == active:
                s = "background:var(--blue-dim); border:1px solid var(--blue); color:var(--blue);"; p = "⟳ "
            else:
                s = "background:var(--bg3); border:1px solid var(--border); color:var(--dim);"; p = "○ "
            html += f"<div style='{s} border-radius:20px; padding:6px 14px; font-family:DM Mono,monospace; font-size:12px;'>{icon} {p}{name}</div>"
        html += "</div>"
        return html

    prog.markdown(show_progress([], "Resolver"), unsafe_allow_html=True)

    with st.spinner(f"Analyzing {query.strip()}... this takes about 60 seconds ⏳"):
        try:
            prog.markdown(show_progress(["Resolver"], "Stock"), unsafe_allow_html=True)
            result = run_datapulse(query.strip())
            prog.markdown(show_progress(["Resolver","Stock","News","Sentiment","Risk","Analyst"], ""), unsafe_allow_html=True)

            stock    = result.get("stock_data", {})
            news     = result.get("news_articles", [])
            news_s   = result.get("news_sentiment", {})
            social   = result.get("social_sentiment", {})
            risk     = result.get("risk", {})
            analysis = result.get("analysis", {})
            company  = result.get("company_name", query)
            ticker   = result.get("ticker", query.upper())

            price     = stock.get("current_price", 0)
            chg       = stock.get("change", 0)
            chg_pct   = stock.get("change_pct", 0)
            mktcap    = format_market_cap(stock.get("market_cap", 0))
            rec       = analysis.get("recommendation", "HOLD")
            rec_emoji = analysis.get("rec_emoji", "🟡")
            target    = analysis.get("price_target", price)
            upside    = analysis.get("upside_pct", 0)
            risk_score= risk.get("overall_score", 5)
            risk_label= risk.get("overall_label", "Medium")
            risk_emoji= risk.get("overall_emoji", "🟡")
            bull_pct  = social.get("bull_pct", 50)
            bear_pct  = social.get("bear_pct", 50)
            chg_color = "var(--green)" if chg >= 0 else "var(--red)"
            chg_sign  = "+" if chg >= 0 else ""

            # ── Company Header ──
            st.markdown(f"""
            <div style="background:var(--bg2); border:1px solid var(--border); border-radius:16px; padding:24px 32px; margin-bottom:20px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:16px;">
                <div>
                    <div style="font-family:'Manrope',sans-serif; font-size:28px; font-weight:800; color:var(--text); letter-spacing:-0.5px;">{company}</div>
                    <div style="font-family:'DM Mono',monospace; font-size:13px; color:var(--muted); margin-top:4px;">{ticker} · {stock.get('sector','—')} · {stock.get('industry','—')}</div>
                </div>
                <div style="display:flex; align-items:baseline; gap:12px;">
                    <div style="font-family:'Manrope',sans-serif; font-size:40px; font-weight:800; color:var(--text); letter-spacing:-1px;">${price:,.2f}</div>
                    <div style="font-family:'DM Mono',monospace; font-size:16px; color:{chg_color};">{chg_sign}{chg:.2f} ({chg_sign}{chg_pct:.2f}%)</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── 4 Metric Cards ──
            c1, c2, c3, c4 = st.columns(4)
            rec_bg = "var(--green-dim)" if rec=="BUY" else ("var(--red-dim)" if rec=="SELL" else "var(--gold-dim)")
            rec_bd = "var(--green)"     if rec=="BUY" else ("var(--red)"     if rec=="SELL" else "var(--gold)")

            for col, icon, label, val, sub, bg, bd in [
                (c1, "📈", "Recommendation", f"{rec_emoji} {rec}", f"Target ${target:,.2f} ({chg_sign}{upside:.1f}%)", rec_bg, rec_bd),
                (c2, "⚠️", "Risk Level",     f"{risk_emoji} {risk_score}/10", risk_label, "var(--bg3)", "var(--border2)"),
                (c3, "💬", "Social Mood",    f"{'🟢' if bull_pct>55 else '🔴' if bull_pct<45 else '🟡'} {bull_pct}% Bulls", f"{bear_pct}% Bears", "var(--bg3)", "var(--border2)"),
                (c4, "🏢", "Market Cap",     mktcap, f"P/E: {stock.get('pe_ratio','N/A')}", "var(--bg3)", "var(--border2)"),
            ]:
                with col:
                    st.markdown(f"""
                    <div style="background:{bg}; border:1px solid {bd}; border-radius:14px; padding:20px 22px; height:110px; margin-bottom:20px;">
                        <div style="font-size:11px; font-family:'DM Mono',monospace; color:var(--muted); text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">{icon} {label}</div>
                        <div style="font-family:'Manrope',sans-serif; font-size:24px; font-weight:800; color:var(--text); line-height:1;">{val}</div>
                        <div style="font-size:12px; color:var(--muted); margin-top:6px; font-family:'DM Mono',monospace;">{sub}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # ── Price Chart + News ──
            col_chart, col_news = st.columns([3, 2])

            with col_chart:
                st.markdown("<div style='font-family:DM Mono,monospace; font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:2px; margin-bottom:10px;'>📈 30-Day Price</div>", unsafe_allow_html=True)
                ph = stock.get("price_history", [])
                if ph:
                    c = "#00d084" if ph[-1] >= ph[0] else "#ff4560"
                    fig = pgo.Figure()
                    fig.add_trace(pgo.Scatter(
                        y=ph, mode="lines",
                        line=dict(color=c, width=2.5),
                        fill="tozeroy",
                        fillcolor=f"rgba({'0,208,132' if c=='#00d084' else '255,69,96'},0.07)",
                        hovertemplate="$%{y:.2f}<extra></extra>"
                    ))
                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        height=200, margin=dict(l=0,r=0,t=8,b=0),
                        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
                        yaxis=dict(showgrid=True, gridcolor="rgba(30,45,61,0.8)",
                                   tickfont=dict(color="#64748b",size=11,family="DM Mono"), zeroline=False),
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

                # 52W range
                lo52 = stock.get("week_52_low", 0)
                hi52 = stock.get("week_52_high", 0)
                if hi52 and lo52 and hi52 != lo52:
                    pos = (price - lo52) / (hi52 - lo52) * 100
                    st.markdown(f"""
                    <div style="background:var(--bg3); border:1px solid var(--border); border-radius:10px; padding:14px 18px; margin-top:4px;">
                        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                            <span style="font-family:'DM Mono',monospace; font-size:11px; color:var(--muted);">52W LOW ${lo52:,.2f}</span>
                            <span style="font-family:'DM Mono',monospace; font-size:11px; color:var(--muted);">52W HIGH ${hi52:,.2f}</span>
                        </div>
                        <div style="background:var(--border); border-radius:4px; height:6px; position:relative;">
                            <div style="background:linear-gradient(90deg,var(--red),var(--gold),var(--green)); border-radius:4px; height:6px; width:100%;"></div>
                            <div style="position:absolute; top:-4px; left:{min(max(pos,2),98):.1f}%; width:14px; height:14px; background:white; border-radius:50%; border:2px solid var(--bg2); transform:translateX(-50%);"></div>
                        </div>
                        <div style="font-family:'DM Mono',monospace; font-size:11px; color:var(--muted); text-align:center; margin-top:6px;">At {pos:.0f}% of 52-week range</div>
                    </div>
                    """, unsafe_allow_html=True)

            with col_news:
                st.markdown(f"<div style='font-family:DM Mono,monospace; font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:2px; margin-bottom:10px;'>📰 News · {news_s.get('emoji','🟡')} {news_s.get('overall','Neutral')} ({news_s.get('score',5)}/10)</div>", unsafe_allow_html=True)
                for a in news[:6]:
                    sc = "#00d084" if a.get("sentiment")=="positive" else ("#ff4560" if a.get("sentiment")=="negative" else "#fbbf24")
                    st.markdown(f"""
                    <a href="{a.get('url','#')}" target="_blank" style="text-decoration:none;">
                    <div style="background:var(--bg3); border:1px solid var(--border); border-left:3px solid {sc}; border-radius:0 10px 10px 0; padding:10px 14px; margin-bottom:7px;">
                        <div style="font-size:13px; color:var(--text); font-weight:500; line-height:1.4; margin-bottom:3px;">{a.get('emoji','🟡')} {a.get('title','')[:70]}</div>
                        <div style="display:flex; justify-content:space-between;">
                            <span style="font-family:'DM Mono',monospace; font-size:10px; color:var(--muted);">{a.get('source','')}</span>
                            <span style="font-family:'DM Mono',monospace; font-size:10px; color:{sc};">{a.get('score',5)}/10</span>
                        </div>
                    </div></a>
                    """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Risk + Social ──
            col_risk, col_social = st.columns([3, 2])

            with col_risk:
                st.markdown(f"<div style='font-family:DM Mono,monospace; font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:2px; margin-bottom:10px;'>⚠️ Risk · {risk_emoji} {risk_label}</div>", unsafe_allow_html=True)
                dims = risk.get("dimensions", [])
                if dims:
                    fig2 = pgo.Figure()
                    names  = [d["name"] for d in dims]
                    scores = [d["score"] for d in dims]
                    colors = ["#ff4560" if s>=7 else "#fbbf24" if s>=5 else "#00d084" for s in scores]
                    fig2.add_trace(pgo.Bar(
                        x=scores, y=names, orientation="h",
                        marker=dict(color=colors, opacity=0.85),
                        text=[f"{s}/10" for s in scores],
                        textposition="outside",
                        textfont=dict(color="#94a3b8", size=12, family="DM Mono"),
                        hovertemplate="%{y}: %{x}/10<extra></extra>"
                    ))
                    fig2.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        height=200, margin=dict(l=0,r=40,t=0,b=0),
                        xaxis=dict(range=[0,13], showgrid=False, showticklabels=False, zeroline=False),
                        yaxis=dict(tickfont=dict(color="#94a3b8",size=12,family="DM Mono"), zeroline=False),
                        showlegend=False, bargap=0.35
                    )
                    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
                for r_item in risk.get("key_risks", []):
                    st.markdown(f"<div style='background:var(--red-dim); border:1px solid rgba(255,69,96,0.2); border-radius:8px; padding:8px 14px; margin-bottom:6px; font-size:13px; color:var(--text);'>⚡ {r_item}</div>", unsafe_allow_html=True)

            with col_social:
                st.markdown("<div style='font-family:DM Mono,monospace; font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:2px; margin-bottom:10px;'>💬 Social Sentiment</div>", unsafe_allow_html=True)
                fig3 = pgo.Figure(pgo.Pie(
                    values=[bull_pct, bear_pct], labels=["Bulls 🟢","Bears 🔴"],
                    hole=0.68, marker=dict(colors=["#00d084","#ff4560"]),
                    textinfo="none", hovertemplate="%{label}: %{value}%<extra></extra>"
                ))
                fig3.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", height=180,
                    margin=dict(l=0,r=0,t=0,b=0),
                    showlegend=True,
                    legend=dict(font=dict(color="#94a3b8",size=12,family="DM Mono"), bgcolor="rgba(0,0,0,0)"),
                    annotations=[dict(text=f"<b>{bull_pct}%</b><br>Bulls", x=0.5, y=0.5,
                                      font=dict(size=16,color="#e2e8f0",family="Manrope"), showarrow=False)]
                )
                st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

                buzz = social.get("buzz_score", 5)
                st.markdown(f"""
                <div style="background:var(--bg3); border:1px solid var(--border); border-radius:10px; padding:14px 18px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                        <span style="font-family:'DM Mono',monospace; font-size:12px; color:var(--muted);">Buzz Score</span>
                        <span style="font-family:'DM Mono',monospace; font-size:12px; color:var(--green); font-weight:700;">{buzz}/10</span>
                    </div>
                    <div style="background:var(--border); border-radius:4px; height:5px; margin-bottom:12px;">
                        <div style="background:var(--green); border-radius:4px; height:5px; width:{buzz*10}%;"></div>
                    </div>
                    <div style="font-size:13px; color:var(--text); line-height:1.6;">{social.get('summary','')}</div>
                </div>
                """, unsafe_allow_html=True)
                themes = social.get("key_themes", [])
                if themes:
                    th_html = "<div style='margin-top:8px; display:flex; flex-wrap:wrap; gap:6px;'>"
                    for t in themes:
                        th_html += f"<div style='background:var(--blue-dim); border:1px solid rgba(56,189,248,0.25); border-radius:16px; padding:4px 12px; font-size:12px; color:var(--blue); font-family:DM Mono,monospace;'>{t}</div>"
                    th_html += "</div>"
                    st.markdown(th_html, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── AI Analyst Report ──
            rec_bg2 = "rgba(0,208,132,0.06)"  if rec=="BUY"  else ("rgba(255,69,96,0.06)"  if rec=="SELL" else "rgba(251,191,36,0.06)")
            rec_bd2 = "rgba(0,208,132,0.3)"   if rec=="BUY"  else ("rgba(255,69,96,0.3)"   if rec=="SELL" else "rgba(251,191,36,0.3)")
            rec_col = "var(--green)"           if rec=="BUY"  else ("var(--red)"            if rec=="SELL" else "var(--gold)")

            st.markdown(f"""
            <div style="background:{rec_bg2}; border:1px solid {rec_bd2}; border-radius:16px; padding:28px 32px; margin-bottom:20px;">
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:20px; flex-wrap:wrap; gap:12px;">
                    <div>
                        <div style="font-family:'DM Mono',monospace; font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:2px; margin-bottom:6px;">🧠 AI Analyst Report</div>
                        <div style="font-family:'Manrope',sans-serif; font-size:22px; font-weight:800; color:var(--text);">{analysis.get('verdict_headline','')}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-family:'Manrope',sans-serif; font-size:36px; font-weight:900; color:{rec_col};">{rec_emoji} {rec}</div>
                        <div style="font-family:'DM Mono',monospace; font-size:13px; color:var(--muted);">Target: ${target:,.2f} · {analysis.get('time_horizon','12 months')}</div>
                    </div>
                </div>
                <div style="font-size:15px; color:var(--text); line-height:1.8; border-left:3px solid {rec_col}; padding-left:16px;">
                    {analysis.get('thesis','')}
                </div>
            </div>
            """, unsafe_allow_html=True)

            cb, cs, cc = st.columns(3)
            with cb:
                st.markdown(f"<div style='background:var(--green-dim); border:1px solid rgba(0,208,132,0.25); border-radius:14px; padding:20px;'><div style='font-family:DM Mono,monospace; font-size:11px; color:var(--green); text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;'>📈 Bull Case</div><div style='font-size:14px; color:var(--text); line-height:1.7;'>{analysis.get('bull_case','')}</div></div>", unsafe_allow_html=True)
            with cs:
                st.markdown(f"<div style='background:var(--red-dim); border:1px solid rgba(255,69,96,0.25); border-radius:14px; padding:20px;'><div style='font-family:DM Mono,monospace; font-size:11px; color:var(--red); text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;'>📉 Bear Case</div><div style='font-size:14px; color:var(--text); line-height:1.7;'>{analysis.get('bear_case','')}</div></div>", unsafe_allow_html=True)
            with cc:
                cats_html = "<div style='background:var(--bg3); border:1px solid var(--border2); border-radius:14px; padding:20px;'><div style='font-family:DM Mono,monospace; font-size:11px; color:var(--blue); text-transform:uppercase; letter-spacing:1px; margin-bottom:10px;'>⚡ Catalysts</div>"
                for cat in analysis.get("catalysts", []):
                    cats_html += f"<div style='font-size:13px; color:var(--text); padding:6px 0; border-bottom:1px solid var(--border); line-height:1.5;'>→ {cat}</div>"
                cats_html += "</div>"
                st.markdown(cats_html, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:var(--bg2); border:1px solid var(--border); border-radius:14px; padding:24px 28px;">
                <div style="font-family:'DM Mono',monospace; font-size:11px; color:var(--muted); text-transform:uppercase; letter-spacing:2px; margin-bottom:12px;">📊 Detailed Analysis</div>
                <div style="font-size:15px; color:#94a3b8; line-height:1.9;">{analysis.get('detailed_analysis','')}</div>
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")
            st.info("💡 Check your GROQ_API_KEY and internet connection")

    st.markdown("</div>", unsafe_allow_html=True)

elif analyze and not query.strip():
    st.warning("⚠️ Please enter a company name or ticker!")

# ── FOOTER ────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:32px 0 20px; margin-top:32px; border-top:1px solid var(--border);">
    <div style="font-family:'DM Mono',monospace; font-size:12px; color:var(--muted);">
        Built by <strong style="color:var(--text);">Koushik</strong> · DataPulse AI · 5 AI Agents · Llama 3.3 70B · LangGraph · Groq · 100% Free
    </div>
    <div style="font-family:'DM Mono',monospace; font-size:11px; color:var(--dim); margin-top:6px;">⚠️ For educational purposes only. Not financial advice.</div>
</div>
""", unsafe_allow_html=True)