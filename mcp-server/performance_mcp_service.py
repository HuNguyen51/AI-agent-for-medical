# performance service
# Dịch vụ này giám sát hiệu suất kinh doanh liên tục và cung cấp cảnh báo khi cần thiết.
# Tính năng chính:
# Theo dõi các chỉ số KPI quan trọng như doanh thu, chi phí, lợi nhuận theo thời gian thực (qua track_kpi).
# Gửi cảnh báo khi phát hiện biến động hoặc xu hướng bất thường (sử dụng trigger_alert).
# Cung cấp báo cáo và dự báo hiệu suất để hỗ trợ đánh giá tình hình kinh doanh.
# Lợi ích: Giúp CEO nắm bắt sức khỏe doanh nghiệp tức thì và đưa ra biện pháp điều chỉnh kịp thời.

# Tool list
# get_kpi_data(kpi_name: str, department: str, time_frame: str) -> dict: Lấy dữ liệu KPI từ các hệ thống (ERP, CRM...).
# set_kpi_threshold(kpi_name: str, lower_bound: float, upper_bound: float, alert_recipient: str) -> bool: Thiết lập ngưỡng cảnh báo cho KPI.
# monitor_kpis(kpi_list: list) -> dict: Liên tục theo dõi danh sách KPIs.
# generate_performance_alert(kpi: str, current_value: float, threshold: float, details: str) -> bool: Gửi cảnh báo khi KPI vượt ngưỡng.
# create_realtime_dashboard(kpi_list: list) -> str: Tạo bảng điều khiển (dashboard) hiển thị KPIs theo thời gian thực.
# analyze_kpi_deviation(kpi_name: str, deviation: float) -> str: Phân tích nguyên nhân có thể gây ra sự lệch chuẩn của KPI.
# create_dashboard(kpis: list, layout: str) -> str: Tạo bảng điều khiển trực quan cho KPIs, trả về mã HTML hoặc URL.
# generate_report(summary: str, data: dict) -> pdf: Tạo báo cáo hiệu suất tổng hợp để trình bày cho CEO/board.
# predict_performance(metric_history: dict, period: int) -> dict: Dự đoán kết quả kinh doanh/kỹ thuật dựa trên dữ liệu quá khứ.