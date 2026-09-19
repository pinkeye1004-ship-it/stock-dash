import hashlib
from datetime import date

import pandas as pd
import streamlit as st

from bi_view import detail
from chat_research import published, trends, growth, request_text


def _latest_price(report):
    prices = (report or {}).get("prices") or {}
    rows = prices.get("rows") or prices.get("data") or []
    if not rows:
        return None, None
    try:
        frame = pd.DataFrame(rows)
        if "date" in frame.columns:
            frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
        frame["close"] = pd.to_numeric(frame.get("close"), errors="coerce")
        frame = frame.dropna(subset=["close"])
        if "date" in frame.columns:
            frame = frame.sort_values("date")
        if frame.empty:
            return None, None
        latest = float(frame["close"].iloc[-1])
        prev = float(frame["close"].iloc[-2]) if len(frame) > 1 else None
        change = ((latest / prev) - 1) * 100 if prev else None
        return latest, change
    except Exception:
        return None, None


def _trend_values(report):
    prices = (report or {}).get("prices") or {}
    rows = prices.get("rows") or prices.get("data") or []
    values = []
    for row in rows[-30:]:
        if isinstance(row, dict):
            try:
                values.append(float(row.get("close")))
            except Exception:
                pass
    return values


def _spark_svg(values, positive=True):
    if len(values) < 2:
        return '<div class="ref-spark empty"></div>'
    lo, hi = min(values), max(values)
    span = hi - lo or 1
    pts = []
    for i, v in enumerate(values):
        x = 4 + (i / (len(values) - 1)) * 92
        y = 30 - ((v - lo) / span) * 24
        pts.append(f"{x:.1f},{y:.1f}")
    cls = "pos" if positive else "neg"
    return f'<svg class="ref-spark {cls}" viewBox="0 0 100 34" preserveAspectRatio="none"><polyline points="{" ".join(pts)}" fill="none"/></svg>'


def _index_card(name, value, change=None, values=None):
    tone = "flat"
    if change is not None:
        tone = "pos" if change >= 0 else "neg"
    change_text = "연결 대기" if change is None else f"{change:+.2f}%"
    value_text = "연결 대기" if value is None else f"{value:,.2f}"
    return f"""
<div class="ref-index-card">
  <div class="ref-index-name">{name}</div>
  <div class="ref-index-value">{value_text}</div>
  <div class="ref-index-change {tone}">{change_text}</div>
  {_spark_svg(values or [], change is None or change >= 0)}
</div>
"""


def _watchlist_rows(stocks):
    rows = []
    for s in stocks[:8]:
        price, change = _latest_price(s.get("_report"))
        rows.append(
            {
                "name": s.get("name", "종목"),
                "price": price,
                "change": change,
            }
        )
    return rows


def _score_from_data(stocks):
    available = 0
    total = 5
    keys = ["financial", "valuation", "flow", "prices", "summary"]
    for key in keys:
        if any((s.get("_report") or {}).get(key) for s in stocks):
            available += 1
    return round((available / total) * 100) if total else 0


