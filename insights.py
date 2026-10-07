import numpy as np
import pandas as pd
import analysis as an


def _number(value: float, digits: int = 0) -> str:
    return f"{value:,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _small_group_note(grouped: pd.DataFrame, column: str) -> str:
    """Nhắc khi bộ lọc khiến một nhóm quá nhỏ để so sánh chắc chắn."""
    smallest = grouped.loc[grouped["Count"].idxmin()]
    if smallest["Count"] < 30:
        return (f" Nhóm **{smallest[column]}** chỉ có **{_number(smallest['Count'])}** "
                "người, nên đọc chênh lệch của nhóm này thận trọng.")
    return ""


def _median_comparison(grouped: pd.DataFrame, column: str) -> str:
    high = grouped.loc[grouped["Median"].idxmax()]
    low = grouped.loc[grouped["Median"].idxmin()]
    if np.isclose(high["Median"], low["Median"]):
        return f"Các nhóm có cùng mức lương trung vị **{_number(high['Median'])}**."
    tied = grouped.loc[np.isclose(grouped["Median"], high["Median"]), column]
    if len(tied) == 1:
        leader = f"**{high[column]}**"
    elif len(tied) == 2:
        leader = f"**{tied.iloc[0]} và {tied.iloc[1]}**"
    else:
        leader = f"**{len(tied)} {'địa điểm' if column == 'Location' else 'nhóm'}**"
    return (f"{leader} có trung vị cao nhất (**{_number(high['Median'])}**), "
            f"cao hơn **{low[column]}** **{_number(high['Median'] - low['Median'])}**.")


