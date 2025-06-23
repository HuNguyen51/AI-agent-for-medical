# AI Agent to Agents

Dự án Agents là hệ thống đa tác nhân A2A (Google: Agent-to-Agent) được thiết kế để cộng tác trong các tác vụ của người dùng. Dự án sử dụng Retrieval- Augmented Generation (RAG) làm công cụ để truy vấn dữ liệu và trả lời câu hỏi, và MCP để xác định và tích hợp các công cụ có thể truy cập vào LLM và agent.

[*Đang ở giai đoạn đầu phân tích và phát triển...*]

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

Dưới đây là cách chạy một agent cụ thể sử dụng langgraph:

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