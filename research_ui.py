import hashlib
import json
from datetime import date

import pandas as pd
import streamlit as st

from ui_v2 import hero, card
from automatic import brief
from bi_view import overview, detail, peers_chart
from chat_research import published, parse_bundle, trends, growth, request_text


def _sparkline_html(values):
    if not values:
        values = [1, 2, 1, 3, 2, 4, 3]
    lo, hi = min(values), max(values)
    span = hi - lo or 1
    bars = []
    for v in values[-18:]:
        h = 18 + int((v - lo) / span * 48)
        bars.append(f'<i style="height:{h}px"></i>')
    return '<div class="px-mini-chart">' + ''.join(bars) + '</div>'


def _market_card(name, value="연결 대기", change="실시간 데이터 연결 필요", tone="px-flat", values=None):
    st.markdown(
        f'''
<div class="px-market-card">
  <div class="px-market-title">{name}</div>
  <div class="px-market-value">{value}</div>
  <div class="px-market-change {tone}">{change}</div>
  {_sparkline_html(values or [])}
</div>
''',
        unsafe_allow_html=True,
    )


def _watch_rows(stocks):
    rows = []
    for stock in stocks[:8]:
        r = stock.get("_report") or {}
        prices = r.get("prices") or {}
        frame = prices.get("rows") or prices.get("data") or []
        last = None
        if frame and isinstance(frame, list):
            last = frame[-1].get("close") if isinstance(frame[-1], dict) else None
        value = f"{float(last):,.0f}원" if last is not None else "분석 필요"
        rows.append((stock.get("name", "종목"), value))
    return rows


def _heat_class(value):
    if value is None:
        return "flat"
    if value >= 3:
        return "up3"
    if value >= 1:
        return "up2"
    if value > 0:
        return "up1"
    if value <= -3:
        return "down3"
    if value <= -1:
        return "down2"
    if value < 0:
        return "down1"
    return "flat"


