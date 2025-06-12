# # Communicates service
# Dịch vụ này hỗ trợ giao tiếp hiệu quả trong nội bộ và với bên ngoài thông qua các công cụ soạn thảo và phân tích thông minh.
# Tính năng chính:
# Hỗ trợ soạn thảo các loại văn bản giao tiếp như email, bài phát biểu, báo cáo, thông cáo với văn phong phù hợp.
# Phân tích sắc thái cảm xúc (qua công cụ perform_sentiment_analysis) và cung cấp dịch thuật để cải thiện chất lượng giao tiếp.
# Tự động xử lý email và văn bản: phân loại, tóm tắt nội dung và tạo bản nháp phản hồi (sử dụng generate_email_template).
# Lợi ích: Đảm bảo thông điệp được truyền tải chính xác, đến đúng người, tiết kiệm thời gian và nâng cao hiệu quả giao tiếp.

# # Tool list
# draft_communication(comm_type: str, audience: str, tone: str, key_points: list) -> dict: Soạn thảo nội dung (email, speech, press_release).
# proofread_and_edit(text: str) -> dict: Kiểm tra lỗi chính tả, ngữ pháp và đề xuất cải thiện văn phong.
# analyze_sentiment(text: str) -> dict: Phân tích sắc thái cảm xúc (tích cực, tiêu cực, trung tính) và các cảm xúc chính.
# translate_text(text: str, target_language: str, source_language: str = 'auto') -> dict: Dịch văn bản sang ngôn ngữ khác.
# generate_talking_points(topic: str, context: str) -> list: Tạo các ý chính cho một cuộc thảo luận hoặc bài phát biểu.

import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime

# =============================================================================
# MCP SERVER
# =============================================================================

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    name = "comms-mcp-server"
)

# Constants
# USER_AGENT = "comms-app/1.0"

# =============================================================================
# COMMUNICATION SERVICE FUNCTIONS
# =============================================================================

llm_client = None

# Viết email
@mcp.tool()
def draft_communication(comm_type: str, audience: str, tone: str, key_points: list[str]) -> dict:
    
    """
    Soạn thảo nội dung giao tiếp bằng LLM dựa trên các điểm chính.
    
    Args:
        comm_type: Loại văn bản ('email', 'speech', 'press_release', 'report')
        audience: Đối tượng nhận ('internal', 'customers', 'media', 'stakeholders')
        tone: Giọng điệu ('formal', 'casual', 'professional', 'friendly')
        key_points: Danh sách các điểm chính cần truyền tải
        llm_client: Client để gọi LLM
    
    Returns:
        dict: Nội dung đã được soạn thảo bởi LLM
    """

    # Tạo prompt chi tiết cho LLM
    prompt = f"""
Hãy soạn thảo một {comm_type} chuyên nghiệp với các yêu cầu sau:

THÔNG TIN CHUNG:
- Loại văn bản: {comm_type}
- Đối tượng: {audience}  
- Giọng điệu: {tone}
- Ngày: {datetime.now().strftime("%d/%m/%Y")}

CÁC ĐIỂM CHÍNH CẦN TRUYỀN TẢI:
{chr(10).join([f"• {point}" for point in key_points])}

YÊU CẦU CỤ THỂ:

1. ĐỐI VỚI EMAIL:
   - Có dòng chủ đề phù hợp
   - Lời chào phù hợp với tone
   - Nội dung được tổ chức rõ ràng theo các điểm chính
   - Lời kết thúc lịch sự
   - Chữ ký [Tên người gửi]

2. ĐỐI VỚI SPEECH (Bài phát biểu):
   - Mở đầu thu hút
   - Phát triển từng ý một cách logic
   - Sử dụng ngôn ngữ phù hợp để thuyết trình
   - Kết thúc ấn tượng

3. ĐỐI VỚI PRESS_RELEASE (Thông cáo báo chí):
   - Tiêu đề nổi bật
   - Lead paragraph tóm tắt toàn bộ nội dung
   - Body paragraphs chi tiết từng điểm
   - Thông tin liên hệ cuối

4. ĐỐI VỚI REPORT (Báo cáo):
   - Tiêu đề và thông tin meta
   - Executive summary
   - Phân tích chi tiết từng điểm
   - Kết luận và khuyến nghị

STYLE GUIDELINES:
- Tone {tone}: {"Trang trọng, lịch sự" if tone == "formal" else "Thân thiện, gần gũi" if tone == "casual" else "Chuyên nghiệp, rõ ràng" if tone == "professional" else "Ấm áp, thân mật"}
- Sử dụng ngôn ngữ phù hợp với audience: {audience}
- Đảm bảo nội dung súc tích nhưng đầy đủ thông tin
- Tránh lặp lại, đảm bảo mạch lạc

Hãy tạo ra một văn bản hoàn chỉnh, chuyên nghiệp và hiệu quả.
"""
    
    if llm_client:
        try:
            response = llm_client.invoke(prompt)
            return {
                "status": "success",
                "code": 1,
                "note": {"type": "text"},
                "response": response, 
            }
        except Exception as e:
            return {
                "status": "failed",
                "code": 11,
                "note": f"Lỗi khi gọi LLM: {str(e)}", 
                "prompt": prompt
            }
    else:
        return {
            "status": "failed",
            "code": 12,
            "note": "Cần tích hợp LLM client để tạo nội dung chất lượng cao. Sử dụng prompt này với LLM khác để có được nội dung {comm_type} chuyên nghiệp",
            "prompt": prompt,
        }

