"""
app.py - Web phân tích và trực quan hóa dữ liệu lương nhân viên.

Chạy:  streamlit run app.py

Cấu trúc 3 dashboard theo file định hướng chart:
    1. Tổng quan               - KPI + biểu đồ 1, 2, 3
    2. Phân tích lương         - biểu đồ 4 đến 8 + ANOVA
    3. Kinh nghiệm & hồi quy   - biểu đồ 9 đến 13 + chỉ số mô hình
"""

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

import analysis as an
import charts as ch

st.set_page_config(
    page_title="Phân tích lương nhân viên",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "data" / "Employers_data.csv"
PLOT_CONFIG = {"displayModeBar": False, "responsive": True}


# ==========================================================================
# Định dạng số kiểu Việt Nam: 115.381,5
# ==========================================================================
def vn(value: float, decimals: int = 0) -> str:
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "X").replace(".", ",").replace("X", ".")


def vn_p(p: float) -> str:
    return "< 0,001" if p < 0.001 else vn(p, 3)


# ==========================================================================
# Giao diện (CSS)
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
.stApp { background: #F4F6FB; }
.block-container { padding-top: 1.6rem; padding-bottom: 3rem; max-width: 1500px; }
header[data-testid="stHeader"] { background: transparent; }

/* Sidebar xanh navy */
section[data-testid="stSidebar"] { background: #0F1E3D; }
section[data-testid="stSidebar"] * { color: #E2E8F0; }
section[data-testid="stSidebar"] [data-baseweb="select"] *,
section[data-testid="stSidebar"] [data-baseweb="tag"] * { color: #1E293B; }
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] { background: #1B2B4F; }
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button { color: #1E293B; }
.brand { display: flex; gap: .7rem; align-items: center; margin: .2rem 0 1.4rem; }
.brand-icon { width: 40px; height: 40px; border-radius: 10px; background: #2563EB;
              display: grid; place-items: center; flex: none; }
.brand-title { font-weight: 700; font-size: .98rem; line-height: 1.35; color: #FFFFFF; }
[data-testid="stPageLink"] a { border-radius: 8px; padding: .45rem .7rem; }
[data-testid="stPageLink"] a:hover { background: #1B2B4F; }
[data-testid="stPageLink"] a[aria-current="page"],
[data-testid="stPageLink-NavLink"][aria-current="page"] { background: #2563EB; }
.side-label { font-size: .78rem; color: #94A3B8 !important; margin: 1.4rem 0 .3rem; }

/* Tiêu đề section */
.page-head { display: flex; justify-content: space-between; align-items: flex-start;
             gap: 1rem; margin-bottom: 1rem; flex-wrap: wrap; }
.page-head h1 { font-size: 1.55rem; font-weight: 700; color: #0F1E3D; margin: 0; padding: 0; }
.page-head p { color: #64748B; margin: .2rem 0 0; font-size: .92rem; }
.scope { background: #FFFFFF; border: 1px solid #DCE3EE; border-radius: 8px;
         padding: .45rem .8rem; font-size: .85rem; color: #1E293B; white-space: nowrap; }

/* Thẻ KPI */
.kpi { background: #FFFFFF; border: 1px solid #E3E8F0; border-radius: 12px;
       padding: 1rem 1.1rem; display: flex; gap: .85rem; align-items: center; height: 100%; }
.kpi-icon { width: 44px; height: 44px; border-radius: 50%; display: grid;
            place-items: center; flex: none; }
.kpi-label { color: #475569; font-size: .84rem; }
.kpi-value { color: #0F1E3D; font-size: 1.45rem; font-weight: 700; line-height: 1.3;
             font-variant-numeric: tabular-nums; }

/* Khung chart: st.container(border=True, key="card_...") */
[class*="st-key-card_"] { background: #FFFFFF; border-radius: 12px; border-color: #E3E8F0 !important; }
.card-title { font-weight: 600; font-size: .95rem; color: #0F1E3D; margin-bottom: .1rem; }
.card-note { font-size: .8rem; color: #64748B; margin-bottom: .2rem; }

/* Chỉ số mô hình */
.eq { background: #EEF3FF; border-radius: 8px; padding: .6rem .8rem; color: #1E3A8A;
      font-weight: 600; font-size: .92rem; margin: .3rem 0 .7rem; }
.metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: .55rem; }
.metric { border: 1px solid #E3E8F0; border-radius: 8px; padding: .55rem .75rem; }
.metric span { display: block; font-size: .78rem; color: #64748B; }
.metric b { font-size: 1.2rem; color: #0F1E3D; font-variant-numeric: tabular-nums; }
.insight { font-size: .86rem; color: #334155; line-height: 1.55; margin-top: .6rem; }
</style>
        """,
        unsafe_allow_html=True,
    )


ICONS = {
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
    total = st.session_state["n_total"]
    n = len(DF)
    scope = (f"Toàn bộ dữ liệu: {vn(n)} nhân viên" if n == total
             else f"Đang lọc: {vn(n)} / {vn(total)} nhân viên")
    st.markdown(
        f'<div class="page-head"><div><h1>{title}</h1><p>{subtitle}</p></div>'
        f'<div class="scope">📅 {scope}</div></div>',
        unsafe_allow_html=True,
    )


def card_title(title: str, note: str = "") -> None:
    html = f'<div class="card-title">{title}</div>'
    if note:
        html += f'<div class="card-note">{note}</div>'
    st.markdown(html, unsafe_allow_html=True)


def card(key: str):
    """Khung trắng bo góc chứa 1 biểu đồ."""
    return st.container(border=True, key=f"card_{key}")


def chart(fig) -> None:
    st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG)


# ==========================================================================
# Dữ liệu (Bài 1 - nhập dữ liệu, Bài 2 - tiền xử lý)
# ==========================================================================
@st.cache_data(show_spinner="Đang đọc và xử lý dữ liệu...")
def load_data(file_bytes: bytes | None) -> tuple[pd.DataFrame, dict]:
    if file_bytes is None:
        raw = pd.read_csv(DATA_PATH)
    else:
        from io import BytesIO
        raw = pd.read_csv(BytesIO(file_bytes))
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
        ("Lương trung bình", vn(k["mean"], 1), "coins", "#0FA37F", "#DDF5EC"),
        ("Lương trung vị", vn(k["median"]), "median", "#7C3AED", "#EDE7FE"),
        ("Lương thấp nhất", vn(k["min"]), "down", "#EA580C", "#FFEBDD"),
        ("Lương cao nhất", vn(k["max"]), "up", "#E11D48", "#FFE4EA"),
    ]
    for col, c in zip(st.columns(5), cards):
        col.markdown(kpi_card(*c), unsafe_allow_html=True)
    st.write("")

    c1, c2, c3 = st.columns([1.35, 1, 1])
    with c1, card("1"):
        card_title("Phân bố mức lương")
        chart(ch.salary_histogram(DF, k["mean"]))
    with c2, card("2"):
        card_title("Nhân viên theo phòng ban")
        chart(ch.headcount_barh(DF))
    with c3, card("3"):
        card_title("Lương trung bình theo phòng ban")
        chart(ch.mean_salary_bar(an.group_salary(DF, "Department"), "Department"))

    # ---- Thống kê mô tả (Bài 5) ----
    d = an.describe_salary(DF)
    skew_text = ("lệch trái (đuôi dài về phía lương thấp)" if d["Skewness"] < -0.5
                 else "lệch phải (đuôi dài về phía lương cao)" if d["Skewness"] > 0.5
                 else "gần đối xứng")
    with card("4"):
        card_title("Thống kê mô tả biến Salary",
                   "Hướng trung tâm, độ phân tán và hình dạng phân phối.")
        cols = st.columns(7)
        items = [
            ("Mode", vn(d["Mode"])), ("Độ lệch chuẩn", vn(d["Std"])),
            ("Q1 / Q3", f'{vn(d["Q1"])} / {vn(d["Q3"])}'), ("IQR", vn(d["IQR"])),
            ("CV", f'{vn(d["CV (%)"], 1)}%'), ("Skewness", vn(d["Skewness"], 3)),
            ("Kurtosis", vn(d["Kurtosis"], 3)),
        ]
        for col, (label, value) in zip(cols, items):
            col.markdown(f'<div class="metric"><span>{label}</span><b>{value}</b></div>',
                         unsafe_allow_html=True)
        st.markdown(
            f'<div class="insight">Trung bình ({vn(d["Mean"])}) '
            f'{"thấp hơn" if d["Mean"] < d["Median"] else "cao hơn"} trung vị ({vn(d["Median"])}), '
            f'phân phối {skew_text}. Có {vn(d["Outliers"])} giá trị ngoại lệ theo quy tắc '
            f'Q1 − 1,5·IQR và Q3 + 1,5·IQR.</div>',
            unsafe_allow_html=True,
        )

    # ---- Kiểm tra và tiền xử lý dữ liệu (Bài 1, 2) ----
    with st.expander("Dữ liệu và các bước tiền xử lý"):
        rep = st.session_state["report"]
        st.markdown(
            f"- Số dòng đọc được: **{vn(rep['rows_raw'])}**, sau xử lý: **{vn(rep['rows_clean'])}**\n"
            f"- Dòng bị loại do thiếu Salary: **{rep['dropped_missing_salary']}**; "
            f"dòng trùng lặp bị loại: **{rep['dropped_duplicates']}**\n"
            f"- Tổng số giá trị khuyết trước xử lý: **{int(rep['missing_before'].sum())}**\n"
            "- Đã tạo thêm 2 cột phân loại bằng `pd.cut()`: `Experience_Group`, `Age_Group`"
        )
        a, b = st.columns([1, 1.6])
        a.markdown("**Kiểu dữ liệu (tương tự `df.info()`)**")
        a.dataframe(an.dtype_table(DF), hide_index=True, width="stretch")
        b.markdown("**5 dòng đầu (`df.head()`)**")
        b.dataframe(DF.head(), hide_index=True, width="stretch")
        st.download_button(
            "Tải dữ liệu đang xem (.csv)",
            DF.to_csv(index=False).encode("utf-8-sig"),
            file_name="luong_nhan_vien_da_xu_ly.csv",
            mime="text/csv",
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
        card_title("Lương theo phòng ban")
        chart(ch.mean_median_bar(dept, "Department"))
    with row1[1], card("6"):
        card_title("Lương theo chức danh")
        chart(ch.mean_median_bar(an.group_salary(DF, "Job_Title"), "Job_Title"))

    row2 = st.columns(2)
    with row2[0], card("7"):
        card_title("Lương theo học vấn")
        chart(ch.mean_median_bar(an.group_salary(DF, "Education_Level"), "Education_Level"))
    with row2[1], card("8"):
        card_title("Lương theo địa điểm")
        chart(ch.mean_median_bar(an.group_salary(DF, "Location"), "Location"))

    row3 = st.columns([1.5, 1])
    with row3[0], card("9"):
        card_title("Phân bố lương theo phòng ban",
                   "Đường giữa hộp là trung vị, thân hộp là IQR, điểm rời là ngoại lệ.")
        chart(ch.salary_box(DF, list(dept["Department"])))

    # ---- ANOVA (Bài 5) ----
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
        card_title("Kinh nghiệm so với mức lương")
        chart(ch.scatter_with_line(DF, "Experience_Years", reg["b0"], reg["b1"],
                                   "Số năm kinh nghiệm", height=380))

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
            f'<b>{vn(reg["b1"])}</b>. Mô hình giải thích {vn(reg["r2_test"] * 100, 1)}% biến thiên '
            f'của lương trên tập test ({an.correlation_strength(reg["r"])}).</div>',
            unsafe_allow_html=True,
        )
       
        INPUT_BG = "#EEF3FF"
        st.markdown('<div style="font-weight:600; font-size:1rem; color:#0F1E3D; '
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
                    f'Lương dự đoán:<b>{vn(an.predict_salary(reg, years))}</b></div>',
                    unsafe_allow_html=True,
                )

    row2 = st.columns(2)
    with row2[0], card("13"):
        card_title("Lương theo nhóm kinh nghiệm")
        chart(ch.group_mean_bar(an.group_salary(DF, "Experience_Group", sort_by_mean=False),
                                "Experience_Group"))
    with row2[1], card("14"):
        card_title("Phần dư của mô hình",
                   "Điểm rải ngẫu nhiên quanh trục 0 cho thấy mô hình tuyến tính phù hợp.")
        chart(ch.residual_plot(reg["test_pred"], reg["test_residual"]))

    age_r, age_p = an.pearson(DF, "Age")
    age_b1, age_b0 = np.polyfit(DF["Age"], DF["Salary"], 1)
    row3 = st.columns(2)
    with row3[0], card("15"):
        card_title("Độ tuổi và mức lương",
                   f"Pearson r = {vn(age_r, 3)}, p-value {vn_p(age_p)}: "
                   f"{an.correlation_strength(age_r)}.")
        chart(ch.scatter_with_line(DF, "Age", age_b0, age_b1, "Độ tuổi"))
    with row3[1], card("16"):
        card_title("Lương theo nhóm tuổi")
        chart(ch.group_mean_bar(an.group_salary(DF, "Age_Group", sort_by_mean=False),
                                "Age_Group", height=345))

    with card("17"):
        card_title("Ma trận tương quan",
                   "Tuổi và kinh nghiệm tương quan rất mạnh với nhau, nên đưa cả hai vào "
                   "một mô hình đa biến sẽ gây đa cộng tuyến.")
        corr = DF[["Age", "Experience_Years", "Salary"]].corr()
        chart(ch.correlation_heatmap(corr, {"Age": "Độ tuổi",
                                            "Experience_Years": "Kinh nghiệm",
                                            "Salary": "Lương"}))


# ==========================================================================
# SIDEBAR + ĐIỀU HƯỚNG
# ==========================================================================
inject_css()

pages = [
    st.Page(page_overview, title="Tổng quan", icon=":material/home:", url_path="tong-quan", default=True),
    st.Page(page_salary, title="Phân tích lương", icon=":material/bar_chart:", url_path="phan-tich-luong"),
    st.Page(page_regression, title="Kinh nghiệm & hồi quy", icon=":material/trending_up:", url_path="hoi-quy"),
]
current = st.navigation(pages, position="hidden")

with st.sidebar:
    st.markdown(
        f'<div class="brand"><div class="brand-icon">{svg("people", "#FFFFFF")}</div>'
        '<div class="brand-title">Phân tích và trực quan hóa dữ liệu lương nhân viên</div></div>',
        unsafe_allow_html=True,
    )
    for p in pages:
        st.page_link(p, label=p.title, icon=p.icon)

    st.markdown('<div class="side-label">Nguồn dữ liệu</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Tải file CSV khác", type="csv", label_visibility="collapsed")

try:
    FULL, report = load_data(uploaded.getvalue() if uploaded else None)
except (ValueError, pd.errors.ParserError) as err:
    st.error(f"Không đọc được dữ liệu. {err}")
    st.stop()
except FileNotFoundError:
    st.error("Không tìm thấy data/Employers_data.csv. Đặt file vào thư mục data/ hoặc tải file ở thanh bên.")
    st.stop()

st.session_state["report"] = report
st.session_state["n_total"] = len(FULL)

with st.sidebar:
    st.markdown('<div class="side-label">Bộ lọc</div>', unsafe_allow_html=True)
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