def render_research(store, state, sample_mode):
    stocks = []
    reports = published()
    for stock in state.get("stocks", []):
        report = reports.get(stock.get("code"))
        if not report and stock.get("code", "").startswith("pending-"):
            matches = [
                v
                for v in reports.values()
                if v.get("name", "").strip().casefold() == stock.get("name", "").strip().casefold()
            ]
            if len(matches) == 1:
                report = matches[0]
        stocks.append({**stock, "_report": report or {}})

    selected_code = st.session_state.get("selected_code")
    selected = next((s for s in stocks if s.get("code") == selected_code), stocks[0] if stocks else None)
    selected_report = selected.get("_report") if selected else {}
    selected_price, selected_change = _latest_price(selected_report)

    st.markdown(
        """
<div class="ref-topline">
  <div class="ref-brand-row">
    <div class="ref-brand-main">PlanX</div>
    <div class="ref-brand-sub">Stock Dashboard</div>
  </div>
  <div class="ref-search">⌕&nbsp;&nbsp; 종목명 또는 키워드를 검색하세요.</div>
  <div class="ref-user-meta">2026년 9월 19일 · 시장 데이터</div>
</div>
""",
        unsafe_allow_html=True,
    )

    # Market strip mirrors the supplied reference. Missing market feeds stay explicit.
    cards = [
        _index_card("KOSPI", None, None, []),
        _index_card("KOSDAQ", None, None, []),
        _index_card("S&P 500", None, None, []),
        _index_card("NASDAQ", None, None, []),
    ]
    promo = """
<div class="ref-index-card ref-promo-card">
  <div class="ref-promo-title">좋은 기업이<br>더 좋은 내일을 만듭니다.</div>
  <div class="ref-promo-sub">Better Investment,<br>A Brighter Tomorrow.</div>
</div>
"""
    st.markdown('<div class="ref-index-grid">' + "".join(cards) + promo + "</div>", unsafe_allow_html=True)

    # Main dashboard: large stock chart, watchlist and investor flow.
    left, middle, right = st.columns([1.75, 1.0, 1.0], gap="small")

    with left:
        if selected:
            st.markdown(
                f"""
<div class="ref-card stock-card">
  <div class="ref-stock-head">
    <div><strong>{selected.get("name","관심종목")}</strong> <span>{selected.get("code","")}</span></div>
    <div class="ref-stock-time">저장된 조사자료 기준</div>
  </div>
  <div class="ref-stock-price">{f"{selected_price:,.0f}원" if selected_price is not None else "연결 대기"}
    <span class="{"pos" if (selected_change or 0)>=0 else "neg"}">{f"{selected_change:+.2f}%" if selected_change is not None else "변동률 대기"}</span>
  </div>
  <div class="ref-period-tabs"><span>1일</span><span>1주</span><span>1개월</span><span class="active">3개월</span><span>6개월</span><span>1년</span><span>3년</span><span>5년</span></div>
</div>
""",
                unsafe_allow_html=True,
            )
            prices = selected_report.get("prices") or {}
            rows = prices.get("rows") or prices.get("data") or []
            if rows:
                try:
                    frame = pd.DataFrame(rows)
                    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
                    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
                    frame = frame.dropna(subset=["date", "close"]).sort_values("date")
                    if not frame.empty:
                        st.line_chart(frame.set_index("date")["close"], height=300, use_container_width=True)
                except Exception:
                    st.info("차트 데이터를 불러오지 못했습니다.")
            else:
                st.info("관심종목의 가격 데이터가 연결되면 메인 차트가 표시됩니다.")
        else:
            st.info("관심종목을 추가하면 메인 차트가 표시됩니다.")

    with middle:
        rows = _watchlist_rows(stocks)
        body = ""
        if rows:
            for row in rows:
                p = "분석 필요" if row["price"] is None else f'{row["price"]:,.0f}'
                ch = "—" if row["change"] is None else f'{row["change"]:+.2f}%'
                cls = "pos" if (row["change"] or 0) >= 0 else "neg"
                body += f'<div class="ref-watch-row"><span>{row["name"]}</span><b>{p}</b><em class="{cls}">{ch}</em><small>매수</small></div>'
        else:
            body = '<div class="ref-empty">관심종목을 추가하세요.</div>'
        st.markdown(
            f"""
<div class="ref-card ref-watch-card">
  <div class="ref-card-head"><strong>주요 관심종목</strong><span>＋ 종목추가</span></div>
  <div class="ref-watch-head"><span>종목명</span><span>현재가</span><span>등락률</span><span>신호</span></div>
  <div>{body}</div>
</div>
""",
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
<div class="ref-card ref-flow-card">
  <div class="ref-card-head"><strong>외국인/기관 수급</strong><span>실시간 ›</span></div>
  <div class="ref-flow-tabs"><span class="active">KOSPI</span><span>KOSDAQ</span><span>선물</span><span>옵션</span></div>
  <div class="ref-flow-metrics"><div><small>외국인</small><b class="pos">데이터 대기</b></div><div><small>기관</small><b class="pos">데이터 대기</b></div><div><small>개인</small><b class="neg">데이터 대기</b></div></div>
  <div class="ref-flow-bars">
    <i style="height:20%"></i><i style="height:36%"></i><i class="neg" style="height:45%"></i><i style="height:55%"></i><i style="height:75%"></i><i style="height:35%"></i><i class="neg" style="height:60%"></i><i style="height:48%"></i><i style="height:72%"></i>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    lower1, lower2, lower3 = st.columns([1.35, 1.05, 1.05], gap="small")

    with lower1:
        heat_items = []
        for s in stocks[:12]:
            r = s.get("_report") or {}
            t = trends(r.get("prices"), r.get("as_of", date.today().isoformat()))[0] if r else {}
            try:
                num = float(str(t.get("daily", "")).replace("%", "").replace("+", ""))
            except Exception:
                num = None
            heat_items.append((s.get("name", "종목"), num))
        labels = ["전기·전자","반도체","자동차","2차전지","바이오","금융","화학","철강","기계·장비","건설","유통","통신"]
        while len(heat_items) < 12:
            heat_items.append((labels[len(heat_items)], None))
        heat_html = ""
        for name, num in heat_items[:12]:
            cls = "flat" if num is None else "up" if num >= 0 else "down"
            label = "대기" if num is None else f"{num:+.2f}%"
            heat_html += f'<div class="ref-heat {cls}"><strong>{name}</strong><span>{label}</span></div>'
        st.markdown(
            f"""
<div class="ref-card">
  <div class="ref-card-head"><strong>업종별 등락 현황</strong><span>더보기 ›</span></div>
  <div class="ref-heat-grid ref-heat-grid-4">{heat_html}</div>
</div>
""",
            unsafe_allow_html=True,
        )

    with lower2:
        st.markdown(
            """
<div class="ref-card">
  <div class="ref-card-head"><strong>투자 스타일</strong><span>PlanX AI 분석결과</span></div>
  <div class="ref-style-list">
    <div><span>MACRO</span><i><b style="width:70%"></b></i><em>70</em><small>강세</small></div>
    <div><span>GROWTH</span><i><b style="width:88%"></b></i><em>88</em><small>매우 강세</small></div>
    <div><span>SIGNAL</span><i><b style="width:65%"></b></i><em>65</em><small>강세</small></div>
    <div><span>EARNINGS</span><i><b style="width:80%"></b></i><em>80</em><small>강세</small></div>
    <div><span>VALUATION</span><i><b style="width:60%"></b></i><em>60</em><small>중립</small></div>
    <div><span>FLOW</span><i><b style="width:75%"></b></i><em>75</em><small>강세</small></div>
    <div><span>DECISION</span><i><b style="width:78%"></b></i><em>78</em><small>검토</small></div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    ai_texts = []
    for s in stocks[:4]:
        summary = (s.get("_report") or {}).get("summary")
        if summary and summary.get("text"):
            ai_texts.append(summary.get("text"))
    ai_html = "".join(f"<li>{x[:120]}</li>" for x in ai_texts) or "<li>조사 결과가 쌓이면 핵심 분석이 표시됩니다.</li>"
    with lower3:
        st.markdown(
            f"""
<div class="ref-card ref-ai-card">
  <div class="ref-card-head"><strong>AI 분석 요약</strong><span>더보기 ›</span></div>
  <ul class="ref-ai-list">{ai_html}</ul>
</div>
<div class="ref-card ref-alert-card" style="margin-top:10px">
  <div class="ref-card-head"><strong>실시간 알림</strong><span>전체보기 ›</span></div>
  <div class="ref-alert-row"><i></i><span>관심종목 최신 조사 상태를 확인하세요.</span></div>
  <div class="ref-alert-row"><i></i><span>시장 데이터 API 연결 시 알림이 확장됩니다.</span></div>
  <div class="ref-alert-row"><i></i><span>공시·수급 변화가 있으면 이 영역에 표시됩니다.</span></div>
</div>
""",
            unsafe_allow_html=True,
        )

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
        selected_id = st.selectbox("자세히 볼 종목", list(options), format_func=lambda k: options[k]["name"], key="research_selected")
        r = options[selected_id].get("_report") or {}
        if r:
            detail(r)
            tabs = st.tabs(["기업", "실적", "주가·수급", "가격 확인"])
            with tabs[0]:
                entry = r.get("business")
                if entry:
                    st.write(entry["text"])
                    if entry.get("source"):
                        st.link_button("원문 근거", entry["source"])
            with tabs[1]:
                f = r.get("financial")
                if f:
                    st.dataframe(
                        [
                            {"항목": "매출", "이번 누적": f["revenue"], "전년 누적": f["prior_revenue"], "변화": growth(f["revenue"], f["prior_revenue"])},
                            {"항목": "영업이익", "이번 누적": f["operating_profit"], "전년 누적": f["prior_operating_profit"], "변화": growth(f["operating_profit"], f["prior_operating_profit"])},
                        ],
                        hide_index=True,
                        use_container_width=True,
                    )
            with tabs[2]:
                flow = r.get("flow")
                if flow:
                    a, b = st.columns(2)
                    a.metric("외국인 순매수", f"{flow['foreign']:+,.0f}")
                    b.metric("기관 순매수", f"{flow['institution']:+,.0f}")
            with tabs[3]:
                v = r.get("valuation")
                if v:
                    a, b, c = st.columns(3)
                    a.metric("낮은 참고가", f"{v['low']:,.0f}원")
                    b.metric("기본 참고가", f"{v['base']:,.0f}원")
                    c.metric("높은 참고가", f"{v['high']:,.0f}원")
        else:
            st.info("이 종목의 조사 결과가 아직 없습니다.")

    with st.expander("조사 요청 · 최신 내용으로 업데이트"):
        st.code(request_text(stocks), language=None)
