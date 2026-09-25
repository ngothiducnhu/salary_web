"""
charts.py - Các hàm vẽ biểu đồ bằng Plotly.

Loại biểu đồ chọn theo mục đích như Bài 4:
    Histogram  -> phân phối tần suất
    Bar        -> so sánh giữa các nhóm
    Box plot   -> phân bố và giá trị ngoại lệ
    Scatter    -> mối quan hệ giữa hai biến
    Residual   -> đánh giá mô hình hồi quy (Bài 6)
    Heatmap    -> ma trận tương quan (Bài 5)
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Bảng màu thống nhất trên toàn bộ dashboard
BLUE = "#2563EB"
TEAL = "#0FA37F"
INK = "#1E293B"
MUTED = "#64748B"
GRID = "#E8EDF5"
FONT = "Be Vietnam Pro, Segoe UI, Arial, sans-serif"

DEPT_COLORS = {
    "Engineering": "#2563EB",
    "Marketing": "#0FA37F",
    "Product": "#38BDF8",
    "HR": "#F59E0B",
    "Sales": "#8B5CF6",
    "Finance": "#22C55E",
}
SEQUENCE = ["#38BDF8", "#0FA37F", "#8B5CF6", "#EC4899", "#F59E0B", "#7C3AED", "#22C55E", "#2563EB"]

LABELS = {
    "Department": "Phòng ban",
    "Job_Title": "Chức danh",
    "Education_Level": "Học vấn",
    "Location": "Địa điểm",
    "Experience_Group": "Nhóm kinh nghiệm (năm)",
    "Age_Group": "Nhóm tuổi",
}


def _color_for(key: str, i: int) -> str:
    return DEPT_COLORS.get(key, SEQUENCE[i % len(SEQUENCE)])


def style(fig: go.Figure, height: int = 330, legend: bool = False) -> go.Figure:
    """Giao diện chung: nền trắng, lưới nhạt, số theo kiểu Việt Nam (1.000,5)."""
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family=FONT, size=12, color=INK),
        separators=",.",
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1,
                    font=dict(size=11)),
        hoverlabel=dict(font_family=FONT, bgcolor="white"),
        bargap=0.25,
    )
    fig.update_xaxes(showgrid=False, linecolor=GRID, tickfont=dict(color=MUTED), title_font=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED), title_font=dict(color=MUTED))
    return fig


# --------------------------------------------------------------------------
# Dashboard 1 - Tổng quan
# --------------------------------------------------------------------------
def salary_histogram(df: pd.DataFrame, mean_value: float) -> go.Figure:
    """Biểu đồ 1: phân bố mức lương, kèm đường trung bình."""
    fig = go.Figure(go.Histogram(
        x=df["Salary"], nbinsx=40, marker_color=BLUE,
        marker_line=dict(color="white", width=1),
        hovertemplate="Mức lương: %{x}<br>Số nhân viên: %{y:,.0f}<extra></extra>",
    ))
    fig.add_vline(x=mean_value, line_dash="dash", line_color=INK, line_width=1)
    fig.add_annotation(x=mean_value, y=1, yref="paper", xanchor="left", yanchor="top",
                       text=f" Trung bình: {mean_value:,.0f}".replace(",", "."),
                       showarrow=False, font=dict(size=11, color=INK))
    fig.update_xaxes(title="Mức lương", tickformat=",.0f")
    fig.update_yaxes(title="Số nhân viên")
    style(fig)
    fig.update_layout(bargap=0.06)
    return fig


def headcount_barh(df: pd.DataFrame) -> go.Figure:
    """Biểu đồ 2: số nhân viên theo phòng ban, bar ngang, xếp từ nhiều đến ít."""
    counts = df["Department"].value_counts().sort_values()
    fig = go.Figure(go.Bar(
        x=counts.values, y=counts.index, orientation="h",
        marker_color=[_color_for(d, i) for i, d in enumerate(counts.index)],
        text=[f"{v:,}".replace(",", ".") for v in counts.values],
        textposition="outside", cliponaxis=False,
        hovertemplate="%{y}: %{x:,.0f} nhân viên<extra></extra>",
    ))
    fig.update_xaxes(title="Số nhân viên", range=[0, counts.max() * 1.18], showgrid=True, gridcolor=GRID)
    fig.update_yaxes(showgrid=False)
    return style(fig)


def mean_salary_bar(grouped: pd.DataFrame, col: str) -> go.Figure:
    """Biểu đồ 3: lương trung bình theo phòng ban, xếp tăng dần."""
    g = grouped.sort_values("Mean")
    fig = go.Figure(go.Bar(
        x=g[col], y=g["Mean"],
        marker_color=[_color_for(d, i) for i, d in enumerate(g[col])],
        text=[f"{v / 1000:,.1f}k".replace(".", ",") for v in g["Mean"]],
        textposition="outside", cliponaxis=False,
        hovertemplate="%{x}<br>Lương trung bình: %{y:,.0f}<extra></extra>",
    ))
    fig.update_xaxes(title=LABELS.get(col, col))
    fig.update_yaxes(title="Lương trung bình", range=[0, g["Mean"].max() * 1.15])
    return style(fig)


# --------------------------------------------------------------------------
# Dashboard 2 - Phân tích lương
# --------------------------------------------------------------------------
def mean_median_bar(grouped: pd.DataFrame, col: str, height: int = 320) -> go.Figure:
    """Biểu đồ 4-7: so sánh trung bình và trung vị giữa các nhóm."""
    x = grouped[col].astype(str)
    fig = go.Figure([
        go.Bar(name="Trung bình", x=x, y=grouped["Mean"], marker_color=BLUE,
               customdata=grouped["Count"],
               hovertemplate="%{x}<br>Trung bình: %{y:,.0f}<br>Số NV: %{customdata:,.0f}<extra></extra>"),
        go.Bar(name="Trung vị", x=x, y=grouped["Median"], marker_color=TEAL,
               hovertemplate="%{x}<br>Trung vị: %{y:,.0f}<extra></extra>"),
    ])
    fig.update_layout(barmode="group", bargroupgap=0.08)
    fig.update_yaxes(title="Lương", tickformat="~s")
    return style(fig, height=height, legend=True)


def salary_box(df: pd.DataFrame, order: list[str]) -> go.Figure:
    """Biểu đồ 8: phân bố lương theo phòng ban (median, IQR, ngoại lệ)."""
    fig = go.Figure()
    for i, dept in enumerate(order):
        color = _color_for(dept, i)
        fig.add_trace(go.Box(
            y=df.loc[df["Department"] == dept, "Salary"], name=dept,
            marker_color=color, line_color=color, fillcolor=_hex_alpha(color, 0.35),
            boxpoints="outliers", marker_size=4,
        ))
    fig.update_yaxes(title="Lương", tickformat="~s")
    fig.update_xaxes(title="Phòng ban")
    return style(fig, height=320)


def _hex_alpha(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


# --------------------------------------------------------------------------
# Dashboard 3 - Kinh nghiệm & hồi quy
# --------------------------------------------------------------------------
def scatter_with_line(df: pd.DataFrame, x: str, b0: float, b1: float,
                      x_title: str, height: int = 360) -> go.Figure:
    """Biểu đồ 9 và 12: scatter dữ liệu thực tế + đường hồi quy y = b0 + b1x."""
    xs = np.linspace(df[x].min(), df[x].max(), 50)
    fig = go.Figure([
        go.Scattergl(
            x=df[x], y=df["Salary"], mode="markers", name="Dữ liệu thực tế",
            marker=dict(color=BLUE, size=5, opacity=0.35),
            hovertemplate=f"{x_title}: %{{x}}<br>Lương: %{{y:,.0f}}<extra></extra>",
        ),
        go.Scatter(
            x=xs, y=b0 + b1 * xs, mode="lines", name="Đường hồi quy",
            line=dict(color=INK, width=2.5),
            hovertemplate="Dự đoán: %{y:,.0f}<extra></extra>",
        ),
    ])
    fig.update_xaxes(title=x_title, showgrid=True, gridcolor=GRID)
    fig.update_yaxes(title="Lương", tickformat="~s")
    return style(fig, height=height, legend=True)


def group_mean_bar(grouped: pd.DataFrame, col: str, height: int = 320) -> go.Figure:
    """Biểu đồ 10 và 13: lương trung bình theo nhóm kinh nghiệm / nhóm tuổi."""
    labels = grouped[col].astype(str)
    fig = go.Figure(go.Bar(
        x=labels, y=grouped["Mean"],
        marker_color=[SEQUENCE[i % len(SEQUENCE)] for i in range(len(grouped))],
        text=[f"{v / 1000:,.0f}k" for v in grouped["Mean"]],
        textposition="outside", cliponaxis=False,
        customdata=grouped["Count"],
        hovertemplate="%{x}<br>Lương trung bình: %{y:,.0f}<br>Số NV: %{customdata:,.0f}<extra></extra>",
    ))
    fig.update_xaxes(title=LABELS.get(col, col), type="category")
    fig.update_yaxes(title="Lương trung bình", tickformat="~s", range=[0, grouped["Mean"].max() * 1.15])
    return style(fig, height=height)


def residual_plot(pred: np.ndarray, residual: np.ndarray, height: int = 320) -> go.Figure:
    """Biểu đồ 11: phần dư theo giá trị dự đoán (tập test)."""
    fig = go.Figure(go.Scattergl(
        x=pred, y=residual, mode="markers",
        marker=dict(color=BLUE, size=5, opacity=0.35),
        hovertemplate="Dự đoán: %{x:,.0f}<br>Phần dư: %{y:,.0f}<extra></extra>",
    ))
    fig.add_hline(y=0, line_color=INK, line_width=1.5)
    fig.update_xaxes(title="Giá trị dự đoán", tickformat="~s", showgrid=True, gridcolor=GRID)
    fig.update_yaxes(title="Phần dư", tickformat="~s")
    return style(fig, height=height)


def correlation_heatmap(corr: pd.DataFrame, labels: dict) -> go.Figure:
    """Ma trận tương quan Pearson giữa các biến số (Bài 5)."""
    names = [labels.get(c, c) for c in corr.columns]
    fig = go.Figure(go.Heatmap(
        z=corr.values, x=names, y=names, zmin=-1, zmax=1,
        colorscale="RdBu", reversescale=True,
        text=corr.values, texttemplate="%{text:.2f}", textfont=dict(size=14),
        hovertemplate="%{y} – %{x}: %{z:.3f}<extra></extra>",
        colorbar=dict(thickness=10, outlinewidth=0),
    ))
    fig.update_yaxes(autorange="reversed", showgrid=False)
    fig.update_xaxes(showgrid=False)
    return style(fig, height=300)
