# analytics service
# Dịch vụ này tập trung vào việc thu thập, phân tích và trực quan hóa dữ liệu để hỗ trợ ra quyết định dựa trên thông tin thực tế.
# Tính năng chính:
# Tự động thu thập, tích hợp và làm sạch dữ liệu từ nhiều nguồn như tài chính, bán hàng, thị trường, tin tức (qua fetch_financial_data).
# Phân tích xu hướng, mối tương quan và phát hiện điểm bất thường, sau đó trình bày dưới dạng báo cáo chi tiết hoặc biểu đồ trực quan (sử dụng create_visualization).
# Cung cấp các chỉ số KPI theo thời gian thực như doanh thu, chi phí, lợi nhuận.
# Lợi ích: Giúp CEO có cái nhìn toàn diện về tình hình kinh doanh, nhận diện cơ hội và rủi ro kịp thời.

# Tool list
# collect_data(source_type: str, parameters: dict) -> DataFrame: Thu thập dữ liệu từ các nguồn (API, database, file, web). source_type có thể là 'sales_db', 'finance_report', 'market_api', 'news_rss', 'web_scrape'.
# integrate_data(data_list: list) -> DataFrame: Hợp nhất dữ liệu từ nhiều nguồn khác nhau.
# clean_data(data: DataFrame) -> DataFrame: Làm sạch và tiền xử lý dữ liệu.
# identify_trends(data: DataFrame, time_column: str, value_column: str) -> dict: Phân tích xu hướng theo thời gian.
# detect_anomalies(data: DataFrame, column: str, method: str) -> list: Phát hiện các điểm bất thường.
# calculate_correlations(data: DataFrame) -> DataFrame: Tính toán mối tương quan giữa các biến.
# calculate_profit(data: DataFrame) -> float: Tính toán lợi nhuận.
# generate_summary_report(analysis_results: dict, format: str) -> str: Tạo báo cáo tóm tắt (text, pdf).
# create_visualization(data: DataFrame, chart_type: str, x_axis: str, y_axis: str) -> str: Tạo biểu đồ trực quan hóa (line, bar, pie...).