# sửa chính tả 
@mcp.tool()
def proofread_and_edit(text: str) -> dict:
    """
    Kiểm tra lỗi chính tả, ngữ pháp và đề xuất cải thiện văn phong bằng LLM.
    
    Args:
        text: Văn bản cần kiểm tra
        llm_client: Client để gọi LLM
    
    Returns:
        dict: Kết quả kiểm tra và đề xuất cải thiện chi tiết
    """
    
    prompt = f"""
Bạn là một biên tập viên chuyên nghiệp. Hãy kiểm tra và phân tích văn bản sau một cách toàn diện:

VĂN BẢN CẦN KIỂM TRA:
\"\"\"
{text}
\"\"\"

NHIỆM VỤ CỦA BẠN:

1. KIỂM TRA LỖI CHÍNH TẢ VÀ NGỮ PHÁP:
   - Tìm và sửa tất cả lỗi chính tả
   - Sửa lỗi ngữ pháp, cú pháp
   - Kiểm tra dấu câu, viết hoa, viết thường
   - Kiểm tra cách sử dụng từ ngữ

2. PHÂN TÍCH VĂN PHONG:
   - Đánh giá độ rõ ràng, mạch lạc
   - Kiểm tra tính nhất quán về tone
   - Phát hiện câu dài, phức tạp cần đơn giản hóa
   - Tìm từ ngữ có thể thay thế tốt hơn

3. ĐỀ XUẤT CẢI THIỆN:
   - Cải thiện cấu trúc câu
   - Đề xuất từ ngữ chính xác hơn
   - Tối ưu hóa độ dài đoạn văn
   - Nâng cao tính thuyết phục

4. KIỂM TRA LOGIC VÀ LUỒNG Ý:
   - Đảm bảo ý tưởng được trình bày logic
   - Kiểm tra sự chuyển tiếp giữa các ý
   - Đánh giá tính đồng nhất của thông điệp

Hãy trả về kết quả ĐẦY ĐỦ theo định dạng JSON sau:

{{
    "văn_bản_gốc": "...",
    "văn_bản_đã_chỉnh_sửa": "...",
    "tóm_tắt_thay_đổi": "Mô tả ngắn gọn những gì đã được cải thiện",
    "lỗi_chính_tả_ngữ_pháp": [
        {{"lỗi": "...", "sửa_thành": "...", "giải_thích": "..."}}
    ],
    "cải_thiện_văn_phong": [
        {{"vấn_đề": "...", "đề_xuất": "...", "lý_do": "..."}}
    ],
    "điểm_mạnh": ["...", "..."],
    "điểm_cần_cải_thiện": ["...", "..."],
    "đánh_giá_tổng_thể": {{
        "độ_rõ_ràng": "điểm_từ_1_đến_10",
        "tính_chuyên_nghiệp": "điểm_từ_1_đến_10",
        "tác_động": "điểm_từ_1_đến_10"
    }},
    "khuyến_nghị_tiếp_theo": ["...", "..."]
}}

Hãy phân tích KỸ LƯỠNG và đưa ra phản hồi CHI TIẾT, CHÍNH XÁC.
"""
    
    if llm_client:
        try:
            response = llm_client.invoke(prompt)
            try:
                response = json.loads(response) if isinstance(response, str) else response
                return {
                    "status": "success",
                    "code": 0,
                    "note": {"type": "json"},
                    "response": response
                }
            except:
                return {
                    "status": "success",
                    "code": 1,
                    "note": {"type": "text"},
                    "response": response, 
                }
        except Exception as e:
            return {
                "status": "failed",
                "code": 11,
                "note": f"Lỗi khi gọi LLM: {str(e)}", 
                "prompt": prompt
            }
    else:
        return {
            "status": "failed",
            "code": 12,
            "note": "Cần tích hợp LLM client để có phân tích chính xác. Sử dụng prompt trên với LLM khác để có phân tích chi tiết và chuyên nghiệp.",
            "prompt": prompt,
            "more_info": {
                "số từ": {len(text.split())},
                "số câu": {len(re.split(r'[.!?]+', text.strip()))},
                "các lỗi có thể": {_quick_basic_check(text)}
            },
        }