def render_research(store, state, sample_mode):
    # Main hero is intentionally a complete dashboard replacement.
    # Existing research/account data remains available through the other sidebar pages.
    stocks = []
    published_reports = published()
    for stock in state.get("stocks", []):
        r = published_reports.get(stock.get("code"))
        if not r and stock.get("code", "").startswith("pending-"):
            matches = [v for v in published_reports.values() if v.get("name", "").strip().casefold() == stock.get("name", "").strip().casefold()]
            if len(matches) == 1:
                r = matches[0]
        item = {**stock, "_report": r or {}}
        stocks.append(item)

    positions = st.session_state.get("account_snapshot", {}).get("positions", [])
    position_map = {p.get("code"): p for p in positions}

    # Header / hero
    st.markdown(
        '''
<div class="px-topbar">
  <div class="px-brand">
    <div class="px-mark">↗</div>
    <div>
      <div class="px-brand-name">PlanX <span style="font-weight:500;color:#64748b">Stock Dashboard</span></div>
      <div class="px-brand-sub">MARKET · PORTFOLIO · AI INSIGHT</div>
    </div>
  </div>
  <div class="px-top-date">데이터 기준일 · 공식자료/저장자료</div>
</div>
''',
        unsafe_allow_html=True,
    )
    hero("투자의 현재를 한눈에", "시장 흐름부터 관심종목, 수급, 업종, 투자 시그널까지 한 화면에서 확인합니다.", "PLANX · STOCK DASHBOARD")

    # Market index strip: never fabricate live index values.
    market_cols = st.columns(4, gap="small")
    for col, name in zip(market_cols, ["KOSPI", "KOSDAQ", "S&P 500", "NASDAQ"]):
        with col:
            _market_card(name)

    # Main grid
    left, middle, right = st.columns([1.55, 1.05, 1.0], gap="small")

    with left:
        selected_code = st.session_state.get("selected_code")
        selected = next((s for s in stocks if s.get("code") == selected_code), stocks[0] if stocks else None)
        if selected:
            r = selected.get("_report") or {}
            prices = r.get("prices")
            frame = None
            if prices and prices.get("rows"):
                try:
                    frame = pd.DataFrame(prices["rows"])
                    if "date" in frame.columns and "close" in frame.columns:
                        frame["date"] = pd.to_datetime(frame["date"])
                        frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
                        frame = frame.dropna(subset=["close"]).sort_values("date")
                except Exception:
                    frame = None
            price = frame["close"].iloc[-1] if frame is not None and not frame.empty else None
            prior = frame["close"].iloc[-2] if frame is not None and len(frame) > 1 else None
            change = ((price / prior) - 1) * 100 if price and prior else None
            st.markdown(
                f'''
<div class="px-widget">
  <div class="px-widget-head"><div class="px-widget-title">{selected.get("name","관심종목")}</div><div class="px-widget-sub">주가 흐름</div></div>
  <div class="px-widget-body">
    <div class="px-stock-hero">
      <div><div class="px-stock-name">최근 조사 가격</div><div class="px-stock-price">{f"{price:,.0f}원" if price is not None else "연결 대기"}</div></div>
      <div class="px-stock-meta {'px-up' if (change or 0)>0 else 'px-down' if (change or 0)<0 else 'px-flat'}">{f"{change:+.2f}%" if change is not None else "변동률 확인 필요"}</div>
    </div>
  </div>
</div>
''',
                unsafe_allow_html=True,
            )
            if frame is not None and not frame.empty:
                st.line_chart(frame.set_index("date")["close"], height=265, use_container_width=True)
            else:
                empty_state("가격 차트 대기", "조사 결과에 가격 자료가 들어오면 이 영역에 추세 차트가 표시됩니다.")
        else:
            empty_state("첫 관심종목을 담아보세요", "왼쪽 메뉴의 내 종목에서 기업을 추가하면 메인 대시보드가 채워집니다.")

        # Sector heat map uses only researched price changes when available.
        heat_items = []
        for s in stocks[:8]:
            r = s.get("_report") or {}
            trend = trends(r.get("prices"), r.get("as_of", date.today().isoformat()))[0] if r else {}
            text_change = trend.get("daily", "확인 필요")
            try:
                num = float(str(text_change).replace("%", "").replace("+", ""))
            except Exception:
                num = None
            heat_items.append((s.get("name", "종목"), num))
        cells = []
        for name, num in heat_items:
            label = "확인 필요" if num is None else f"{num:+.1f}%"
            cells.append(f'<div class="px-heat {_heat_class(num)}"><small>{name}</small><strong>{label}</strong></div>')
        if not cells:
            cells = ['<div class="px-heat flat"><small>데이터 대기</small><strong>연결 필요</strong></div>']
        st.markdown(
            f'''
<div class="px-widget" style="margin-top:8px">
  <div class="px-widget-head"><div class="px-widget-title">관심종목 흐름</div><div class="px-widget-sub">저장된 조사자료 기준</div></div>
  <div class="px-widget-body"><div class="px-heatmap">{''.join(cells)}</div></div>
</div>
''',
            unsafe_allow_html=True,
        )

    with middle:
        st.markdown(
            '''
<div class="px-widget">
  <div class="px-widget-head"><div class="px-widget-title">주요 관심종목</div><div class="px-widget-sub">내 목록</div></div>
  <div class="px-widget-body">
''',
            unsafe_allow_html=True,
        )
        if stocks:
            for name, value in _watch_rows(stocks):
                st.markdown(f'<div class="px-watch-row"><span class="px-watch-name">{name}</span><span class="px-watch-price">{value}</span><span class="px-watch-change">—</span></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="padding:16px 0;color:#64748b;font-size:11px">관심종목을 추가하면 이곳에 표시됩니다.</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

        st.markdown(
            '''
<div class="px-widget" style="margin-top:8px">
  <div class="px-widget-head"><div class="px-widget-title">외국인 · 기관 수급</div><div class="px-widget-sub">조사자료 기준</div></div>
  <div class="px-widget-body">
''',
            unsafe_allow_html=True,
        )
        for s in stocks[:6]:
            flow = (s.get("_report") or {}).get("flow") or {}
            foreign = flow.get("foreign")
            institution = flow.get("institution")
            total = (abs(float(foreign or 0)) + abs(float(institution or 0))) or 1
            f_pct = abs(float(foreign or 0)) / total * 100
            st.markdown(f'<div class="px-flow-row"><span>{s.get("name","종목")}</span><div class="px-flow-bar"><div class="px-flow-fill" style="width:{min(100,max(4,f_pct))}%"></div></div><strong>{f"{float(foreign):+,.0f}" if foreign is not None else "—"}</strong></div>', unsafe_allow_html=True)
        if not stocks:
            st.caption("수급 데이터가 있는 종목을 추가하면 표시됩니다.")
        st.markdown('</div></div>', unsafe_allow_html=True)

    with right:
        st.markdown(
            '''
<div class="px-widget">
  <div class="px-widget-head"><div class="px-widget-title">투자 시그널</div><div class="px-widget-sub">참고용 지표</div></div>
  <div class="px-widget-body">
''',
            unsafe_allow_html=True,
        )
        for label, key in [("MICRO", "financial"), ("GROWTH", "financial"), ("EARNINGS", "financial"), ("VALUATION", "valuation"), ("FLOW", "flow"), ("MOMENTUM", "prices")]:
            available = any((s.get("_report") or {}).get(key) for s in stocks)
            score = 75 if available else 0
            st.markdown(f'<div class="px-signal"><span class="px-signal-main">{label}</span><span class="px-signal-tag">{"데이터 있음" if available else "대기"}</span></div><div class="px-score-row"><div class="px-score"><span>상태</span><strong>{score}</strong></div></div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

        st.markdown(
            '''
<div class="px-widget" style="margin-top:8px">
  <div class="px-widget-head"><div class="px-widget-title">AI 분석 요약</div><div class="px-widget-sub">근거 기반</div></div>
  <div class="px-widget-body">
''',
            unsafe_allow_html=True,
        )
        summaries = []
        for s in stocks[:3]:
            r = s.get("_report") or {}
            summary = r.get("summary")
            if summary and summary.get("text"):
                summaries.append((s.get("name","종목"), summary["text"]))
        if summaries:
            for name, summary in summaries:
                st.markdown(f'<div class="px-news"><div class="px-news-date">{name}</div><div class="px-news-title">{summary[:140]}</div></div>', unsafe_allow_html=True)
        else:
            st.caption("조사 결과가 쌓이면 AI/핵심 요약 영역에 표시됩니다.")
        st.markdown('</div></div>', unsafe_allow_html=True)

    # Lower controls retain the original workflow without returning to the old hero page.
    st.markdown("### 종목 추가 · 상세 분석")
    if not sample_mode:
        with st.expander("＋ 관심종목 추가", expanded=not stocks):
            with st.form("research_manual"):
                name = st.text_input("종목명", placeholder="예: 삼성전자")
                code = st.text_input("종목코드 · 선택", max_chars=6)
                if st.form_submit_button("내 목록에 추가", type="primary"):
                    import re
                    if not name.strip() or (code and not re.fullmatch(r"[0-9]{6}", code)):
                        st.error("종목명과 숫자 6자리 코드를 확인하세요. 코드는 생략할 수 있습니다.")
                    else:
                        known = next((s for s in state.get("stocks", []) if s["name"].strip().casefold() == name.strip().casefold()), {})
                        identity = known.get("code") or code or "pending-" + hashlib.sha256(name.strip().casefold().encode()).hexdigest()[:16]
                        store.save_stock({"code": identity, "name": name.strip(), "kind": known.get("kind", "관심")})
                        st.rerun()

    if stocks:
        options = {s["code"]: s for s in stocks}
        selected = st.selectbox("자세히 볼 종목", list(options), format_func=lambda k: options[k]["name"], key="research_selected")
        selected_stock = options[selected]
        r = selected_stock.get("_report") or {}
        if r:
            detail(r)
            tabs = st.tabs(["기업", "실적", "주가·수급", "가격 확인"])
            with tabs[0]:
                entry = r.get("business")
                if entry:
                    st.write(entry["text"])
                    if entry.get("source"): st.link_button("원문 근거", entry["source"])
            with tabs[1]:
                f = r.get("financial")
                if f:
                    st.dataframe([{"항목":"매출","이번 누적":f["revenue"],"전년 누적":f["prior_revenue"],"변화":growth(f["revenue"],f["prior_revenue"])},
                                  {"항목":"영업이익","이번 누적":f["operating_profit"],"전년 누적":f["prior_operating_profit"],"변화":growth(f["operating_profit"],f["prior_operating_profit"])}], hide_index=True, use_container_width=True)
            with tabs[2]:
                flow = r.get("flow")
                if flow:
                    a,b = st.columns(2)
                    a.metric("외국인 순매수", f"{flow['foreign']:+,.0f}")
                    b.metric("기관 순매수", f"{flow['institution']:+,.0f}")
                if r.get("prices", {}).get("source"): st.link_button("가격 자료 근거", r["prices"]["source"])
            with tabs[3]:
                v = r.get("valuation")
                if v:
                    a,b,c = st.columns(3)
                    a.metric("낮은 참고가", f"{v['low']:,.0f}원")
                    b.metric("기본 참고가", f"{v['base']:,.0f}원")
                    c.metric("높은 참고가", f"{v['high']:,.0f}원")
        else:
            st.info("이 종목의 조사 결과가 아직 없습니다. 조사 요청문을 대화창에 보내면 결과를 채울 수 있습니다.")

    with st.expander("조사 요청 · 최신 내용으로 업데이트"):
        st.write("종목을 추가한 뒤 아래 요청문을 대화창에 보내면 조사 결과를 반영할 수 있습니다.")
        st.code(request_text(stocks), language=None)
