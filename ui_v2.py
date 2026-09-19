from __future__ import annotations

import html
import streamlit as st


NAV_ITEMS = [
    ("홈", "⌂"),
    ("시장 현황", "▥"),
    ("종목 분석", "◫"),
    ("공시 분석", "▤"),
    ("테마 & 섹터", "◇"),
    ("포트폴리오", "▣"),
    ("관심 종목", "☆"),
    ("AI 인사이트", "✦"),
    ("데이터 연결 관리", "⚙"),
]


def apply_theme():
    st.markdown(
        """
<style>
:root {
  --bg: #F7F9FC;
  --surface: #FFFFFF;
  --surface-soft: #F9FBFF;
  --line: #E6EAF0;
  --line-strong: #D8DEE8;
  --text: #0F172A;
  --muted: #64748B;
  --blue: #2563EB;
  --blue-soft: #EFF6FF;
  --green: #059669;
  --red: #DC2626;
}
html, body, [class*="css"] {
  font-family: Pretendard, "Noto Sans KR", "Apple SD Gothic Neo", sans-serif;
}
.stApp {
  background: var(--bg);
  color: var(--text);
}
.block-container {
  max-width: 1480px;
  padding-top: 1.4rem;
  padding-bottom: 4rem;
}
header[data-testid="stHeader"] {
  background: rgba(247,249,252,.88);
  backdrop-filter: blur(12px);
}
section[data-testid="stSidebar"] {
  background: #FFFFFF;
  border-right: 1px solid var(--line);
}
section[data-testid="stSidebar"] > div {
  padding-top: .9rem;
}
[data-testid="stSidebar"] .stRadio > label {
  display: none;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
  gap: .18rem;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
  border-radius: 12px;
  padding: .45rem .55rem;
  transition: all .15s ease;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
  background: #F3F6FB;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) {
  background: #EAF2FF;
  color: #1D4ED8;
  font-weight: 700;
}
h1, h2, h3, h4 {
  color: var(--text);
  letter-spacing: -.035em;
}
h1 { font-weight: 800; }
h2, h3 { font-weight: 760; }
p, li { line-height: 1.62; }
[data-testid="stCaptionContainer"] {
  color: var(--muted);
}
[data-testid="stMetric"] {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 16px 18px;
  box-shadow: 0 8px 24px rgba(15,23,42,.035);
}
[data-testid="stMetricLabel"] {
  color: var(--muted);
}
[data-testid="stMetricValue"] {
  color: var(--text);
  font-weight: 750;
}
[data-testid="stVerticalBlockBorderWrapper"] {
  border-color: var(--line) !important;
  border-radius: 16px !important;
  background: var(--surface);
  box-shadow: 0 8px 24px rgba(15,23,42,.03);
}
.stButton > button, .stFormSubmitButton > button {
  border-radius: 11px;
  min-height: 2.7rem;
  font-weight: 700;
}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {
  background: var(--blue);
  border-color: var(--blue);
}
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
  border-radius: 12px !important;
}
.stTabs [data-baseweb="tab-list"] {
  gap: 8px;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 10px;
  padding: 8px 12px;
}
.stDataFrame {
  border: 1px solid var(--line);
  border-radius: 14px;
  overflow: hidden;
}
.planx-brand {
  display:flex; align-items:center; gap:10px; margin: 2px 0 18px 0;
}
.planx-brand-mark {
  width:32px; height:32px; border-radius:10px;
  display:flex; align-items:center; justify-content:center;
  background:linear-gradient(145deg,#2563EB,#60A5FA);
  color:white; font-size:18px; font-weight:800;
}
.planx-brand-title {
  font-size:18px; line-height:1.15; font-weight:800; letter-spacing:-.03em;
}
.planx-brand-sub {
  font-size:10px; color:#94A3B8; margin-top:2px;
}
.planx-hero {
  background: linear-gradient(135deg, #FFFFFF 0%, #F8FBFF 55%, #EFF6FF 100%);
  border: 1px solid #E2E8F0;
  border-radius: 22px;
  padding: 28px 30px;
  margin-bottom: 18px;
  box-shadow: 0 14px 38px rgba(15,23,42,.045);
}
.planx-eyebrow {
  color:#2563EB; font-size:12px; font-weight:800; letter-spacing:.08em;
  text-transform:uppercase; margin-bottom:8px;
}
.planx-hero h1 {
  margin:0; font-size:34px; line-height:1.18;
}
.planx-hero p {
  margin:9px 0 0; color:#64748B; font-size:14px;
}
.planx-card {
  background:#FFFFFF;
  border:1px solid #E6EAF0;
  border-radius:16px;
  padding:17px 18px;
  min-height:116px;
  box-shadow:0 8px 24px rgba(15,23,42,.03);
}
.planx-card-title {
  font-size:12px; color:#64748B; margin-bottom:8px; font-weight:700;
}
.planx-card-value {
  font-size:22px; color:#0F172A; font-weight:800; letter-spacing:-.03em;
}
.planx-card-note {
  margin-top:7px; font-size:11px; color:#94A3B8;
}
.planx-empty {
  background: #FFFFFF;
  border:1px dashed #CBD5E1;
  border-radius:16px;
  padding:22px;
  color:#64748B;
}
.planx-source {
  display:inline-flex; align-items:center; gap:5px;
  color:#64748B; background:#F8FAFC; border:1px solid #E2E8F0;
  padding:4px 8px; border-radius:999px; font-size:10px;
}
.planx-status-ok { color:#047857; background:#ECFDF5; border-color:#A7F3D0; }
.planx-status-wait { color:#92400E; background:#FFFBEB; border-color:#FDE68A; }
.planx-status-bad { color:#B91C1C; background:#FEF2F2; border-color:#FECACA; }
hr { border-color:#E6EAF0 !important; }
@media (max-width: 900px) {
  .block-container { padding-left:1rem; padding-right:1rem; }
  .planx-hero { padding:22px 20px; }
  .planx-hero h1 { font-size:28px; }
}
/* Quiet, readable research workspace. */
.block-container { max-width:1240px; padding-top:2rem; }
.stApp { background:#f8f6f1; }
section[data-testid="stSidebar"] { background:#eee7da; border-right:0; }
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color:#493e2f; }
section[data-testid="stSidebar"] .planx-brand-title { color:#493e2f; font-size:22px; }
section[data-testid="stSidebar"] .planx-brand-sub { color:#806e50; font-size:13px; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap:10px; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label { padding:14px 12px; border-radius:8px; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover { background:#e7ddc9; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) { background:#dfcea8; box-shadow:inset 3px 0 #ad873f; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) p { color:#493e2f; }
[data-testid="stSidebar"] .stButton button p { color:#1b2c45; }
.planx-brand { margin:12px 0 36px; }
.planx-brand-mark { background:#a17c36; border-radius:9px; width:38px; height:38px; }
.planx-hero { background:transparent; border:0; border-radius:0; padding:0 0 18px; box-shadow:none; margin-bottom:6px; }
.planx-hero h1 { font-size:36px; font-weight:750; }
.planx-hero p { font-size:16px; color:#77674e; max-width:650px; }
.planx-eyebrow { font-size:12px; color:#98763a; letter-spacing:.12em; }
.planx-card { box-shadow:none; min-height:132px; border-radius:12px; padding:22px; border-top:3px solid #b1883c; }
.planx-card-title { font-size:14px; font-weight:500; }
.planx-card-value { font-size:28px; font-variant-numeric:tabular-nums; }
.planx-card-note { font-size:13px; color:#5d6d82; }
[data-testid="stMetric"] { box-shadow:none; border-radius:12px; }
[data-testid="stExpander"] { background:#fff; border-radius:10px; }
[data-testid="stExpander"] summary p { font-size:15px; }
[data-testid="stMarkdownContainer"] p { font-size:16px; line-height:1.75; }
[data-testid="stCaptionContainer"] p { font-size:14px; }
.stTabs [data-baseweb="tab-list"] { gap:4px; overflow-x:auto; }
.stTabs [data-baseweb="tab"] { font-size:15px; padding:12px 14px; white-space:nowrap; }
.stTextInput input { min-height:46px; font-size:16px; background:#fff; }
.stButton > button, .stFormSubmitButton > button { min-height:44px; border-radius:8px; }
@media (max-width:640px) {
  .block-container { padding-top:1.3rem; }
  .planx-hero h1 { font-size:28px; }
  .planx-card { min-height:100px; padding:14px; }
  .planx-card-value { font-size:23px; }
}

/* Generated reference dashboard match */
.stApp { background:#f5f8fc !important; }
.block-container { max-width: 1360px !important; padding-top: 1.0rem !important; padding-bottom: 2rem !important; }
section[data-testid="stSidebar"] { background:#f8fafc !important; border-right:1px solid #e5eaf1 !important; min-width:190px; }
section[data-testid="stSidebar"] > div { padding: 1.1rem .75rem !important; }
section[data-testid="stSidebar"] .planx-brand { margin: 4px 8px 20px !important; }
section[data-testid="stSidebar"] .planx-brand-mark { width:30px !important; height:30px !important; border-radius:9px !important; background:#2563eb !important; }
section[data-testid="stSidebar"] .planx-brand-title { font-size:16px !important; color:#172033 !important; }
section[data-testid="stSidebar"] .planx-brand-sub { font-size:9px !important; color:#94a3b8 !important; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap:3px !important; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label { padding:9px 10px !important; border-radius:8px !important; color:#64748b !important; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) { background:#eaf2ff !important; color:#2563eb !important; box-shadow:none !important; }
.px-dashboard-head { display:flex; align-items:center; justify-content:space-between; gap:16px; margin:0 0 10px; }
.px-dashboard-brand { font-size:22px; font-weight:800; color:#172033; letter-spacing:-.04em; }
.px-dashboard-brand span { color:#64748b; font-weight:600; font-size:13px; margin-left:7px; }
.px-search-pill { flex:1; max-width:410px; height:34px; display:flex; align-items:center; gap:8px; padding:0 13px; border:1px solid #e3e8ef; border-radius:9px; background:#fff; color:#a0a9b8; font-size:11px; }
.px-head-meta { display:flex; align-items:center; gap:12px; color:#64748b; font-size:10px; white-space:nowrap; }
.px-dashboard-title { margin:7px 0 12px; }
.px-dashboard-title .eyebrow { color:#2563eb; font-size:10px; font-weight:800; letter-spacing:.1em; }
.px-dashboard-title h1 { margin:2px 0 0; font-size:25px; font-weight:800; letter-spacing:-.045em; }
.px-dashboard-title p { margin:3px 0 0; color:#7b8798; font-size:11px; }
.px-index-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin-bottom:9px; }
.px-market-card { position:relative; overflow:hidden; min-height:76px; padding:10px 12px 8px; background:#fff; border:1px solid #e5eaf1; border-radius:10px; box-shadow:0 3px 12px rgba(15,23,42,.025); }
.px-market-title { color:#64748b; font-size:9px; font-weight:700; }
.px-market-value { margin-top:2px; color:#172033; font-size:17px; line-height:1.1; font-weight:800; }
.px-market-change { margin-top:3px; font-size:9px; font-weight:700; }
.px-up { color:#dc2626; } .px-down { color:#2563eb; } .px-flat { color:#94a3b8; }
.px-mini-chart { position:absolute; right:7px; bottom:9px; width:64px; height:36px; display:flex; align-items:flex-end; gap:2px; opacity:.8; }
.px-mini-chart i { flex:1; border-radius:2px 2px 0 0; background:#c9d7f0; }
.px-widget { background:#fff; border:1px solid #e5eaf1; border-radius:10px; box-shadow:0 3px 12px rgba(15,23,42,.025); overflow:hidden; }
.px-widget-head { display:flex; justify-content:space-between; align-items:center; padding:10px 12px 7px; border-bottom:1px solid #f0f3f7; }
.px-widget-title { color:#172033; font-size:11px; font-weight:800; }
.px-widget-sub { color:#9aa5b5; font-size:8px; }
.px-widget-body { padding:9px 12px 11px; }
.px-stock-hero { display:flex; align-items:flex-end; justify-content:space-between; }
.px-stock-name { color:#8a96a7; font-size:9px; }
.px-stock-price { margin-top:1px; color:#172033; font-size:22px; font-weight:850; letter-spacing:-.04em; }
.px-stock-meta { font-size:10px; font-weight:800; padding-bottom:3px; }
.px-watch-row { display:grid; grid-template-columns:1.2fr .9fr .45fr; gap:6px; align-items:center; min-height:27px; border-bottom:1px solid #f2f4f7; font-size:9px; }
.px-watch-row:last-child { border-bottom:0; }
.px-watch-name { color:#334155; font-weight:700; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.px-watch-price { color:#172033; text-align:right; font-variant-numeric:tabular-nums; }
.px-watch-change { color:#94a3b8; text-align:right; }
.px-flow-row { display:grid; grid-template-columns:1.1fr 1.4fr .5fr; gap:7px; align-items:center; min-height:25px; font-size:8px; color:#475569; }
.px-flow-row strong { text-align:right; font-size:8px; color:#334155; }
.px-flow-bar { height:5px; border-radius:99px; background:#edf1f6; overflow:hidden; }
.px-flow-fill { height:100%; border-radius:99px; background:#6f8fca; }
.px-heatmap { display:grid; grid-template-columns:repeat(4,1fr); gap:3px; }
.px-heat { min-height:45px; padding:6px; display:flex; flex-direction:column; justify-content:space-between; border-radius:5px; border:1px solid rgba(255,255,255,.45); color:#fff; }
.px-heat small { font-size:7px; opacity:.9; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.px-heat strong { font-size:10px; }
.px-heat.up3,.px-heat.up2,.px-heat.up1 { background:#d78383; }
.px-heat.down3,.px-heat.down2,.px-heat.down1 { background:#6d94d1; }
.px-heat.flat { background:#b8c1cd; }
.px-signal { display:flex; align-items:center; justify-content:space-between; min-height:25px; font-size:9px; }
.px-signal-main { color:#475569; font-weight:700; }
.px-signal-tag { color:#059669; background:#ecfdf5; border:1px solid #d1fae5; padding:2px 5px; border-radius:99px; font-size:7px; }
.px-score-row { margin:-3px 0 2px; }
.px-score { display:grid; grid-template-columns:55px 1fr 22px; align-items:center; gap:7px; font-size:7px; color:#94a3b8; }
.px-score:after { content:""; grid-column:2; grid-row:1; height:4px; border-radius:99px; background:linear-gradient(90deg,#5f86c6 70%,#e8edf4 70%); }
.px-score span { grid-column:1; } .px-score strong { grid-column:3; color:#64748b; text-align:right; font-size:8px; }
.px-news { padding:6px 0; border-bottom:1px solid #f1f3f6; }
.px-news:last-child { border-bottom:0; }
.px-news-date { color:#2563eb; font-size:7px; font-weight:700; }
.px-news-title { margin-top:2px; color:#475569; font-size:8px; line-height:1.45; }
.px-promo { min-height:86px; border-radius:9px; background:linear-gradient(145deg,#e8eef7,#f8fafc); border:1px solid #e0e7ef; padding:11px; margin-top:8px; color:#475569; }
.px-promo strong { display:block; color:#1e3a5f; font-size:10px; margin-bottom:3px; }
.px-promo span { font-size:8px; line-height:1.4; }
.px-dashboard-footer { margin-top:10px; color:#94a3b8; font-size:8px; text-align:right; }
@media (max-width:900px) {
  .px-index-grid { grid-template-columns:repeat(2,1fr); }
  .px-dashboard-head { flex-wrap:wrap; }
  .px-search-pill { order:3; max-width:none; width:100%; }
}


/* Reference dashboard v3 */
.stApp { background:#f7f9fc !important; }
.block-container { max-width: 1500px !important; padding-top: 3.6rem !important; padding-bottom: 2rem !important; }\n.ref-topline { padding-top: .35rem !important; min-height: 52px; }
section[data-testid="stSidebar"] { background:#f3eee5 !important; border-right:1px solid #e4ddd1 !important; }
section[data-testid="stSidebar"] > div { padding:1.4rem .8rem !important; }
section[data-testid="stSidebar"] .planx-brand { margin:6px 8px 32px !important; }
section[data-testid="stSidebar"] .planx-brand-mark { display:none !important; }
section[data-testid="stSidebar"] .planx-brand-title { font-family:Georgia,serif !important; font-size:34px !important; color:#3e2d17 !important; letter-spacing:-.04em !important; }
section[data-testid="stSidebar"] .planx-brand-sub { font-size:10px !important; letter-spacing:.18em !important; color:#3f3a33 !important; text-transform:uppercase; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] { gap:11px !important; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label { padding:13px 14px !important; border-radius:8px !important; color:#2f2b26 !important; }
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked) { background:#e8dcc5 !important; color:#2f2619 !important; box-shadow:inset 3px 0 #9a6b26 !important; }
.ref-topline { display:grid; grid-template-columns:auto minmax(300px,1fr) auto; align-items:center; gap:22px; margin-bottom:12px; }
.ref-brand-row { display:flex; align-items:baseline; gap:12px; white-space:nowrap; }
.ref-brand-main { font-family:Georgia,serif; font-size:38px; font-weight:700; color:#4a2f0c; letter-spacing:-.05em; }
.ref-brand-sub { font-size:11px; letter-spacing:.2em; font-weight:700; color:#2f3033; }
.ref-search { height:38px; display:flex; align-items:center; padding:0 14px; border:1px solid #e0e5ec; border-radius:9px; background:#fff; color:#8893a3; font-size:11px; max-width:430px; }
.ref-user-meta { color:#697586; font-size:10px; white-space:nowrap; }
.ref-index-grid { display:grid; grid-template-columns:repeat(5,1fr); gap:9px; margin-bottom:11px; }
.ref-index-card { position:relative; min-height:86px; padding:12px 14px; border:1px solid #e1e6ed; border-radius:10px; background:#fff; box-shadow:0 4px 14px rgba(15,23,42,.025); overflow:hidden; }
.ref-index-name { font-size:10px; font-weight:800; color:#111827; }
.ref-index-value { margin-top:2px; font-size:22px; font-weight:800; color:#111827; letter-spacing:-.035em; }
.ref-index-change { margin-top:4px; font-size:10px; font-weight:700; }
.ref-index-change.pos,.pos { color:#dc2626; }
.ref-index-change.neg,.neg { color:#2563eb; }
.ref-index-change.flat { color:#94a3b8; }
.ref-spark { position:absolute; right:10px; bottom:10px; width:98px; height:36px; }
.ref-spark polyline { stroke-width:2.3; vector-effect:non-scaling-stroke; }
.ref-spark.pos polyline { stroke:#ef4444; }
.ref-spark.neg polyline { stroke:#3b82f6; }
.ref-spark.empty { width:92px; height:1px; background:#dbe3ed; bottom:14px; }
.ref-slogan-row { display:flex; justify-content:space-between; align-items:center; margin:3px 2px 9px; color:#64748b; font-size:11px; }
.ref-tab-row { display:flex; align-items:center; justify-content:space-between; gap:10px; margin-bottom:10px; }
.ref-tab-row > div:first-child { margin-right:0; }
.ref-tab { padding:10px 19px; background:#f1f3f5; border-radius:8px; color:#475569; font-size:11px; font-weight:700; display:inline-block; margin-right:4px; }
.ref-tab.active { background:linear-gradient(180deg,#b88a49,#a8742b); color:#fff; }
.ref-flow-nav { margin-left:auto; display:flex; align-items:center; gap:9px; }
.ref-flow-nav span { min-width:92px; text-align:center; padding:9px 14px; border-radius:8px; background:#f2f4f6; color:#475569; font-size:10px; }
.ref-flow-nav span.active { background:#a67c45; color:#fff; }
.ref-flow-nav b { color:#a0a8b3; }
.ref-card { background:#fff; border:1px solid #e0e5ec; border-radius:10px; box-shadow:0 4px 14px rgba(15,23,42,.025); padding:13px 14px; height:100%; }
.ref-card-head { display:flex; align-items:center; justify-content:space-between; min-height:22px; margin-bottom:7px; }
.ref-card-head strong { font-size:12px; color:#182033; }
.ref-card-head span { font-size:8px; color:#7c8797; }
.pill { background:#e9f7ef; color:#15803d !important; border-radius:999px; padding:3px 7px; }
.score-card { min-height:244px; }
.ref-score-ring { width:110px; height:110px; border-radius:50%; margin:7px auto 8px; background:conic-gradient(#138f4a 0 78%,#e6e7e8 78% 100%); display:flex; align-items:center; justify-content:center; position:relative; }
.ref-score-ring:before { content:""; position:absolute; width:78px; height:78px; border-radius:50%; background:#fff; }
.ref-score-ring div { position:relative; z-index:1; font-size:30px; font-weight:800; color:#1f2937; }
.ref-score-ring small { display:block; font-size:8px; color:#94a3b8; text-align:center; margin-top:-2px; }
.ref-score-list { display:grid; grid-template-columns:1fr auto; gap:4px 9px; font-size:9px; color:#475569; }
.ref-score-list b { color:#111827; }
.signal-card { min-height:244px; position:relative; overflow:hidden; }
.signal-card h4 { margin:14px 0 10px; font-size:13px; color:#1f2937; }
.signal-card p { margin:0; color:#7a8696; font-size:9px; line-height:1.55; max-width:85%; }
.ref-bars { position:absolute; bottom:14px; left:14px; right:14px; height:54px; display:flex; align-items:flex-end; gap:6px; }
.ref-bars i { flex:1; border-radius:2px 2px 0 0; opacity:.9; }
.ref-stock-head { display:flex; justify-content:space-between; align-items:center; }
.ref-stock-head strong { font-size:19px; color:#111827; }
.ref-stock-head span { font-size:9px; color:#94a3b8; margin-left:5px; }
.ref-stock-time { font-size:9px; color:#94a3b8; }
.ref-stock-price { margin-top:18px; font-size:24px; font-weight:800; color:#111827; }
.ref-stock-price span { margin-left:8px; font-size:11px; }
.ref-heat-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:3px; }
.ref-heat { min-height:76px; border-radius:3px; padding:10px; display:flex; flex-direction:column; justify-content:space-between; }
.ref-heat strong { font-size:9px; }
.ref-heat span { font-size:13px; font-weight:700; }
.ref-heat.up { background:#78cf8a; color:#13351c; }
.ref-heat.down { background:#efb3b3; color:#551b1b; }
.ref-heat.flat { background:#e8edf2; color:#64748b; }
.ref-watch-row { display:grid; grid-template-columns:1.3fr .7fr .55fr; gap:8px; align-items:center; min-height:31px; border-bottom:1px solid #eef1f4; font-size:9px; }
.ref-watch-row:last-child { border-bottom:0; }
.ref-watch-row b,.ref-watch-row em { text-align:right; font-style:normal; }
.ref-empty { color:#94a3b8; font-size:9px; padding:18px 0; }
.ref-bottom-grid { display:grid; grid-template-columns:1.8fr 1fr; gap:10px; margin-top:10px; }
.ref-ai-list { margin:4px 0 0 18px; padding:0; color:#475569; font-size:9px; line-height:1.7; }
.ref-alert-row { display:grid; grid-template-columns:8px 1fr; gap:7px; align-items:center; min-height:24px; font-size:8px; color:#475569; }
.ref-alert-row i { width:6px; height:6px; border-radius:50%; background:#3b82f6; }
[data-testid="stLineChart"] { background:#fff; border-left:1px solid #e0e5ec; border-right:1px solid #e0e5ec; border-bottom:1px solid #e0e5ec; border-radius:0 0 10px 10px; padding:4px 8px 7px; }
@media (max-width:1100px) {
  .ref-index-grid { grid-template-columns:repeat(2,1fr); }
  .ref-topline { grid-template-columns:1fr; }
  .ref-search { max-width:none; }
  .ref-flow-nav { display:none; }
}


/* PlanX reference v4 */
.stApp{background:#f6faff !important;}
.block-container{max-width:1560px !important;padding-top:1.6rem !important;padding-left:1.1rem !important;padding-right:1.1rem !important;}
section[data-testid="stSidebar"]{background:#f7f9fc !important;border-right:1px solid #e6edf5 !important;}
section[data-testid="stSidebar"] > div{padding:1.2rem .85rem !important;}
section[data-testid="stSidebar"] .planx-brand{margin:0 8px 26px !important;}
section[data-testid="stSidebar"] .planx-brand-mark{display:flex !important;background:#2f80ed !important;width:34px !important;height:34px !important;border-radius:10px !important;}
section[data-testid="stSidebar"] .planx-brand-title{font-size:24px !important;color:#0f274f !important;font-family:inherit !important;font-weight:800 !important;}
section[data-testid="stSidebar"] .planx-brand-sub{font-size:10px !important;color:#61708a !important;letter-spacing:.01em !important;text-transform:none !important;}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"]{gap:5px !important;}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label{padding:11px 12px !important;border-radius:9px !important;color:#41536f !important;}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:has(input:checked){background:#e9f2ff !important;color:#1267d6 !important;box-shadow:none !important;}
.ref-topline{grid-template-columns:auto minmax(360px,1fr) auto !important;gap:24px !important;margin-bottom:16px !important;min-height:54px !important;}
.ref-brand-main{font-family:inherit !important;font-size:30px !important;color:#0f274f !important;font-weight:800 !important;}
.ref-brand-sub{font-size:15px !important;letter-spacing:0 !important;color:#0f274f !important;font-weight:700 !important;}
.ref-search{height:42px !important;border-radius:22px !important;background:#fff !important;font-size:12px !important;max-width:500px !important;box-shadow:0 4px 18px rgba(44,91,154,.06);}
.ref-user-meta{font-size:11px !important;color:#31486a !important;}
.ref-index-grid{grid-template-columns:repeat(5,1fr) !important;gap:12px !important;margin-bottom:16px !important;}
.ref-index-card{min-height:112px !important;padding:15px 16px !important;border-radius:12px !important;background:linear-gradient(180deg,#fff,#f9fbff) !important;}
.ref-index-name{font-size:11px !important;color:#101f38 !important;}
.ref-index-value{font-size:24px !important;color:#0c2145 !important;}
.ref-index-change{font-size:11px !important;}
.ref-spark{width:94px !important;height:42px !important;}
.ref-slogan-row,.ref-tab-row{display:none !important;}
.ref-card{border-radius:12px !important;border-color:#e3ebf5 !important;box-shadow:0 8px 24px rgba(45,87,145,.045) !important;}
.score-card,.signal-card{min-height:0 !important;}
.ref-score-ring{width:100px !important;height:100px !important;}
.ref-score-list{font-size:10px !important;}
.signal-card{padding:15px !important;}
.signal-card h4{font-size:14px !important;margin:10px 0 8px !important;}
.signal-card p{font-size:10px !important;}
.ref-bars{height:46px !important;}
.ref-stock-head strong{font-size:22px !important;color:#0d2345 !important;}
.ref-stock-price{font-size:29px !important;color:#ff1744 !important;margin-top:10px !important;}
.ref-heat-grid{grid-template-columns:repeat(4,1fr) !important;gap:2px !important;}
.ref-heat{min-height:82px !important;border-radius:4px !important;}
.ref-heat.up{background:linear-gradient(135deg,#e05861,#dc6d78) !important;color:#fff !important;}
.ref-heat.down{background:linear-gradient(135deg,#4097f0,#2f70d8) !important;color:#fff !important;}
.ref-watch-row{min-height:33px !important;font-size:10px !important;}
.ref-bottom-grid{grid-template-columns:1.6fr 1fr !important;}
.ref-ai-list{font-size:10px !important;}
.ref-alert-row{font-size:9px !important;}
[data-testid="stLineChart"]{border:1px solid #e5edf7 !important;border-radius:12px !important;}
@media (max-width:1200px){.ref-index-grid{grid-template-columns:repeat(2,1fr) !important;}.ref-topline{grid-template-columns:1fr !important;}}

</style>
""",
        unsafe_allow_html=True,
    )


