## Demo Web App

Ứng dụng demo này trình bày việc một Host Agent điều hướng tác vụ đến các Remote Agent để thực hiện tác vụ nào đó trên giao thức A2A.

![image](./a2a_demo_arch.png)

- Frontend là [mesop](https://github.com/mesop-dev/mesop) web application tạo ra cuộc hội thoại giữa người dùng cuối và "Host Agent". Ứng dụng này có thể tạo ra nội dung text, thought bubbles, web forms (yêu cầu bổ sung dữ liệu từ agents), và hình ảnh. Các kiểu dữ nội dung khác sẽ sớm được cập nhật,

- **Host Agent** là Google ADK agent có khả năng điều hướng user requests đến các Remote Agents.

- Mỗi **Remote Agent** là một A2AClient chạy trong Google ADK agent. Mỗi remote agent sẽ lấy A2AServer's [AgentCard](https://google.github.io/A2A/#documentation?id=agent-card) và uỷ quyền tất cả requests bằng A2A.

## Features

<need quick gif>

### Thêm Agent một cách linh hoạt

Clicking on the robot icon in the web app lets you add new agents. Enter the address of the remote agent's AgentCard and the app will fetch the card and add the remote agent to the local set of known agents.
Nhấp vào biểu tượng robot trong ứng dụng web cho phép bạn thêm các Agent mới. Nhập địa chỉ AgentCard của remote agent và ứng dụng sẽ lấy card và thêm remote agent đó vào danh sách các agents cục bộ.

### Giao tiếp với một hoặc nhiều Agents

Nhấn vào nút chat để bắt đầu hoặc tiếp tục một cuộc trò chuyện hiện có. Cuộc trò chuyện này sẽ được gửi đến Host Agent, sau đó Host Agent sẽ chuyển giao yêu cầu cho một hoặc nhiều remote agent.

Nếu agent trả về nội dung phức tạp - như hình ảnh hoặc web-form - frontend sẽ hiển thị nội dung này trong giao diện trò chuyện. Remote Agent sẽ đảm nhiệm việc chuyển đổi nội dung này giữa A2A và ứng dụng của web apps.

### Khám phá A2A tasks

Nhấn vào lịch sử để xem các tin nhắn được gửi giữa web app và tất cả các agent (Host agent và Remote agent).

Nhấn vào danh sách tasks để xem tất cả các cập nhật A2A tasks từ các remote agent.

## Prerequisites

- Python 3.12 hoặc cao hơn
- UV
- [Agent servers](/agents/README.md) giao tiếp A2A 
- Authentication credentials (API Key hoặc Vertex AI)

## Running the Examples

1. Điều hướng đến thư mục giao diện demo:
   ```bash
   cd demo/ui
   ```
2. Tạo file môi trường chứa API_KEY:

   ```bash
   echo "GOOGLE_API_KEY=your_api_key_here" > .env
   ```

3. Chạy giao diện demo:

   ```bash
  python ./main.py
   ```

   Note: ứng dụng chạy mặc định ở cổng 12000.

4. Tương tác với demo UI, và thêm các Agents.

Vào thư mục `agents` để chọn agent muốn thêm, và chạy file `__main__.py` trong đó như [hướng dẫn chạy agents](/agents/README.md)

Quay lại demo UI, chọn _Remote Agents_ có hình biểu tượng robot, và thêm agent và nhập địa URL của remote agent. Màn hình sẽ hiển thị các thông tin trong Agent's Card.

Sau đó bạn có thể trò chuyện với các agent và nó có thể truy cập và remote agent để thực hiện các chức năng của remote agent.

Bạn có thể review các sự kiện diễn ra trong quá trình trò truyện để xem việc điều hướng của Host Agent, việc thực hiện tác vụ của các Remote Agent cũng như cách các Agent tương tác với nhau.


Có thể dụng `uv run .` thay cho `python file.py` trong quá trình sử dụng.