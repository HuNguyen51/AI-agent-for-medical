## Hosts

Ứng dụng mẫu hoặc agent là A2A client hoạt động với A2A server.

* [CLI](/hosts/cli)  
  Công cụ dòng lệnh để tương tác với A2A server. Chỉ định địa chỉ server trên dòng lệnh. CLI client tìm kiếm agent card và thực hiện hoàn thành nhiệm vụ trong một vòng lặp dựa trên đầu vào dòng lệnh.

* [Orchestrator Agent](/hosts/multiagent)  
Agent giao tiếp A2A và có thể chuyển giao nhiệm vụ cho remote agent. Được xây dựng trên Google ADK cho mục đích trình diễn. Bao gồm một "Host Agent" duy trì tập hợp các "Remote Agent". Host Agent bản thân nó là một agent và có thể chuyển giao nhiệm vụ cho một hoặc nhiều Remote Agent. Mỗi Remote Agent là một A2AClient chuyển giao đến A2A Server.

* [MultiAgent Web Host](/demo/README.md)  
*Nằm trong đường dẫn [demo](/demo/README.md)*  
Ứng dụng web hiển thị trực quan các cuộc trò chuyện A2A với nhiều agent (sử dụng [Orchestrator Agent](/hosts/multiagent)). Hiển thị văn bản, hình ảnh và webform artifact. Có tab riêng để trực quan hóa trạng thái nhiệm vụ, lịch sử và các agent card đã biết.