def brand():
    st.markdown(
        """
<div class="planx-brand">
  <div class="planx-brand-mark">↗</div>
  <div>
    <div class="planx-brand-title">PlanX</div>
    <div class="planx-brand-sub">Stock Dashboard</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, eyebrow: str = "PLANX INVESTMENT OS"):
    st.markdown(
        f"""
<div class="planx-hero">
  <div class="planx-eyebrow">{html.escape(eyebrow)}</div>
  <h1>{html.escape(title)}</h1>
  <p>{html.escape(subtitle)}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def card(title: str, value: str, note: str = "", status: str = ""):
    status_html = f'<div class="planx-card-note">{html.escape(status)}</div>' if status else ""
    st.markdown(
        f"""
<div class="planx-card">
  <div class="planx-card-title">{html.escape(title)}</div>
  <div class="planx-card-value">{html.escape(value)}</div>
  <div class="planx-card-note">{html.escape(note)}</div>
  {status_html}
</div>
""",
        unsafe_allow_html=True,
    )


def empty_state(title: str, message: str):
    st.markdown(
        f"""
<div class="planx-empty">
  <strong style="color:#334155">{html.escape(title)}</strong><br>
  <span>{html.escape(message)}</span>
</div>
""",
        unsafe_allow_html=True,
    )


def source_badge(label: str, state: str = "wait"):
    cls = {"ok": "planx-status-ok", "bad": "planx-status-bad"}.get(state, "planx-status-wait")
    st.markdown(
        f'<span class="planx-source {cls}">{html.escape(label)}</span>',
        unsafe_allow_html=True,
    )