def for_chart(chart_id: int, df: pd.DataFrame, reg: dict | None = None) -> str:
    """Nêu điều nổi bật và cách đọc biểu đồ, không suy diễn quan hệ nhân quả."""
    salary = df["Salary"]

    if chart_id == 1:
        q1, q3 = salary.quantile([0.25, 0.75])
        mean, median = salary.mean(), salary.median()
        relation = ("thấp hơn" if mean < median else "cao hơn" if mean > median
                    else "bằng")
        return (f"**50% nhân viên** nhận từ **{_number(q1)} đến {_number(q3)}**; "
                f"khoảng giữa rộng **{_number(q3 - q1)}**. Đường đứt nét là lương "
                f"trung bình **{_number(mean)}**, {relation} trung vị **{_number(median)}**. "
                "Trung vị ở dãy chỉ số phía trên là mức lương nằm giữa các nhân viên.")

    if chart_id == 2:
        counts = df["Department"].value_counts()
        if len(counts) == 1:
            return (f"Bộ lọc hiện chỉ còn **{counts.index[0]}** với "
                    f"**{_number(counts.iloc[0])} nhân viên**; hãy chọn thêm phòng ban để so quy mô.")
        largest, smallest = counts.index[0], counts.index[-1]
        return (f"**{largest}** đông nhất (**{_number(counts.iloc[0])} người**), "
                f"nhiều hơn **{smallest}** **{_number(counts.iloc[0] - counts.iloc[-1])} người**. "
                "Biểu đồ này cho biết quy mô mỗi phòng ban; đọc kèm biểu đồ lương để "
                "không nhầm số nhân viên với mức lương.")

    if chart_id == 3:
        grouped = an.group_salary(df, "Department")
        high = grouped.loc[grouped["Mean"].idxmax()]
        low = grouped.loc[grouped["Mean"].idxmin()]
        if len(grouped) == 1:
            return (f"Bộ lọc hiện chỉ còn **{high['Department']}** với lương trung bình "
                    f"**{_number(high['Mean'])}**; cần thêm phòng ban để so sánh.")
        top_median = grouped.loc[grouped["Median"].idxmax()]
        message = (f"**{high['Department']}** có lương trung bình cao nhất "
                   f"(**{_number(high['Mean'])}**), hơn **{low['Department']}** "
                   f"**{_number(high['Mean'] - low['Mean'])}**.")
        if top_median["Department"] != high["Department"]:
            message += (f" Nhưng **{top_median['Department']}** dẫn đầu về trung vị "
                        f"(**{_number(top_median['Median'])}**): thứ hạng đổi khi nhìn mức điển hình.")
        else:
            message += " Đây là số trung bình; xem thêm cột trung vị ở trang Phân tích lương để biết mức điển hình."
        return message + _small_group_note(grouped, "Department")

    if chart_id in (4, 5, 6, 7):
        column = {4: "Department", 5: "Job_Title", 6: "Education_Level",
                  7: "Location"}[chart_id]
        grouped = an.group_salary(df, column)
        if len(grouped) == 1:
            only = grouped.iloc[0]
            return (f"Bộ lọc chỉ còn **{only[column]}**. Trung vị là "
                    f"**{_number(only['Median'])}**; cần thêm nhóm để so sánh.")
        median_text = _median_comparison(grouped, column)
        if chart_id == 4:
            top_mean = grouped.loc[grouped["Mean"].idxmax()]
            top_median = grouped.loc[grouped["Median"].idxmax()]
            if top_mean[column] != top_median[column]:
                detail = (f"Trong khi đó, **{top_mean[column]}** dẫn đầu về trung bình. "
                          "Cột trung vị phù hợp hơn khi bạn muốn biết mức lương điển hình.")
            else:
                detail = ("Nhìn cả cột trung bình và trung vị: nếu hai cột cách xa nhau, "
                          "một số mức lương cao hoặc thấp đang kéo số trung bình.")
        elif chart_id == 5:
            high = grouped.loc[grouped["Median"].idxmax()]
            low = grouped.loc[grouped["Median"].idxmin()]
            detail = (f"Hai nhóm này lần lượt có **{_number(high['Count'])}** và "
                      f"**{_number(low['Count'])}** người; xem số người khi đánh giá "
                      "mức chênh giữa các chức danh.")
        elif chart_id == 6:
            detail = ("Đây là mức lương của các nhóm học vấn trong dữ liệu hiện có; "
                      "chức danh và kinh nghiệm có thể cũng khác nhau giữa các nhóm.")
        else:
            table = an.anova_table(df, ["Location"])
            if not table.empty and np.isfinite(table.iloc[0]["p-value"]):
                detail = ("Kiểm định chưa cho thấy khác biệt rõ ràng về lương trung bình "
                          "giữa các địa điểm." if table.iloc[0]["p-value"] >= 0.05 else
                          "Kiểm định cho thấy lương trung bình có khác biệt giữa ít nhất hai địa điểm.")
            else:
                detail = "Số liệu hiện tại chưa đủ để kiểm định chênh lệch trung bình giữa các địa điểm."
        return f"{median_text} {detail}" + _small_group_note(grouped, column)

    if chart_id == 8:
        grouped = df.groupby("Department")["Salary"]
        medians = grouped.median()
        spreads = grouped.quantile(0.75) - grouped.quantile(0.25)
        if len(medians) == 1:
            department = medians.index[0]
            return (f"Bộ lọc chỉ còn **{department}**. Trung vị là "
                    f"**{_number(medians.iloc[0])}**; phần thân hộp trải trên "
                    f"**{_number(spreads.iloc[0])}** và chứa 50% mức lương ở giữa.")
        widest = spreads.idxmax()
        return (f"**{medians.idxmax()}** có trung vị cao nhất (**{_number(medians.max())}**). "
                f"Hộp của **{widest}** rộng nhất: 50% mức lương giữa trải trên "
                f"**{_number(spreads[widest])}**. Hộp càng rộng, lương trong phòng ban "
                "càng khác nhau; điểm nằm ngoài râu là mức lương bất thường.")

    if chart_id == 9 and reg is not None:
        direction = "tăng" if reg["b1"] >= 0 else "giảm"
        return (f"Đường đen cho thấy mỗi năm kinh nghiệm tăng thêm gắn với lương "
                f"dự đoán **{direction} khoảng {_number(abs(reg['b1']))}**. "
                f"Trên tập kiểm tra, dự đoán lệch thực tế trung bình **{_number(reg['mae'])}**. "
                "Các chấm cùng số năm vẫn ở nhiều mức lương, nên đường chỉ thể hiện xu hướng chung.")

    if chart_id in (10, 13):
        column = "Experience_Group" if chart_id == 10 else "Age_Group"
        grouped = an.group_salary(df, column, sort_by_mean=False)
        high = grouped.loc[grouped["Mean"].idxmax()]
        low = grouped.loc[grouped["Mean"].idxmin()]
        if len(grouped) == 1:
            return (f"Bộ lọc chỉ còn nhóm **{high[column]}** với lương trung bình "
                    f"**{_number(high['Mean'])}**.")
        rising = np.all(np.diff(grouped["Mean"].to_numpy()) >= 0)
        trend = "Lương trung bình tăng qua từng nhóm. " if rising else ""
        message = (f"{trend}Nhóm **{high[column]}** có lương trung bình **{_number(high['Mean'])}**, "
                   f"cao hơn nhóm **{low[column]}** **{_number(high['Mean'] - low['Mean'])}**. ")
        if chart_id == 10:
            message += ("Các nhóm kinh nghiệm có khoảng năm khác nhau; đây là so sánh "
                        "giữa nhân viên, không phải mức tăng lương hằng năm của một người.")
        else:
            message += ("Đây là các nhóm nhân viên khác nhau, không phải mức tăng lương "
                        "của một người khi thêm tuổi.")
        return message + _small_group_note(grouped, column)

    if chart_id == 11 and reg is not None:
        pred, residual = reg["test_pred"], reg["test_residual"]
        high_mean = residual[pred >= np.quantile(pred, 0.8)].mean()
        if abs(high_mean) <= 0.25 * reg["rmse"]:
            high_text = ("Ở 20% mức dự đoán cao nhất, chênh lệch trung bình "
                         f"chỉ **{_number(abs(high_mean))}**.")
        else:
            direction = "cao hơn" if high_mean < 0 else "thấp hơn"
            high_text = ("Ở 20% mức dự đoán cao nhất, mô hình dự đoán "
                         f"**{direction} thực tế trung bình {_number(abs(high_mean))}**.")
        return ("Điểm dưới đường 0 nghĩa là mô hình dự đoán cao hơn lương thực tế; "
                f"điểm trên đường 0 là dự đoán thấp hơn. {high_text} "
                "Hãy xem vùng này khi dùng mô hình cho mức lương cao.")

    if chart_id == 12:
        slope, _ = np.polyfit(df["Age"], salary, 1)
        age_exp = df["Age"].corr(df["Experience_Years"])
        direction = "tăng" if slope >= 0 else "giảm"
        caveat = ("Tuổi và kinh nghiệm cũng đi cùng rất sát trong dữ liệu này, "
                  "nên không thể tách riêng ảnh hưởng của tuổi." if abs(age_exp) >= 0.8 else
                  "Biểu đồ chỉ cho thấy hai đại lượng đi cùng nhau, không chứng minh tuổi làm lương đổi.")
        return (f"Đường xu hướng cho thấy thêm một tuổi gắn với lương "
                f"**{direction} khoảng {_number(abs(slope))}** trong dữ liệu đang xem. {caveat}")

    if chart_id == 14:
        corr = df[["Age", "Experience_Years", "Salary"]].corr()
        age_exp = corr.loc["Age", "Experience_Years"]
        age_salary = corr.loc["Age", "Salary"]
        exp_salary = corr.loc["Experience_Years", "Salary"]
        closer = "tuổi" if abs(age_salary) >= abs(exp_salary) else "kinh nghiệm"
        if abs(age_exp) >= 0.8:
            caveat = ("Tuổi và kinh nghiệm cũng đi cùng rất mạnh "
                      f"(**r = {_number(age_exp, 2)}**), nên không thể gán "
                      "riêng chênh lệch lương cho một trong hai biến.")
        else:
            caveat = (f"Tuổi và kinh nghiệm có mức liên hệ **r = {_number(age_exp, 2)}**; "
                      "màu đậm thể hiện liên hệ mạnh, không chứng minh nguyên nhân.")
        return (f"Trong hai yếu tố, **{closer}** đi cùng lương sát hơn "
                f"(**r = {_number(max(abs(age_salary), abs(exp_salary)), 2)}**). {caveat}")

    raise ValueError(f"Chưa có nhận xét cho biểu đồ {chart_id}")
