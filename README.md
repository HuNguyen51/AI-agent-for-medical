# AI Agents for CEO

Dự án Agents là hệ thống đa tác nhân A2A (Agent-to- Agent) được thiết kế để cộng tác trong các tác vụ của người dùng. Dự án sử dụng Retrieval- Augmented Generation (RAG) làm công cụ để truy vấn dữ liệu riêng tư và trả lời câu hỏi, và MCP để xác định và tích hợp các công cụ có thể truy cập vào LLM và tác nhân.

Hệ thống này sử dụng AI hỗ trợ CEO tối ưu hóa công việc thông qua phân tích dữ liệu, ra quyết định chiến lược, quản lý thông tin, giao tiếp hiệu quả, tự động hóa tác vụ và giám sát hiệu suất doanh nghiệp theo thời gian thực. Cung cấp cái nhìn toàn diện, tiết kiệm thời gian, nâng cao hiệu quả ra quyết định và phản ứng nhanh với sự đổi mới. Phân tích thông tin và cung cấp tư vấn chiến lược dựa trên kinh nghiệm mô phỏng từ các CEO hàng đầu, hỗ trợ giải quyết tình huống phức tạp.

Lợi ích: Tăng khả năng dự đoán, cải thiện đàm phán, nâng cao lãnh đạo, và tối ưu giao tiếp nội bộ.

[*Đang ở giai đoạn đầu phân tích và phát triển...*]

## Mục tiêu dự án là:
1. Trợ lý Phân tích Dữ liệu và Cung cấp Thông tin Chi tiết:

Tự động thu thập, tổng hợp, phân tích dữ liệu từ nhiều nguồn khác nhau (báo cáo tài chính, dữ liệu bán hàng, thị trường, đối thủ, tin tức...). Xác định xu hướng, mối tương quan, các điểm bất thường và tạo báo cáo tóm tắt hoặc trực quan hóa dễ hiểu.

2. Trợ lý Hỗ trợ Ra quyết định Chiến lược:

Phân tích các kịch bản khác nhau dựa trên dữ liệu đầu vào, dự báo kết quả tiềm năng của các chiến lược khác nhau, đánh giá rủi ro liên quan đến từng lựa chọn. Có thể sử dụng các mô hình mô phỏng.

3. Trợ lý Quản lý Thông tin và Kiến thức:

Tổ chức, tìm kiếm và truy xuất thông tin nội bộ (tài liệu, email, biên bản họp...) một cách hiệu quả. Tóm tắt các tài liệu dài, bài báo hoặc chuỗi email. Cập nhật tin tức ngành và các thông tin liên quan đến công ty/đối thủ theo thời gian thực.

4. Trợ lý Giao tiếp và Soạn thảo Nội dung:

Hỗ trợ soạn thảo email, thư từ, bài phát biểu, thông cáo báo chí hoặc bản nháp tài liệu. Phân tích sắc thái cảm xúc trong các trao đổi (ví dụ: phản hồi của khách hàng, bình luận trên mạng xã hội). Hỗ trợ dịch thuật nhanh chóng.

5. Trợ lý Quản lý Lịch trình và Tự động hóa Tác vụ:

Quản lý lịch họp phức tạp, tự động sắp xếp các cuộc hẹn dựa trên sự rảnh rỗi của các bên, nhắc nhở lịch trình. Tự động hóa các tác vụ lặp đi lặp lại như gửi báo cáo định kỳ, tổng hợp dữ liệu từ các nguồn cơ bản.

6. Trợ lý Giám sát Hiệu suất Doanh nghiệp:

Liên tục theo dõi các chỉ số hiệu suất chính (KPIs) trên toàn bộ doanh nghiệp, cảnh báo ngay lập tức khi có chỉ số đi chệch mục tiêu hoặc có dấu hiệu bất thường ở bất kỳ bộ phận nào.
Tại sao hữu ích cho CEO: Cho phép CEO có cái nhìn tổng quan theo thời gian thực về sức khỏe của doanh nghiệp và nhanh chóng can thiệp khi cần thiết.

## Cấu trúc dự án
Chúng ta có 3 thư mục quan trọng:

* [**Common**](/common)  
Code để các agents và apps sử dụng để giao tiếp A2A thông qua HTTP.

* [**Agents**](/agents/README.md)  
Các AI Agents thực hiện các chức năng riêng biệt sử dụng nhiều framework khác nhau để thực hiện nhiệm vụ của nó bằng các tool khác nhau. Tất cả sử dụng common A2AServer.

* [**Hosts**](/hosts/README.md)  
Ứng dụng host sử dụng A2AClient. Bao gồm CLI hiển thị hoàn thành nhiệm vụ đơn giản với một agent, ứng dụng web mesop giao tiếp với nhiều agent, và orchestrator agent chuyển giao nhiệm vụ cho một trong nhiều remote A2A agent.

Các thư mục phụ trợ như:

- **db-server**: Dùng để tạo vector database từ dữ liệu người dùng cho mục đích tăng cường dữ liệu tuỳ chỉnh cho các phản hồi.
- **llm-server**: Dùng để load local model cho phép client tương tác với server bằn OpenAI API.

## Prerequisites

- Python 3.13 hoặc cao hơn
- [UV](https://docs.astral.sh/uv/)

## Khởi chạy các Agents

Chạy một (hoặc nhiều) [agent](/agents/README.md) A2A server và [demo web ui](/demo/README.md) với [host applications](/hosts/README.md). 

Dưới đây là cách chạy một agent cụ thể sử dụng langgraph là personal_info_agent:

1. Thư mục hiện hành sẽ là thư mục gốc.

2. Tạo file môi trường chứa API_KEY:

   ```bash
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```

3. Chạy Agent:

   ```bash
   python agent-server/__main__.py
   ```

  Url và port tuỳ vào configs/*-agent.yaml. Ví dụ: http://localhost:10000

4. Chạy [UI](/demo/README.md) để tương tác với các Agents :

   ```bash
   python demo/ui/main.py
   ```

Có thể dụng `uv run .` thay cho `python <file>.py` trong quá trình sử dụng.


## Lưu ý

Dự án này vẫn đang trong quá trình phát triển và có thể có một số lỗi hoặc hạn chế.

Hy vọng file README này sẽ giúp bạn hiểu rõ hơn về dự án và cách sử dụng nó.

Nhiều module dựa trên nển tảng Google A2A.