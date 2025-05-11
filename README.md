**Agents Server**

Dự án này cung cấp một server local để tạo agent sử dụng RAG và trả lời câu hỏi dựa trên tài liệu liên quan.

**Cài đặt**

Để cài đặt dự án, bạn cần có Python 3.10.9 và các thư viện sau:

* `transformers` để tạo mô hình ngôn ngữ.
* `langchain` để tạo retriever và chuỗi xử lý.

**Chức năng chính**

Dự án này cung cấp hai chức năng chính:

* Tạo agent sử dụng RAG để trả lời câu hỏi dựa trên tài liệu liên quan.
* Tạo server local để tương tác với agent.
* `main.ipynb` chứa code để tạo agent sử dụng RAG, bao gồm:
	+ Tạo mô hình ngôn ngữ từ server.
	+ Tạo retriever để truy hồi tài liệu liên quan.
	+ Tạo chuỗi xử lý để kết hợp tài liệu và trả lời câu hỏi.
* `Chat.py` chứa code để tạo đối tượng Chat, bao gồm:
	+ Khởi tạo đối tượng Chat với mô hình ngôn ngữ, retriever và câu prompt.
	+ Định nghĩa các chuỗi xử lý để tạo truy vấn tìm kiếm và kết hợp tài liệu.

**Cách sử dụng**

Để sử dụng dự án, bạn cần thực hiện các bước sau:

1. Cài đặt các thư viện cần thiết.
2. Chạy file `server.py` để load các mô hình ngôn ngữ và tương tác với agent.
3. Chạy file `main.ipynb` để tạo agent sử dụng RAG (Retrieval-Augmented Generation) tương tác với documents.

**Lưu ý**

Dự án này vẫn đang trong quá trình phát triển và có thể có một số lỗi hoặc hạn chế.

Hy vọng file README này sẽ giúp bạn hiểu rõ hơn về dự án và cách sử dụng nó.