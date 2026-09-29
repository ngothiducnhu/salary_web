from html import escape
from pathlib import Path
import re
import numpy as np
import pandas as pd
import streamlit as st
import analysis as an
import charts as ch
import insights

st.set_page_config(
    page_title="Phân tích lương nhân viên",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "data" / "Employers_data.csv"
PLOT_CONFIG = {"displayModeBar": False, "responsive": True}


def vn(value: float, decimals: int = 0) -> str:
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def vn_p(p: float) -> str:
    return "< 0,001" if p < 0.001 else vn(p, 3)


# ==========================================================================
# CSS
# ==========================================================================
def inject_css() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&display=swap');

html, body, .stApp, .stApp p, .stApp label, .stApp li, .stApp h1, .stApp h2,
.stApp h3, .stApp h4, .stApp input, .stApp button, .stApp td, .stApp th {
    font-family: 'Be Vietnam Pro', 'Segoe UI', Arial, sans-serif;
}
.stApp { background: #F1F6FC; }
.block-container {
    padding: 0.5rem 3rem 3rem;
    max-width: none;
}
header[data-testid="stHeader"] { background: transparent; }

/* Sidebar theo mẫu: logo cột, menu xanh và bộ lọc xanh xám. */
section[data-testid="stSidebar"] {
    background: #F1F6FC;
    border-right: 0;
    min-width: 258px;
    width: 258px;
}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    position: relative;
    min-height: calc(100vh - 1rem);
    margin: 1rem 0 0 1rem;
    padding: 1.25rem .9rem 1.5rem;
    background: #FFFFFF;
    border: 1px solid #E3ECF8;
    border-bottom: 0;
    border-radius: 15px 15px 0 0;
    box-shadow: 0 8px 26px rgba(65, 101, 153, .08);
    overflow-x: clip;
}
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
    position: relative;
    z-index: 2;
}
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
    position: relative;
    margin-top: -3.5rem;
}
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button,
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] button[kind="header"] {
    color: #5C78A5;
}
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] {
    transform: translateY(-1.1rem) !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button {
    transform: translateY(-5px);
}
.brand { display: flex; align-items: center; gap: .85rem; margin: .1rem 0 2rem; }
.brand-icon { width: 52px; height: 52px; flex: none; display: flex; align-items: center;
              justify-content: center; background: #EAF2FF; border-radius: 12px; }
.brand-bars { width: 28px; height: 28px; display: flex; align-items: end; gap: 2px; flex: none; }
.brand-bars span { width: 4px; border-radius: 2px 2px 0 0; background: #4B82F1;
                   box-shadow: 0 0 10px #5D9BFF55; }
.brand-bars span:nth-child(1) { height: 11px; }
.brand-bars span:nth-child(2) { height: 18px; }
.brand-bars span:nth-child(3) { height: 15px; }
.brand-bars span:nth-child(4) { height: 24px; }
.brand-bars span:nth-child(5) { height: 20px; }
.brand-text { display: flex; flex-direction: column; min-width: 0;
                            padding-left: 0; }
.brand-title { font-weight: 700; font-size: 1.05rem; line-height: 1.3; color: #19315C;
               letter-spacing: .02em; white-space: nowrap; }
.brand-sub { font-size: .76rem; line-height: 1.4; color: #5C78A5; margin-top: .25rem; }
section[data-testid="stSidebar"] [data-testid="stPageLink"] { margin-bottom: .18rem; }
section[data-testid="stSidebar"] [data-testid="stPageLink"] a {
    min-height: 39px; border-radius: 7px; padding: .52rem .7rem;
    color: #1B315A !important; font-size: .84rem; font-weight: 600;
    opacity: 1 !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a * {
    color: inherit !important; opacity: 1 !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover { background: #EAF2FF; color: #2868DF !important; }
}
section[data-testid="stSidebar"] [data-testid="stPageLink"] a svg { color: currentColor; }
.side-divider { height: 1px; background: #E2EAF5; margin: 1.25rem .2rem 2rem; }
.side-label { display: flex; align-items: center; gap: .45rem; font-size: .92rem;
             color: #1B315A; margin: 0 0 .65rem; }
.side-label svg { opacity: .8; }
section[data-testid="stSidebar"] [data-testid="stMultiSelect"] { margin-bottom: .35rem; }
section[data-testid="stSidebar"] [data-testid="stMultiSelect"] label {
    color: #1B315A; font-size: .78rem; font-weight: 500;
}
section[data-testid="stSidebar"] [data-testid="stMultiSelect"] label * {
    color: inherit !important;
}
section[data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
    min-height: 38px; background: #F7FAFF; border: 1px solid #C9D9F0;
    border-radius: 7px; box-shadow: none;
}
section[data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="select"] > div:hover {
    border-color: #78A6F2; background: #FFFFFF;
}
section[data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="select"] * {
    color: #1B315A;
}
section[data-testid="stSidebar"] [data-testid="stMultiSelect"] input::placeholder {
    color: #4A6692; opacity: 1;
}
section[data-testid="stSidebar"] [data-testid="stMultiSelect"] [data-baseweb="tag"] {
    background: #DDEAFF; color: #2868DF;
}
section[data-testid="stSidebar"] [data-baseweb="menu"] [role="option"]:first-child {
    font-size: 0;
}
section[data-testid="stSidebar"] [data-baseweb="menu"] [role="option"]:first-child::after {
    content: "Chọn tất cả";
    font-size: .85rem;
    color: #1B315A;
}
@media (max-width: 700px) {
    section[data-testid="stSidebar"] { width: min(258px, 88vw); min-width: 0; }
}

/* Tiêu đề trang */
.page-head { display: flex; align-items: center; min-height: 68px; margin-bottom: 1rem; }
.page-head h1 { font-size: 1.55rem; line-height: 1.3; font-weight: 500;
                color: #0F1E3D; margin: 0; padding: 0; }
.page-head p { color: #64748B; margin: .2rem 0 0; font-size: .88rem; line-height: 1.5; }
@media (max-width: 700px) {
    .page-head { align-items: flex-start; }
    .page-head h1 { font-size: 1.35rem; }
}
/* Thẻ KPI */
.kpi { background: #FFFFFF; border: 1px solid #E3E8F0; border-radius: 12px;
       padding: 1rem 1.1rem; display: flex; gap: .85rem; align-items: center; height: 100%; }
.kpi-icon { width: 44px; height: 44px; border-radius: 50%; display: grid;
            place-items: center; flex: none; }
.kpi-label { color: #475569; font-size: .84rem; }
.kpi-value { color: #0F1E3D; font-size: 1.45rem; font-weight: 700; line-height: 1.3;
             font-variant-numeric: tabular-nums; }

/* Khung chart: st.container(border=True, key="card_...") */
[class*="st-key-card_"] { background: #FFFFFF; border-radius: 12px;
                          border: 1px solid #E2EAF5 !important;
                          box-shadow: 0 7px 22px rgba(65, 101, 153, .075);
                          overflow: visible; }
.card-title { font-weight: 600; font-size: .95rem; color: #1B315A;
              margin-bottom: .1rem; white-space: normal; overflow-wrap: anywhere; }
.card-note { font-size: .8rem; color: #7185A4; margin-bottom: .2rem; }
.chart-heading { display: flex; align-items: flex-start; gap: .5rem;
                 width: 100%; position: relative; z-index: 10; }
.chart-heading .card-title { flex: 1; min-width: 0; line-height: 1.45; }
.chart-insight-icon { display: inline-grid; place-items: center; position: relative;
                      flex: none; width: 28px; height: 28px; border-radius: 50%;
                      background: #EEF3FF; font-size: 17px; cursor: help; }
.chart-insight-icon:hover, .chart-insight-icon:focus-visible { background: #DBEAFE; }
.chart-insight-icon:focus-visible { outline: 2px solid #2563EB; outline-offset: 2px; }
.chart-insight-tooltip { position: absolute; top: calc(100% + 8px); right: 0;
                         width: min(360px, calc(100vw - 32px)); box-sizing: border-box;
                         padding: .85rem 1rem; border-radius: 10px; background: #0F1E3D;
                         box-shadow: 0 12px 30px #0F1E3D30; color: #FFFFFF;
                         font-size: .88rem; font-weight: 400; line-height: 1.55;
                         text-align: left; visibility: hidden; opacity: 0;
                         pointer-events: none; z-index: 100; }
.chart-insight-icon:hover .chart-insight-tooltip,
.chart-insight-icon:focus .chart-insight-tooltip { visibility: visible; opacity: 1; }
.chart-insight-tooltip strong { color: #FFFFFF; font-weight: 700; }

/* Chỉ số mô hình */
.eq { background: #EEF3FF; border-radius: 8px; padding: .6rem .8rem; color: #1E3A8A;
      font-weight: 600; font-size: .92rem; margin: .3rem 0 .7rem; }
.metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .55rem; }
.metric { border: 1px solid #E3E8F0; border-radius: 8px; padding: .55rem .75rem; }
.metric span { display: block; font-size: .78rem; color: #64748B; }
.metric b { font-size: 1.2rem; color: #0F1E3D; font-variant-numeric: tabular-nums; }
.metric-range b { font-size: clamp(.8rem, 1.15vw, 1.05rem); white-space: nowrap; }
.insight { font-size: .86rem; color: #334155; line-height: 1.55; margin-top: .6rem; }
.overview-insight { margin-bottom: 1rem; }
</style>
        """,
        unsafe_allow_html=True,
    )


ICONS = {
    "filter": '<path d="M3 5h18l-7 8v6l-4 2v-8L3 5Z"/>',
    "people": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "coins": '<ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"/>',
    "median": '<path d="M3 3v18h18"/><rect x="7" y="12" width="3" height="6"/><rect x="12" y="8" width="3" height="10"/><rect x="17" y="5" width="3" height="13"/>',
    "down": '<path d="M12 5v14"/><path d="m19 12-7 7-7-7"/>',
    "up": '<path d="m22 7-8.5 8.5-5-5L2 17"/><path d="M16 7h6v6"/>',
}


def svg(name: str, color: str, size: int = 22) -> str:
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round">{ICONS[name]}</svg>')


def kpi_card(label: str, value: str, icon: str, color: str, bg: str) -> str:
    return (f'<div class="kpi"><div class="kpi-icon" style="background:{bg}">'
            f'{svg(icon, color)}</div><div><div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div></div></div>')


def page_head(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="page-head"><div><h1>{escape(title)}</h1>'
        f'<p>{escape(subtitle)}</p></div></div>',
        unsafe_allow_html=True,
    )


def card_title(title: str, note: str = "") -> None:
    html = f'<div class="card-title">{title}</div>'
    if note:
        html += f'<div class="card-note">{note}</div>'
    st.markdown(html, unsafe_allow_html=True)


def chart_title(title: str, chart_id: int, note: str = "", reg: dict | None = None) -> None:
    """Hiện nhận xét khi rê chuột hoặc đặt tiêu điểm vào biểu tượng bóng đèn."""
    comment = escape(insights.for_chart(chart_id, DF, reg))
    comment = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", comment)
    note_html = f'<div class="card-note">{escape(note)}</div>' if note else ""
    st.markdown(
        f'<div class="chart-heading"><div class="card-title">{escape(title)}</div>'
        f'<span class="chart-insight-icon" tabindex="0" '
        f'aria-label="Nhận xét cho {escape(title)}" aria-describedby="chart-tip-{chart_id}">'
        f'💡<span class="chart-insight-tooltip" id="chart-tip-{chart_id}" role="tooltip">'
        f'{comment}</span></span></div>{note_html}',
        unsafe_allow_html=True,
    )


def card(key: str):
    """Khung trắng giãn theo chiều cao của các box cùng hàng."""
    return st.container(border=True, key=f"card_{key}", height="stretch")


def chart(fig) -> None:
    st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)

@st.cache_data(show_spinner="Đang đọc và xử lý dữ liệu...")
def load_data() -> tuple[pd.DataFrame, dict]:
    raw = pd.read_csv(DATA_PATH)
    return an.clean_data(raw)


@st.cache_data(show_spinner=False)
def cached_regression(df: pd.DataFrame, x: str) -> dict:
    result = an.fit_regression(df, x=x)
    result.pop("model")  # đối tượng sklearn không cần cache
    return result


# ==========================================================================
# DASHBOARD 1 - TỔNG QUAN
# ==========================================================================
def page_overview() -> None:
    page_head("Tổng quan", "Quy mô bộ dữ liệu và phân bố mức lương của nhân viên.")
    k = an.kpis(DF)

    cards = [
        ("Tổng nhân viên", vn(k["count"]), "people", "#2563EB", "#E0EAFF"),
        ("Lương trung bình", vn(k["mean"]), "coins", "#0FA37F", "#DDF5EC"),
        ("Lương trung vị", vn(k["median"]), "median", "#7C3AED", "#EDE7FE"),
        ("Lương thấp nhất", vn(k["min"]), "down", "#EA580C", "#FFEBDD"),
        ("Lương cao nhất", vn(k["max"]), "up", "#E11D48", "#FFE4EA"),
    ]
    for col, c in zip(st.columns(5), cards):
        col.markdown(kpi_card(*c), unsafe_allow_html=True)
    st.write("")

    c1, c2, c3 = st.columns([1.35, 1, 1])
    with c1, card("1"):
        chart_title("Phân bố mức lương", 1)
        chart(ch.salary_histogram(DF, k["mean"]))
    with c2, card("2"):
        chart_title("Nhân viên theo phòng ban", 2)
        chart(ch.headcount_barh(DF))
    with c3, card("3"):
        chart_title("Lương trung bình theo phòng ban", 3)
        chart(ch.mean_salary_bar(an.group_salary(DF, "Department"), "Department"))

    d = an.describe_salary(DF)
    if d["Skewness"] < -0.5:
        skew_text = "lệch trái (đuôi dài về phía lương thấp)"
    elif d["Skewness"] > 0.5:
        skew_text = "lệch phải (đuôi dài về phía lương cao)"
    elif d["Kurtosis"] < -0.5:
        skew_text = ("có độ lệch nhỏ nhưng bẹt (kurtosis âm): lương trải rộng, "
                     "không tập trung quanh trung bình, có thể gồm nhiều nhóm mức lương khác nhau")
    else:
        skew_text = "gần đối xứng"
    with card("4"):
        card_title("Thống kê mô tả biến Salary",
                   "Hướng trung tâm, độ phân tán và hình dạng phân phối.")
        cols = st.columns([1, 1, 1.5, 1, 1, 1, 1])
        items = [
            ("Mode", vn(d["Mode"])), ("Độ lệch chuẩn", vn(d["Std"])),
            ("Q1 / Q3", f'{vn(d["Q1"])} / {vn(d["Q3"])}'), ("IQR", vn(d["IQR"])),
            ("CV", f'{vn(d["CV (%)"], 1)}%'), ("Skewness", vn(d["Skewness"], 3)),
            ("Kurtosis", vn(d["Kurtosis"], 3)),
        ]
        for col, (label, value) in zip(cols, items):
            metric_class = "metric metric-range" if label == "Q1 / Q3" else "metric"
            col.markdown(f'<div class="{metric_class}"><span>{label}</span><b>{value}</b></div>',
                         unsafe_allow_html=True)
        st.markdown(
            f'<div class="insight overview-insight">Trung bình ({vn(d["Mean"])}) '
            f'{"thấp hơn" if d["Mean"] < d["Median"] else "cao hơn"} trung vị ({vn(d["Median"])}), '
            f'phân phối {skew_text}. Có {vn(d["Outliers"])} giá trị ngoại lệ theo quy tắc '
            f'Q1 − 1,5·IQR và Q3 + 1,5·IQR.</div>',
            unsafe_allow_html=True,
        )


# ==========================================================================
# DASHBOARD 2 - PHÂN TÍCH LƯƠNG
# ==========================================================================
def page_salary() -> None:
    page_head("Phân tích lương",
              "So sánh mức lương theo phòng ban, chức danh, học vấn và địa điểm.")

    dept = an.group_salary(DF, "Department")
    row1 = st.columns(2)
    with row1[0], card("5"):
        chart_title("Lương theo phòng ban", 4)
        chart(ch.mean_median_bar(dept, "Department"))
    with row1[1], card("6"):
        chart_title("Lương theo chức danh", 5)
        chart(ch.mean_median_bar(an.group_salary(DF, "Job_Title"), "Job_Title"))

    row2 = st.columns(2)
    with row2[0], card("7"):
        chart_title("Lương theo học vấn", 6)
        chart(ch.mean_median_bar(an.group_salary(DF, "Education_Level"), "Education_Level"))
    with row2[1], card("8"):
        chart_title("Lương theo địa điểm", 7)
        chart(ch.mean_median_bar(an.group_salary(DF, "Location"), "Location"))

    row3 = st.columns([1.5, 1])
    with row3[0], card("9"):
        chart_title("Phân bố lương theo phòng ban", 8,
                    "Đường giữa hộp là trung vị, thân hộp là IQR, điểm rời là ngoại lệ.")
        chart(ch.salary_box(DF, list(dept["Department"])))

    with row3[1], card("10"):
        card_title("Kiểm định ANOVA",
                   "Lương trung bình giữa các nhóm có khác nhau thật sự không? (α = 0,05)")
        table = an.anova_table(DF, ["Job_Title", "Education_Level", "Department",
                                    "Location", "Gender"])
        if table.empty:
            st.info("Cần ít nhất 2 nhóm trong mỗi biến để chạy ANOVA. Hãy nới bộ lọc.")
        else:
            show = table.copy()
            show["Biến"] = show["Biến"].map(lambda c: ch.LABELS.get(c, "Giới tính" if c == "Gender" else c))
            show["F"] = show["F"].map(lambda v: vn(v, 2))
            show["p-value"] = show["p-value"].map(vn_p)
            st.dataframe(show[["Biến", "F", "p-value", "Kết luận"]],
                         hide_index=True, width="stretch")
            weak = table.loc[table["p-value"] >= 0.05, "Biến"].map(
                lambda c: ch.LABELS.get(c, "Giới tính" if c == "Gender" else c).lower()).tolist()
            if weak:
                st.markdown(
                    f'<div class="insight">Với {", ".join(weak)}, p-value ≥ 0,05 nên chưa đủ '
                    'bằng chứng cho thấy lương khác nhau giữa các nhóm, dù biểu đồ cột có '
                    'chênh lệch nhỏ.</div>', unsafe_allow_html=True)


# ==========================================================================
# DASHBOARD 3 - KINH NGHIỆM VÀ HỒI QUY
# ==========================================================================
def page_regression() -> None:
    page_head("Kinh nghiệm & mức lương",
              "Quan hệ giữa kinh nghiệm, độ tuổi và lương; mô hình hồi quy tuyến tính.")

    if len(DF) < 30:
        st.warning("Cần ít nhất 30 nhân viên để xây dựng mô hình hồi quy. Hãy nới bộ lọc bên trái.")
        return

    reg = cached_regression(DF, "Experience_Years")

    row1 = st.columns([1.6, 1])
    with row1[0], card("11"):
        chart_title("Kinh nghiệm so với mức lương", 9, reg=reg)
        chart(ch.scatter_with_line(DF, "Experience_Years", reg["b0"], reg["b1"],
                                   "Số năm kinh nghiệm", height=360))

    with row1[1], card("12"):
        card_title("Thông tin mô hình hồi quy")
        st.markdown(
            f'<div class="eq">Salary = {vn(reg["b0"], 1)} + {vn(reg["b1"], 1)} × Experience_Years</div>'
            '<div class="metric-grid">'
            f'<div class="metric"><span>Pearson r</span><b>{vn(reg["r"], 3)}</b></div>'
            f'<div class="metric"><span>p-value</span><b>{vn_p(reg["p"])}</b></div>'
            f'<div class="metric"><span>R² (train)</span><b>{vn(reg["r2_train"], 3)}</b></div>'
            f'<div class="metric"><span>R² (test)</span><b>{vn(reg["r2_test"], 3)}</b></div>'
            '</div>'
            f'<div class="insight">Mỗi năm kinh nghiệm tăng thêm, lương dự đoán tăng khoảng '
            f'<b>{vn(reg["b1"])}</b>. Kinh nghiệm và lương: '
            f'{an.correlation_strength(reg["r"])} (r = {vn(reg["r"], 3)}). '
            f'Mô hình giải thích {vn(reg["r2_test"] * 100, 1)}% biến thiên '
            'của lương trên tập test.</div>',
            unsafe_allow_html=True,
        )
       
        INPUT_BG = "#EEF3FF"
        st.markdown('<div style="font-weight:600; font-size:1rem; color:#0F1E3D; &nbsp;'
                    'margin:.8rem 0 .4rem;">Dự đoán lương theo số năm kinh nghiệm</div>',
                    unsafe_allow_html=True)

        with st.container(key="pred_row"):
            c_input, c_result = st.columns([3, 7], gap="small", vertical_alignment="top")
            with c_input:
                years = st.number_input(
                    "Số năm kinh nghiệm", min_value=0, max_value=50, value=10, step=1,
                    label_visibility="collapsed", key="pred_years",
                )
            with c_result:
                st.markdown(
                    f'<div style="height:2.5rem; box-sizing:border-box; margin:0; padding:0 1rem; '
                    f'display:flex; align-items:center; border-radius:8px; '
                    f'background:{INPUT_BG}; color:#1E293B; font-size:1rem; white-space:nowrap;">'
                    f'Lương dự đoán:&nbsp;<b>{vn(an.predict_salary(reg, years))}</b></div>',
                    unsafe_allow_html=True,
                )

    row2 = st.columns(2)
    with row2[0], card("13"):
        chart_title("Lương theo nhóm kinh nghiệm", 10)
        chart(ch.group_mean_bar(an.group_salary(DF, "Experience_Group", sort_by_mean=False),
                                "Experience_Group", height=440))
    with row2[1], card("14"):
        chart_title("Phần dư của mô hình", 11,
                    "Phần dư = lương thực tế − lương dự đoán (tập test). "
                    "Mô hình phù hợp khi các điểm rải ngẫu nhiên quanh trục 0.", reg=reg)
        chart(ch.residual_plot(reg["test_pred"], reg["test_residual"]))
        pred, res = reg["test_pred"], reg["test_residual"]
        hi = pred >= np.quantile(pred, 0.8)
        hi_mean = res[hi].mean()
        if abs(hi_mean) > 0.25 * reg["rmse"]:
            msg = (f"Phần dư chưa hoàn toàn ngẫu nhiên: ở vùng dự đoán cao, phần dư trung bình "
                   f"là {vn(hi_mean)}, tức mô hình dự đoán "
                   f"{'cao hơn' if hi_mean < 0 else 'thấp hơn'} thực tế. "
                   "Mô hình đơn biến chưa giải thích hết biến thiên của lương.")
        else:
            msg = "Phần dư rải tương đối đều quanh 0, mô hình tuyến tính khá phù hợp."
        st.markdown(f'<div class="insight">{msg}</div>', unsafe_allow_html=True)

    age_r, age_p = an.pearson(DF, "Age")
    age_b1, age_b0 = np.polyfit(DF["Age"], DF["Salary"], 1)
    row3 = st.columns(2)
    with row3[0], card("15"):
        chart_title("Độ tuổi và mức lương", 12,
                    f"Pearson r = {vn(age_r, 3)}, p-value {vn_p(age_p)}: "
                    f"{an.correlation_strength(age_r)}.")
        chart(ch.scatter_with_line(DF, "Age", age_b0, age_b1, "Độ tuổi"))
    with row3[1], card("16"):
        chart_title("Lương theo nhóm tuổi", 13)
        chart(ch.group_mean_bar(an.group_salary(DF, "Age_Group", sort_by_mean=False),
                                "Age_Group", height=345))

    with card("17"):
        chart_title("Ma trận tương quan", 14,
                    "Tuổi và kinh nghiệm tương quan rất mạnh với nhau, nên đưa cả hai vào "
                    "một mô hình đa biến sẽ gây đa cộng tuyến.")
        corr = DF[["Age", "Experience_Years", "Salary"]].corr()
        chart(ch.correlation_heatmap(corr, {"Age": "Độ tuổi",
                                            "Experience_Years": "Kinh nghiệm",
                                            "Salary": "Lương"}))


# ==========================================================================
# SIDEBAR
# ==========================================================================
inject_css()

pages = [
    st.Page(page_overview, title="Tổng quan", icon=":material/home:", url_path="tong-quan", default=True),
    st.Page(page_salary, title="Phân tích lương", icon=":material/finance:", url_path="phan-tich-luong"),
    st.Page(page_regression, title="Kinh nghiệm & mức lương", icon=":material/trending_up:", url_path="hoi-quy"),
]
current = st.navigation(pages, position="hidden")

with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-icon" aria-hidden="true">'
        '<div class="brand-bars">'
        '<span></span><span></span><span></span><span></span><span></span>'
        '</div></div>'
        '<div class="brand-text">'
        '<div class="brand-title">LƯƠNG NHÂN VIÊN</div>'
        '<div class="brand-sub">Phân tích &amp; Trực quan hóa dữ liệu</div></div>',
        unsafe_allow_html=True,
    )
    for p in pages:
        with st.container(key=f"nav_{p.url_path}"):
            st.page_link(p, label=p.title, icon=p.icon)
    st.markdown(
        f'<style>.st-key-nav_{current.url_path} a {{'
        'background: #EAF2FF !important; border-radius: 8px !important;'
        'box-shadow: inset 3px 0 0 #3B82F6, 0 2px 6px rgba(59, 130, 246, .18) !important;'
        'color: #2563EB !important; font-weight: 700 !important; }}</style>',
        unsafe_allow_html=True,
    )

try:
    FULL, report = load_data()
except (ValueError, pd.errors.ParserError) as err:
    st.error(f"Không đọc được dữ liệu. {err}")
    st.stop()
except FileNotFoundError:
    st.error("Không tìm thấy data/Employers_data.csv. Đặt file vào thư mục data/ hoặc tải file ở thanh bên.")
    st.stop()

st.session_state["report"] = report

with st.sidebar:
    st.markdown(
        f'<div class="side-divider"></div><div class="side-label">'
        f'{svg("filter", "#1B315A", 16)}<span>Bộ lọc dữ liệu</span></div>',
        unsafe_allow_html=True,
    )
    f_dept = st.multiselect("Phòng ban", sorted(FULL["Department"].unique()), placeholder="Tất cả")
    f_loc = st.multiselect("Địa điểm", sorted(FULL["Location"].unique()), placeholder="Tất cả")
    f_gender = st.multiselect("Giới tính", sorted(FULL["Gender"].unique()), placeholder="Tất cả")

DF = FULL
if f_dept:
    DF = DF[DF["Department"].isin(f_dept)]
if f_loc:
    DF = DF[DF["Location"].isin(f_loc)]
if f_gender:
    DF = DF[DF["Gender"].isin(f_gender)]

if DF.empty:
    st.warning("Không có nhân viên nào khớp bộ lọc. Bỏ bớt lựa chọn ở thanh bên để xem lại dữ liệu.")
    st.stop()

current.run()
