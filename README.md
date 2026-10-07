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
├── charts.py           # Các hàm vẽ 14 biểu đồ Plotly
├── insights.py         # Nhận xét riêng cho từng biểu đồ theo bộ lọc
├── data/Employers_data.csv
├── .streamlit/config.toml
└── requirements.txt
```
