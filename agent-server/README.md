## Prerequisites

- Python 3.13 hoặc cao hơn
- [UV](https://docs.astral.sh/uv/)
- API Key cho LLM

## Setup & Running

1. Thư mục hiện hành sẽ là thư mục gốc.

2. Tạo file môi trường chứa API_KEY:

   ```bash
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```

3. Chạy Agent:

   ```bash
   python agents-server/__main__.py
   ```

  Url và port tuỳ vào `configs/*-agent.yaml`. Ví dụ: http://localhost:10000

  Có nhiều Agent thì sẽ chạy nhiều file với các host và port khác nhau.

4. Chạy [UI](/demo/README.md) để tương tác với các Agents :

   ```bash
   python demo/ui/main.py
   ```

Có thể dụng `uv run .` thay cho `python <file>.py` trong quá trình sử dụng.