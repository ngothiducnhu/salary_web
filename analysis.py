"""
analysis.py - Xử lý dữ liệu và tính toán thống kê.

Mỗi hàm gắn với một bài trong slide:
    Bài 1 - Nhập dữ liệu, kiểm tra kiểu dữ liệu, tóm tắt
    Bài 2 - Tiền xử lý: giá trị khuyết, định dạng, chia nhóm (binning)
    Bài 5 - Thống kê mô tả, tương quan Pearson, gom nhóm, ANOVA
    Bài 6 - Hồi quy tuyến tính, MSE, R^2
    Bài 7 - Train/test split, MAE, RMSE
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split

# --------------------------------------------------------------------------
# Cấu hình chung
# --------------------------------------------------------------------------
REQUIRED_COLUMNS = [
    "Age", "Gender", "Department", "Job_Title",
    "Experience_Years", "Education_Level", "Location", "Salary",
]
NUMERIC_COLUMNS = ["Age", "Experience_Years", "Salary"]
CATEGORICAL_COLUMNS = ["Gender", "Department", "Job_Title", "Education_Level", "Location"]

# Các ký hiệu thường dùng cho giá trị khuyết trong dữ liệu thô (Bài 2)
MISSING_MARKERS = ["?", ".", "", " ", "N/A", "NA", "n/a", "Null", "null", "None", "NaN", "nan"]

# Nhóm kinh nghiệm và nhóm tuổi (Bài 2 - chuyển giá trị số thành giá trị phân loại)
EXP_BINS = [-1, 2, 5, 10, 20, 30, np.inf]
EXP_LABELS = ["0-2", "3-5", "6-10", "11-20", "21-30", "31+"]
AGE_BINS = [0, 29, 39, 49, np.inf]
AGE_LABELS = ["Dưới 30", "30-39", "40-49", "50+"]

# Thứ tự hiển thị có ý nghĩa cho biến phân loại có thứ tự
EDUCATION_ORDER = ["Bachelor", "Master", "PhD"]


# --------------------------------------------------------------------------
# Bài 1 + Bài 2: Nhập và tiền xử lý dữ liệu
# --------------------------------------------------------------------------
def validate_columns(df: pd.DataFrame) -> None:
    """Báo lỗi rõ ràng nếu file CSV thiếu cột bắt buộc."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            "File CSV thiếu các cột: " + ", ".join(missing)
            + ". Cần đủ các cột: " + ", ".join(REQUIRED_COLUMNS) + "."
        )