def _quick_basic_check(text: str) -> list:
    """Kiểm tra cơ bản nhanh khi không có LLM."""
    issues = []
    if re.search(r'\s+([,.!?;:])', text):
        issues.append("Khoảng trắng thừa trước dấu câu")
    if re.search(r'([,.!?;:])[a-zA-ZÀ-ỹ]', text):
        issues.append("Thiếu khoảng trắng sau dấu câu")
    if len([s for s in text.split('.') if len(s.split()) > 30]) > 0:
        issues.append("Có câu quá dài, nên chia nhỏ")
    return issues

# phân tích cảm xúc
@mcp.tool()
def analyze_sentiment(text: str) -> dict:
    """
    Phân tích sắc thái cảm xúc chi tiết bằng LLM.
    
    Args:
        text: Văn bản cần phân tích
        llm_client: Client để gọi LLM
    
    Returns:
        dict: Kết quả phân tích cảm xúc chi tiết
    """
    
    prompt = f"""
Bạn là một chuyên gia phân tích cảm xúc và ngôn ngữ học. Hãy phân tích TOÀN DIỆN cảm xúc và sắc thái của văn bản sau:

VĂN BẢN CẦN PHÂN TÍCH:
\"\"\"
{text}
\"\"\"

PHÂN TÍCH CHI TIẾT:

1. SENTIMENT TỔNG THỂ:
   - Xác định sentiment chính: tích_cực/tiêu_cực/trung_tính
   - Đo độ tin cậy (0.0-1.0)
   - Giải thích căn cứ đánh giá

2. PHÂN TÍCH CẢM XÚC CHI TIẾT:
   - Vui mừng, hạnh phúc (0.0-1.0)
   - Buồn bã, thất vọng (0.0-1.0)  
   - Tức giận, khó chịu (0.0-1.0)
   - Lo lắng, căng thẳng (0.0-1.0)
   - Hài lòng, tin tưởng (0.0-1.0)
   - Ngạc nhiên, bất ngờ (0.0-1.0)
   - Sợ hãi, lo sợ (0.0-1.0)
   - Thờ ơ, trung lập (0.0-1.0)

3. PHÂN TÍCH NGÔN NGỮ:
   - Tone giọng điệu (formal, casual, aggressive, polite, etc.)
   - Mức độ lịch sự (1-10)
   - Mức độ tự tin (1-10)
   - Mức độ khách quan (1-10)

4. PHÂN TÍCH NGỮ CẢNH:
   - Ý định của người viết
   - Mối quan hệ với người nhận (suy đoán)
   - Bối cảnh có thể (công việc, cá nhân, etc.)

5. TỪ KHÓA VÀ CỤM TỪ CẢM XÚC:
   - Liệt kê các từ/cụm từ thể hiện cảm xúc mạnh
   - Phân loại theo tích cực/tiêu cực/trung tính

Trả về kết quả theo định dạng JSON CHÍNH XÁC:

{{
    "sentiment_tổng_thể": "tích_cực/tiêu_cực/trung_tính",
    "độ_tin_cậy": 0.xx,
    "điểm_sentiment": {{
        "tích_cực": xx,
        "tiêu_cực": xx,
        "trung_tính": xx
    }},
    "cảm_xúc_chi_tiết": {{
        "vui_mừng": 0.xx,
        "buồn_bã": 0.xx,
        "tức_giận": 0.xx,
        "lo_lắng": 0.xx,
        "hài_lòng": 0.xx,
        "thất_vọng": 0.xx,
        "ngạc_nhiên": 0.xx,
        "sợ_hãi": 0.xx,
        "thờ_ơ": 0.xx
    }},
    "phân_tích_ngôn_ngữ": {{
        "tone_giọng_điệu": "...",
        "mức_độ_lịch_sự": x,
        "mức_độ_tự_tin": x,
        "mức_độ_khách_quan": x
    }},
    "ngữ_cảnh": {{
        "ý_định_người_viết": "...",
        "mối_quan_hệ_suy_đoán": "...",
        "bối_cảnh_có_thể": "..."
    }},
    "từ_khóa_cảm_xúc": {{
        "tích_cực": ["...", "..."],
        "tiêu_cực": ["...", "..."],  
        "trung_tính": ["...", "..."]
    }},
    "phân_tích_cụ_thể": "Mô tả chi tiết về cảm xúc và lý do đánh giá",
    "khuyến_nghị": "Gợi ý cách cải thiện tone nếu cần thiết"
}}

Hãy phân tích CHÍNH XÁC, KHÁCH QUAN và CHI TIẾT dựa trên nội dung thực tế của văn bản.
"""
    
    if llm_client:
        try:
            response = llm_client.invoke(prompt)
            try:
                response = json.loads(response) if isinstance(response, str) else response
                return {
                    "status": "success",
                    "code": 0,
                    "note": {"type": "json"},
                    "response": response
                }
            except:
                return {
                    "status": "success",
                    "code": 1,
                    "note": {"type": "text"},
                    "response": response, 
                }
        except Exception as e:
            return {
                "status": "failed",
                "note": f"Lỗi khi gọi LLM: {str(e)}", 
                "code": 11,
                "prompt": prompt
            }
    else:
        return {
            "status": "failed",
            "code": 12,
            "note": "Cần tích hợp LLM client để phân tích cảm xúc chính xác. Sử dụng prompt trên với LLM để có phân tích cảm xúc chi tiết và chính xác",
            "prompt": prompt,
        }

