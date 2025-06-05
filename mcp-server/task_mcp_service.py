# task service
# Dịch vụ này tự động hóa và quản lý lịch trình, giảm tải công việc thủ công hàng ngày.
# Tính năng chính:
# Quản lý lịch trình phức tạp, kết nối với Google Calendar để lập lịch họp, tạo sự kiện, gửi lời mời và đặt nhắc nhở hạn chót (qua find_available_slots).
# Tự động hóa các tác vụ lặp lại như tạo báo cáo định kỳ (sử dụng generate_periodic_report) và nhắc nhở công việc quan trọng.
# Quản lý lịch cá nhân theo thời gian thực.
# Lợi ích: Tiết kiệm thời gian, tăng hiệu suất làm việc và đảm bảo không bỏ lỡ các nhiệm vụ quan trọng.

# Tool list
# check_calendar_availability(attendees: list, start_time: str, end_time: str) -> list: Kiểm tra lịch trống của những người tham gia.
# schedule_meeting(topic: str, attendees: list, duration_minutes: int, preferences: dict) -> dict: Tự động tìm và đặt lịch họp phù hợp.
# set_reminder(event: str, remind_time: str, recipient: str) -> bool: Đặt lời nhắc.
# create_automation_workflow(trigger: dict, actions: list) -> str: Tạo một luồng công việc tự động (ví dụ: khi có email X, tóm tắt và gửi cho Y).
# execute_scheduled_task(task_id: str) -> dict: Thực thi một tác vụ đã được lên lịch (ví dụ: gửi báo cáo).
# prioritize_tasks(task_list: list, criteria: dict) -> list: Sắp xếp thứ tự ưu tiên cho công việc.
# generate_periodic_report(data_source: str, period: str) -> str: Tạo báo cáo định kỳ từ nguồn dữ liệu, hỗ trợ định dạng văn bản.