def clean_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Tiền xử lý dữ liệu theo Bài 2, trả về (df_sạch, báo_cáo).

    1. Chuyển các ký hiệu khuyết ("?", "N/A", ô trống...) thành NaN
    2. Định dạng: bỏ khoảng trắng thừa, ép kiểu số bằng pd.to_numeric
    3. Giá trị khuyết:
       - Salary (biến mục tiêu) khuyết -> loại bỏ dòng (dropna)
       - Biến số khác -> thay bằng trung bình (mean)
       - Biến phân loại -> thay bằng giá trị xuất hiện nhiều nhất (mode)
    4. Loại dòng trùng lặp
    5. Tạo nhóm kinh nghiệm, nhóm tuổi bằng pd.cut (binning)
    """
    validate_columns(raw)
    df = raw.copy()
    report = {"rows_raw": len(df)}

    # 1. Ký hiệu khuyết -> NaN
    df = df.replace(MISSING_MARKERS, np.nan)

    # 2. Định dạng dữ liệu
    for col in CATEGORICAL_COLUMNS:
        df[col] = df[col].astype("string").str.strip()
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    report["missing_before"] = df[REQUIRED_COLUMNS].isna().sum()

    # 3. Xử lý giá trị khuyết
    df = df.dropna(subset=["Salary"])
    report["dropped_missing_salary"] = report["rows_raw"] - len(df)
    for col in ["Age", "Experience_Years"]:
        df[col] = df[col].fillna(df[col].mean())
    for col in CATEGORICAL_COLUMNS:
        if df[col].isna().any():
            df[col] = df[col].fillna(df[col].mode().iloc[0])

    # 4. Dòng trùng lặp
    before = len(df)
    subset = ["Employee_ID"] if "Employee_ID" in df.columns else None
    df = df.drop_duplicates(subset=subset)
    report["dropped_duplicates"] = before - len(df)

    df["Age"] = df["Age"].round().astype(int)
    df["Experience_Years"] = df["Experience_Years"].round().astype(int)

    # 5. Binning
    df["Experience_Group"] = pd.cut(df["Experience_Years"], bins=EXP_BINS, labels=EXP_LABELS)
    df["Age_Group"] = pd.cut(df["Age"], bins=AGE_BINS, labels=AGE_LABELS)

    report["rows_clean"] = len(df)
    return df.reset_index(drop=True), report


def dtype_table(df: pd.DataFrame) -> pd.DataFrame:
    """Bảng kiểu dữ liệu + số giá trị non-null, tương tự df.info() (Bài 1)."""
    cols = [c for c in df.columns if c in REQUIRED_COLUMNS]
    return pd.DataFrame({
        "Cột": cols,
        "Kiểu dữ liệu": [str(df[c].dtype) for c in cols],
        "Số giá trị non-null": [int(df[c].notna().sum()) for c in cols],
        "Số giá trị khác nhau": [int(df[c].nunique()) for c in cols],
    })


# --------------------------------------------------------------------------
# Bài 5: Thống kê mô tả
# --------------------------------------------------------------------------
def kpis(df: pd.DataFrame) -> dict:
    s = df["Salary"]
    return {
        "count": len(df),
        "mean": s.mean(),
        "median": s.median(),
        "min": s.min(),
        "max": s.max(),
    }


def describe_salary(df: pd.DataFrame) -> dict:
    """Hướng trung tâm, độ phân tán, hình dạng phân phối và ngoại lệ của Salary."""
    s = df["Salary"]
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return {
        "Mean": s.mean(),
        "Median": s.median(),
        "Mode": s.mode().iloc[0],
        "Range": s.max() - s.min(),
        "Q1": q1,
        "Q3": q3,
        "IQR": iqr,
        "Variance": s.var(),          # phương sai mẫu, chia n - 1
        "Std": s.std(),
        "CV (%)": s.std() / s.mean() * 100,
        "Skewness": s.skew(),
        "Kurtosis": s.kurt(),
        "Outliers": int(((s < low) | (s > high)).sum()),
    }


def group_salary(df: pd.DataFrame, col: str, sort_by_mean: bool = True) -> pd.DataFrame:
    """Gom nhóm bằng groupby: trung bình, trung vị, số lượng nhân viên (Bài 5)."""
    g = (
        df.groupby(col, observed=True)["Salary"]
        .agg(Mean="mean", Median="median", Count="count")
        .reset_index()
    )
    if col == "Education_Level":
        order = [e for e in EDUCATION_ORDER if e in g[col].values]
        order += [e for e in g[col] if e not in order]
        g[col] = pd.Categorical(g[col], categories=order, ordered=True)
        return g.sort_values(col)
    if sort_by_mean:
        return g.sort_values("Mean", ascending=False)
    return g


def anova_table(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """
    ANOVA một chiều (scipy.stats.f_oneway): kiểm tra lương trung bình
    giữa các nhóm của một biến phân loại có khác nhau hay không (Bài 5).
    """
    rows = []
    for col in cols:
        groups = [g["Salary"].values for _, g in df.groupby(col, observed=True) if len(g) > 1]
        if len(groups) < 2:
            continue
        f, p = stats.f_oneway(*groups)
        rows.append({
            "Biến": col,
            "Số nhóm": len(groups),
            "F": f,
            "p-value": p,
            "Kết luận": "Có ảnh hưởng đến lương" if p < 0.05 else "Không có khác biệt đáng kể",
        })
    return pd.DataFrame(rows)


def pearson(df: pd.DataFrame, x: str, y: str = "Salary") -> tuple[float, float]:
    """Hệ số tương quan Pearson và p-value (Bài 5)."""
    r, p = stats.pearsonr(df[x], df[y])
    return float(r), float(p)


def correlation_strength(r: float) -> str:
    """Diễn giải mức độ tương quan theo bảng ngưỡng trong Bài 5."""
    a = abs(r)
    if a >= 0.8:
        level = "mạnh"
    elif a >= 0.5:
        level = "vừa"
    elif a >= 0.3:
        level = "yếu"
    else:
        return "không có tương quan"
    return f"tương quan {'thuận' if r > 0 else 'nghịch'} {level}"


# --------------------------------------------------------------------------
# Bài 6 + Bài 7: Hồi quy tuyến tính và đánh giá mô hình
# --------------------------------------------------------------------------
def fit_regression(df: pd.DataFrame, x: str = "Experience_Years", y: str = "Salary",
                   test_size: float = 0.3, random_state: int = 0) -> dict:
    """
    Hồi quy tuyến tính đơn biến: y = b0 + b1 * x

    - Chia dữ liệu train/test bằng train_test_split (Bài 7)
    - Fit mô hình trên tập train (Bài 6)
    - Đánh giá: R^2 train/test, MSE, MAE, RMSE
    - Phần dư (residual) = giá trị thực - giá trị dự đoán, tính trên tập test
    """
    X = df[[x]]
    Y = df[y]
    X_train, X_test, y_train, y_test = train_test_split(
        X, Y, test_size=test_size, random_state=random_state
    )

    lm = LinearRegression()
    lm.fit(X_train, y_train)
    y_pred = lm.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r, p = pearson(df, x, y)

    return {
        "model": lm,
        "b0": float(lm.intercept_),
        "b1": float(lm.coef_[0]),
        "r": r,
        "p": p,
        "r2_train": lm.score(X_train, y_train),
        "r2_test": lm.score(X_test, y_test),
        "mse": mse,
        "mae": mean_absolute_error(y_test, y_pred),
        "rmse": float(np.sqrt(mse)),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "test_pred": y_pred,
        "test_residual": (y_test.values - y_pred),
    }


def predict_salary(result: dict, value: float) -> float:
    """Dự đoán lương từ mô hình đã fit."""
    return result["b0"] + result["b1"] * value
