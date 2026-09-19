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
    <div class="ref-brand-sub">STOCK INTELLIGENCE</div>
  </div>
  <div class="ref-search">⌕&nbsp;&nbsp; 종목명 또는 키워드를 검색하세요.</div>
  <div class="ref-user-meta">시장 데이터 샘플 · 사용자</div>
</div>
""",
        unsafe_allow_html=True,
    )

    # market strip - real values only where researched data exists
    cards = []
    if selected_report:
        val, chg = _latest_price(selected_report)
        vals = _trend_values(selected_report)
        cards.append(_index_card("선택 종목", val, chg, vals))
    cards.extend(
        [
            _index_card("KOSPI", None, None, []),
            _index_card("KOSDAQ", None, None, []),
            _index_card("USD/KRW", None, None, []),
            _index_card("WTI", None, None, []),
        ]
    )
    st.markdown('<div class="ref-index-grid">' + "".join(cards[:5]) + "</div>", unsafe_allow_html=True)

    st.markdown(
        """
<div class="ref-slogan-row">
  <div>더 깊은 분석이, 더 나은 투자를 만듭니다. PlanX가 시장의 흐름을 함께 읽어드립니다.</div>
  <div>공식자료 · 저장자료 기준</div>
</div>
<div class="ref-tab-row">
  <div class="ref-tab active">오늘의 투자판단</div>
  <div class="ref-tab">관심종목분석</div>
  <div class="ref-flow-nav"><span>시장</span><b>›</b><span>산업</span><b>›</b><span>기업</span><b>›</b><span class="active">투자판단</span></div>
</div>
""",
        unsafe_allow_html=True,
    )

    score = _score_from_data(stocks)
    score_label = "데이터 축적중" if score < 40 else "중립" if score < 70 else "긍정"

    c1, c2, c3, c4, c5 = st.columns([1.0, 1.1, 1.1, 1.1, 1.1], gap="small")
    with c1:
        st.markdown(
            f"""
<div class="ref-card score-card">
  <div class="ref-card-head"><strong>종합 투자점수</strong></div>
  <div class="ref-score-ring"><div>{score}<small>/100</small></div></div>
  <div class="ref-score-list">
    <span>데이터 완성도</span><b>{score}</b>
    <span>현재 상태</span><b>{score_label}</b>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    signal_specs = [
        ("◎ 매크로", "안정적인 흐름 지속", "금리와 유동성 방향을 확인합니다.", "#94a3b8"),
        ("◉ 성장산업", "AI·반도체 수요 확인", "산업 성장과 투자 기회를 함께 봅니다.", "#16a34a"),
        ("◼ 수출·수주", "수출 개선세 점검", "매출로 전환되는지 확인합니다.", "#16a34a"),
        ("▥ 실적 성장", "이익 성장 확인", "매출보다 영업이익의 속도를 봅니다.", "#16a34a"),
    ]
    for col, spec in zip([c2, c3, c4, c5], signal_specs):
        title, headline, desc, color = spec
        with col:
            st.markdown(
                f"""
<div class="ref-card signal-card">
  <div class="ref-card-head"><strong>{title}</strong><span class="pill">{"긍정" if color == "#16a34a" else "중립"}</span></div>
  <h4>{headline}</h4>
  <p>{desc}</p>
  <div class="ref-bars">
    <i style="height:18px;background:{color}"></i><i style="height:24px;background:{color}"></i>
    <i style="height:31px;background:{color}"></i><i style="height:38px;background:{color}"></i><i style="height:46px;background:{color}"></i>
  </div>
</div>
""",
                unsafe_allow_html=True,
            )

    left, mid, right = st.columns([2.1, 1.0, 1.0], gap="small")

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
                        st.line_chart(frame.set_index("date")["close"], height=240, use_container_width=True)
                except Exception:
                    st.info("차트 데이터를 불러오지 못했습니다.")
            else:
                st.info("가격 차트는 조사 데이터가 연결되면 표시됩니다.")
        else:
            st.info("관심종목을 추가하면 메인 차트가 표시됩니다.")

    with mid:
        heat_items = []
        for s in stocks[:9]:
            r = s.get("_report") or {}
            t = trends(r.get("prices"), r.get("as_of", date.today().isoformat()))[0] if r else {}
            try:
                num = float(str(t.get("daily", "")).replace("%", "").replace("+", ""))
            except Exception:
                num = None
            heat_items.append((s.get("name", "종목"), num))
        if not heat_items:
            heat_items = [("데이터 대기", None)]
        heat_html = ""
        for name, num in heat_items:
            cls = "flat" if num is None else "up" if num >= 0 else "down"
            label = "대기" if num is None else f"{num:+.1f}%"
            heat_html += f'<div class="ref-heat {cls}"><strong>{name}</strong><span>{label}</span></div>'
        st.markdown(
            f"""
<div class="ref-card">
  <div class="ref-card-head"><strong>섹터별 등락률</strong><span>저장자료</span></div>
  <div class="ref-heat-grid">{heat_html}</div>
</div>
""",
            unsafe_allow_html=True,
        )

    with right:
        rows = _watchlist_rows(stocks)
        body = ""
        if rows:
            for row in rows:
                p = "분석 필요" if row["price"] is None else f'{row["price"]:,.0f}'
                ch = "—" if row["change"] is None else f'{row["change"]:+.2f}%'
                cls = "pos" if (row["change"] or 0) >= 0 else "neg"
                body += f'<div class="ref-watch-row"><span>★ {row["name"]}</span><b>{p}</b><em class="{cls}">{ch}</em></div>'
        else:
            body = '<div class="ref-empty">관심종목을 추가하세요.</div>'
        st.markdown(
            f"""
<div class="ref-card">
  <div class="ref-card-head"><strong>관심종목</strong><span>더보기 ›</span></div>
  <div>{body}</div>
</div>
""",
            unsafe_allow_html=True,
        )

    ai_texts = []
    for s in stocks[:3]:
        summary = (s.get("_report") or {}).get("summary")
        if summary and summary.get("text"):
            ai_texts.append(summary.get("text"))
    ai_html = "".join(f"<li>{x[:160]}</li>" for x in ai_texts) or "<li>조사 결과가 쌓이면 핵심 분석이 표시됩니다.</li>"
    st.markdown(
        f"""
<div class="ref-bottom-grid">
  <div class="ref-card">
    <div class="ref-card-head"><strong>AI 분석 요약</strong><span>더보기 ›</span></div>
    <ul class="ref-ai-list">{ai_html}</ul>
  </div>
  <div class="ref-card">
    <div class="ref-card-head"><strong>실시간 알림</strong><span>저장자료 기준</span></div>
    <div class="ref-alert-row"><i></i><span>관심종목과 조사 결과의 최신 상태를 확인하세요.</span></div>
    <div class="ref-alert-row"><i></i><span>시장 데이터 API 연결 시 이 영역이 확장됩니다.</span></div>
  </div>
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