# Dịch văn bản
@mcp.tool()
def translate_text(text: str, target_language: str, source_language: str = 'auto') -> dict:
    """
    Dịch văn bản sang ngôn ngữ khác bằng LLM.
    
    Args:
        text: Văn bản cần dịch
        target_language: Ngôn ngữ đích ('en', 'vi', 'zh', 'ja', 'ko', 'fr', 'de', 'es')
        source_language: Ngôn ngữ nguồn (mặc định 'auto' - tự động nhận diện)
        llm_client: Client để gọi LLM
    
    Returns:
        dict: Kết quả dịch thuật chi tiết
    """
    
    language_names = {
        'en': 'English (Tiếng Anh)',
        'vi': 'Vietnamese (Tiếng Việt)', 
        'zh': 'Chinese (Tiếng Trung)',
        'ja': 'Japanese (Tiếng Nhật)',
        'ko': 'Korean (Tiếng Hàn)',
        'fr': 'French (Tiếng Pháp)',
        'de': 'German (Tiếng Đức)',
        'es': 'Spanish (Tiếng Tây Ban Nha)'
    }
    
    target_lang_name = language_names.get(target_language, target_language)
    
    prompt = f"""
Bạn là một dịch giả chuyên nghiệp đa ngôn ngữ. Hãy thực hiện nhiệm vụ dịch thuật sau:

VĂN BẢN NGUỒN:
\"\"\"
{text}
\"\"\"

YÊU CẦU DỊCH THUẬT:
- Ngôn ngữ đích: {target_lang_name}
- Ngôn ngữ nguồn: {"Tự động nhận diện" if source_language == "auto" else language_names.get(source_language, source_language)}

HƯỚNG DẪN DỊCH:

1. NHẬN DIỆN NGÔN NGỮ NGUỒN:
   - Xác định chính xác ngôn ngữ của văn bản
   - Phát hiện có trộn lẫn nhiều ngôn ngữ không

2. DỊCH CHÍNH XÁC:
   - Giữ nguyên ý nghĩa gốc 100%
   - Tự nhiên trong ngôn ngữ đích
   - Phù hợp với ngữ cảnh và văn hóa
   - Bảo tồn tone và style

3. XỬ LÝ ĐẶC BIỆT:
   - Thuật ngữ chuyên môn: dịch chính xác hoặc giữ nguyên kèm giải thích
   - Tên riêng: giữ nguyên hoặc chuyển âm phù hợp
   - Thành ngữ, tục ngữ: tìm câu tương đương hoặc giải thích ý nghĩa

4. KIỂM TRA CHẤT LƯỢNG:
   - Đọc lại bản dịch để đảm bảo tự nhiên
   - Kiểm tra không bỏ sót nội dung
   - Đảm bảo ngữ pháp đúng trong ngôn ngữ đích

Trả về kết quả theo định dạng JSON:

{{
    "văn_bản_gốc": "...",
    "ngôn_ngữ_nguồn_nhận_diện": "...",
    "ngôn_ngữ_đích": "{target_lang_name}",
    "bản_dịch_chính": "...",
    "các_lựa_chọn_dịch_khác": [
        "Phiên bản dịch 1 (nếu có cách dịch khác)",
        "Phiên bản dịch 2 (nếu có)"
    ],
    "ghi_chú_dịch_thuật": [
        "Giải thích về thuật ngữ đặc biệt nếu có",
        "Lưu ý về văn hóa, ngữ cảnh nếu cần"
    ],
    "độ_tin_cậy": 0.xx,
    "mức_độ_khó_dịch": "dễ/trung_bình/khó",
    "khuyến_nghị": "Lời khuyên về cách sử dụng bản dịch nếu cần"
}}

Hãy dịch CHÍNH XÁC, TỰ NHIÊN và GIỮ NGUYÊN Ý NGHĨA.
"""
    
    if llm_client:
        try:
            response = llm_client.invoke(prompt)
            try:
                response = json.loads(response) if isinstance(response, str) else response
                return {
                    "status": "success",
                    "code": 0,
                    "note": {"type": "json"},
                    "response": response
                }
            except:
                return {
                    "status": "success",
                    "code": 1,
                    "note": {"type": "text"},
                    "response": response, 
                }
        except Exception as e:
            return {
                "status": "failed",
                "note": f"Lỗi khi gọi LLM: {str(e)}", 
                "code": 11,
                "prompt": prompt
            }
    else:
        return {
            "status": "failed",
            "code": 12,
            "note": "Cần tích hợp LLM client để dịch thuật chính xác. Sử dụng prompt trên với LLM khác để có bản dịch chất lượng cao.",
            "prompt": prompt,
            "more_info": {
                "văn bản nguồn": f"{text[:100]}{"..." if len(text) > 100 else ""}",
                "ngôn ngữ đích": f"{target_lang_name}",
                "độ dài": f"{len(text)} ký tự"
            },
        }
    
