# Web phân tích và trực quan hóa dữ liệu lương nhân viên

Viết hoàn toàn bằng Python: Streamlit (giao diện web), pandas (xử lý dữ liệu),
Plotly (biểu đồ), SciPy (Pearson, ANOVA), scikit-learn (hồi quy tuyến tính).

## Cách chạy

```bash
pip install -r requirements.txt
streamlit run app.py
```

Trình duyệt sẽ mở tại http://localhost:8501

## Cấu trúc

```
salary_app/
├── app.py              # Giao diện: sidebar, 3 dashboard, bộ lọc
├── analysis.py         # Tiền xử lý, thống kê, ANOVA, hồi quy
├── charts.py           # 13 biểu đồ Plotly
├── data/Employers_data.csv
├── .streamlit/config.toml
└── requirements.txt
```

## Đối chiếu với slide bài giảng

| Phần trong web | Kiến thức | Bài |
|---|---|---|
| Đọc CSV, bảng kiểu dữ liệu, `head()`, tải CSV | Nhập/xuất dữ liệu, `dtypes`, `info()` | Bài 1 |
| `clean_data()`: xử lý "?", "N/A", dropna, fillna mean/mode, `pd.cut` | Tiền xử lý, binning | Bài 2 |
| Histogram, bar, bar ngang, boxplot, scatter, heatmap | Chọn biểu đồ theo mục đích | Bài 3, 4 |
| Web dashboard bằng Streamlit | Data Dashboard | Bài 4 |
| Mode, Std, IQR, CV, Skewness, Kurtosis, ngoại lệ | Thống kê mô tả | Bài 5 |
| `groupby`, Pearson r + p-value, ANOVA, ma trận tương quan | Gom nhóm, tương quan, ANOVA | Bài 5 |
| Salary = b0 + b1 × Experience_Years, residual plot, R² | Hồi quy tuyến tính | Bài 6 |
| Train/test 70/30, R² train/test, MAE, RMSE | Đánh giá mô hình | Bài 7 |

## Dùng file dữ liệu khác

Tải file CSV ở thanh bên. File cần có các cột:
`Age, Gender, Department, Job_Title, Experience_Years, Education_Level, Location, Salary`.
