# knowlegge service
# Dịch vụ này quản lý và tối ưu hóa việc truy xuất thông tin nội bộ cũng như cập nhật kiến thức từ bên ngoài.
# Tính năng chính:
# Tổ chức, tìm kiếm và truy xuất thông tin từ tài liệu, email, cuộc họp (qua search_documents) và cập nhật tin tức ngành, đối thủ (qua get_latest_news).
# Quản lý tập trung tài liệu công ty, tự động phân loại và gán thẻ tệp trong Google Drive, đồng thời tóm tắt nội dung.
# Cải thiện tìm kiếm bằng ngôn ngữ tự nhiên và tạo cơ sở tri thức có thể truy vấn nhanh.
# Lợi ích: Tiết kiệm thời gian tìm kiếm, đảm bảo thông tin được lưu trữ hiệu quả và luôn cập nhật.

# Tool list
# search_internal_kb(query: str, filters: dict) -> list: Tìm kiếm thông tin trong cơ sở tri thức nội bộ (tài liệu, email, họp...). Sử dụng RAG tại đây.
# retrieve_document_content(doc_id: str) -> str: Lấy nội dung chi tiết của một tài liệu.
# summarize_text(text: str, length: str) -> str: Tóm tắt văn bản (ngắn, trung bình, dài).
# track_news_feed(keywords: list, sources: list) -> list: Theo dõi và lấy tin tức từ các nguồn được chỉ định.
# get_competitor_updates(company_name: str) -> list: Cập nhật thông tin về đối thủ cạnh tranh.
# index_information(content: str, metadata: dict) -> bool: Lưu trữ và lập chỉ mục thông tin mới vào KB.
# answer_faq_rag(query: str) -> str: Trả lời câu hỏi dựa trên dữ liệu riêng tư (RAG).
# get_latest_news(industry: str, date_range: str) -> list: Thu thập tin tức ngành mới nhất từ nguồn công khai hoặc API.
# categorize_files(files: List[str]) -> dict: Phân loại tài liệu theo loại (hợp đồng, báo cáo, hướng dẫn...).
# tag_document(document: str, tags: List[str]) -> bool: Gán thẻ (tags) cho tài liệu để dễ dàng tìm kiếm trong tương lai.