# Tạo ý chính
@mcp.tool()
def generate_talking_points(topic: str, context: str) -> dict:
    """
    Tạo các ý chính cho cuộc thảo luận/bài phát biểu bằng LLM.
    
    Args:
        topic: Chủ đề chính
        context: Bối cảnh (meeting, presentation, interview, etc.)
        llm_client: Client để gọi LLM
    
    Returns:
        dict: Danh sách các ý chính được tạo bởi LLM
    """
    
    # Giữ lại templates cơ bản làm reference
    context_references = {
        'meeting': "Cuộc họp - cần có cấu trúc rõ ràng, mục tiêu cụ thể, và action items",
        'presentation': "Thuyết trình - cần hook thu hút, nội dung logic, và call-to-action",
        'interview': "Phỏng vấn - cần thể hiện kinh nghiệm, thành tựu, và tầm nhìn",
        'training': "Đào tạo - cần mục tiêu học tập, thực hành, và đánh giá",
        'pitch': "Pitch - cần problem, solution, market, và ask",
        'negotiation': "Đàm phán - cần preparation, BATNA, và win-win approach"
    }
    
    context_info = context_references.get(context.lower(), f"Bối cảnh {context} - cần phù hợp với tình huống cụ thể")
    
    prompt = f"""
Bạn là một chuyên gia communication và public speaking. Hãy tạo ra các talking points chi tiết và hiệu quả cho:

CHỦ ĐỀ: {topic}
BỐI CẢNH: {context} ({context_info})

YÊU CẦU TẠO TALKING POINTS:

1. PHÂN TÍCH CHỦ ĐỀ VÀ BỐI CẢNH:
   - Hiểu rõ bản chất của chủ đề
   - Xác định mục tiêu communication
   - Phân tích audience có thể
   - Đánh giá thời lượng phù hợp

2. CẤU TRÚC TALKING POINTS:
   - Mở đầu: Hook thu hút, giới thiệu chủ đề
   - Thân bài: 3-7 điểm chính, được phát triển logic
   - Kết luận: Tóm tắt và call-to-action

3. NỘI DUNG CỤ THỂ CHO TỪNG ĐIỂM:
   - Key message rõ ràng
   - Supporting evidence/examples
   - Transition tự nhiên giữa các ý
   - Timing gợi ý cho mỗi phần

4. CUSTOMIZATION THEO BỐI CẢNH:
   - Meeting: Focus vào problem-solving, decision-making
   - Presentation: Emphasize storytelling, visual aids
   - Interview: Highlight experience, achievements, vision
   - Training: Include interactive elements, assessments

5. TIPS VÀ LƯU Ý:
   - Từ ngữ nên sử dụng/tránh
   - Body language suggestions
   - Potential questions và cách trả lời
   - Backup points nếu cần

Trả về kết quả theo định dạng JSON ĐẦY ĐỦ:

{{
    "chủ_đề": "{topic}",
    "bối_cảnh": "{context}",
    "phân_tích_tổng_quan": {{
        "mục_tiêu_chính": "...",
        "audience_target": "...",
        "thời_lượng_đề_xuất": "X-Y phút",
        "tone_phù_hợp": "..."
    }},
    "cấu_trúc_tổng_thể": {{
        "mở_đầu": {{
            "hook": "...",
            "thesis_statement": "...",
            "preview": "...",
            "thời_gian": "X phút"
        }},
        "thân_bài": [
            {{
                "điểm_chính": "...",
                "supporting_points": ["...", "..."],
                "examples": ["...", "..."],
                "transition": "...",
                "thời_gian": "X phút"
            }}
        ],
        "kết_luận": {{
            "tóm_tắt": "...",
            "call_to_action": "...",
            "closing_statement": "...",
            "thời_gian": "X phút"
        }}
    }},
    "talking_points_chi_tiết": [
        "1. [Điểm chính 1] - Nội dung cụ thể",
        "2. [Điểm chính 2] - Nội dung cụ thể",
        "..."
    ],
    "supporting_materials": {{
        "key_statistics": ["...", "..."],
        "relevant_examples": ["...", "..."],
        "potential_quotes": ["...", "..."]
    }},
    "practical_tips": {{
        "delivery_tips": ["...", "..."],
        "body_language": ["...", "..."],
        "voice_tone": "..."
    }},
    "q_and_a_preparation": [
        {{
            "potential_question": "...",
            "suggested_answer": "..."
        }}
    ],
    "backup_content": [
        "Ý phụ 1 - nếu có thời gian thừa",
        "Ý phụ 2 - nếu cần điều chỉnh"
    ],
    "success_metrics": "Cách đánh giá hiệu quả của buổi communication"
}}

Hãy tạo ra talking points CHẤT LƯỢNG CAO, THỰC TẾ và HIỆU QUẢ phù hợp với chủ đề và bối cảnh cụ thể.
"""
    
    if llm_client:
        try:
            response = llm_client.invoke(prompt)
            try:
                response = json.loads(response) if isinstance(response, str) else response
                return {
                    "status": "success",
                    "code": 0,
                    "note": {"type": "json"},
                    "response": response
                }
            except:
                return {
                    "status": "success",
                    "code": 1,
                    "note": {"type": "text"},
                    "response": response, 
                }
        except Exception as e:
            return {
                "status": "failed",
                "note": f"Lỗi khi gọi LLM: {str(e)}", 
                "code": 11,
                "prompt": prompt
            }
    else:
        return {
            "status": "failed",
            "code": 12,
            "note": "Cần tích hợp LLM client để có dàn ý tốt hơn. Sử dụng prompt trên với LLM khác để có bản dịch chất lượng cao.",
            "promt": prompt,
            "more_info": {
                "chủ đề": f"{topic}",
                "bối cảnh": f"{context} ({context_info})",
            },
        }

        
# =============================================================================
# FUNCTION CALLING SCHEMA FOR LLM INTEGRATION
# =============================================================================

def get_function_schemas() -> List[Dict[str, Any]]:
    """
    Trả về schema cho function calling với LLM.
    
    Returns:
        List[Dict]: Danh sách schema cho các function
    """
    
    return [
        {
            "name": "draft_communication",
            "description": "Soạn thảo nội dung giao tiếp như email, bài phát biểu, báo cáo, thông cáo với văn phong phù hợp",
            "parameters": {
                "type": "object",
                "properties": {
                    "comm_type": {
                        "type": "string",
                        "enum": ["email", "speech", "press_release", "report"],
                        "description": "Loại văn bản cần soạn thảo"
                    },
                    "audience": {
                        "type": "string",
                        "description": "Đối tượng nhận (internal, customers, media, stakeholders, etc.)"
                    },
                    "tone": {
                        "type": "string",
                        "enum": ["formal", "casual", "professional", "friendly"],
                        "description": "Giọng điệu của văn bản"
                    },
                    "key_points": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Danh sách các điểm chính cần truyền tải"
                    }
                },
                "required": ["comm_type", "audience", "tone", "key_points"]
            }
        },
        {
            "name": "proofread_and_edit",
            "description": "Kiểm tra lỗi chính tả, ngữ pháp và đề xuất cải thiện văn phong",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Văn bản cần kiểm tra và chỉnh sửa"
                    }
                },
                "required": ["text"]
            }
        },
        {
            "name": "analyze_sentiment",
            "description": "Phân tích sắc thái cảm xúc (tích cực, tiêu cực, trung tính) và các cảm xúc chính",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Văn bản cần phân tích cảm xúc"
                    }
                },
                "required": ["text"]
            }
        },
        {
            "name": "translate_text",
            "description": "Dịch văn bản sang ngôn ngữ khác",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Văn bản cần dịch"
                    },
                    "target_language": {
                        "type": "string",
                        "enum": ["en", "vi", "zh", "ja", "ko", "fr", "de", "es"],
                        "description": "Ngôn ngữ đích"
                    },
                    "source_language": {
                        "type": "string",
                        "default": "auto",
                        "description": "Ngôn ngữ nguồn (mặc định auto - tự động nhận diện)"
                    }
                },
                "required": ["text", "target_language"]
            }
        },
        {
            "name": "generate_talking_points",
            "description": "Tạo các ý chính cho một cuộc thảo luận hoặc bài phát biểu",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Chủ đề chính của cuộc thảo luận"
                    },
                    "context": {
                        "type": "string",
                        "description": "Bối cảnh (meeting, presentation, interview, training, etc.)"
                    }
                },
                "required": ["topic", "context"]
            }
        }
    ]

# =============================================================================
# EXAMPLE USAGE AND TESTING
# =============================================================================

def test_functions():
    """Test các function để đảm bảo hoạt động đúng."""
    
    print("=== TESTING COMMUNICATION SERVICE ===\n")
    
    # Test draft_communication
    print("1. Testing draft_communication:")
    draft = draft_communication(
        comm_type="email",
        audience="khách hàng",
        tone="professional",
        key_points=[
            "Thông báo về sản phẩm mới",
            "Ưu đãi đặc biệt cho khách hàng thân thiết",
            "Hướng dẫn sử dụng chi tiết"
        ]
    )
    print(draft)
    print("\n" + "="*50 + "\n")
    
    # Test analyze_sentiment
    print("2. Testing analyze_sentiment:")
    sentiment = analyze_sentiment("Tôi rất hài lòng với dịch vụ này. Nhân viên thân thiện và chuyên nghiệp.")
    print(json.dumps(sentiment, ensure_ascii=False, indent=2))
    print("\n" + "="*50 + "\n")
    
    # Test generate_talking_points
    print("3. Testing generate_talking_points:")
    points = generate_talking_points("Chiến lược marketing 2024", "presentation")
    print(json.dumps(points, ensure_ascii=False, indent=2))
    print("\n" + "="*50 + "\n")



if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='streamable-http')