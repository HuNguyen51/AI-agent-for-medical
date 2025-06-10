import asyncio
import os
os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"

from openai import AsyncOpenAI
from agents import set_default_openai_client
from agents import set_default_openai_api

from dotenv import load_dotenv
load_dotenv()

api_key=os.getenv('GOOGLE_API_KEY')
base_url="https://generativelanguage.googleapis.com/v1beta/openai/"

custom_client = AsyncOpenAI(base_url=base_url, api_key=api_key)
set_default_openai_client(custom_client)
set_default_openai_api("chat_completions")


from typing import Any

from agents import Agent, Runner#, gen_trace_id, trace
from agents.mcp import MCPServer, MCPServerSse
from agents.model_settings import ModelSettings


from remote_agents.base_agent import BaseAgent, ResponseFormat

class CommsAgent(BaseAgent):
    def __init__(self, 
                 name,
                 model, 
                 tools: list=None, 
                 mcp_servers: list=None,
                 instructions: str="Hãy dùng các tool để trả lời câu hỏi.", 
                 content_type: list=['text', 'text/plain']):
        super().__init__(name, model, tools, mcp_servers, instructions, content_type)
        
        self.agent = Agent(
            name=self.name,
            model=self.model,
            instructions=self.SYSTEM_INSTRUCTION,
            tools=self.tools if self.tools else [],
            mcp_servers=self.mcp_servers,
            model_settings=ModelSettings(tool_choice="auto"),
        )

    # IMPORTANT
    # https://langchain-ai.github.io/langgraph/agents/mcp/
    # giống với đã sửa bên data_agent

    async def invoke(self, query, sessionId):
        input = [{"role": "user", "content": query}]
        result = await Runner.run(starting_agent=self.agent, input=input, max_turns=5)#, tracing_disbale = True
        return result.final_output # return ở đây

        # lấy thông tin từ result rồi tạo phản hồi mới dựa trên đó
        # new_input = result.to_input_list() + [{"role": "user", "content": message}]

#     async def stream(mcp_server: MCPServer):
#         """Ví dụ nâng cao với progress tracking"""
        
#         result_stream = Runner.run_streamed(
#             starting_agent=agent,
#             input=[{"role": "user", "content": query}],
#             max_turns=10
#         )
        
#         partial_response = ""
#         import time
#         import json

#         async for event in result_stream.stream_events():
#             # Xử lý raw response events
#             if hasattr(event, 'data') and hasattr(event.data, 'type') and event.data.type == 'response.output_text.delta':
#                 delta_text = event.data.delta
#                 partial_response += delta_text
#                 print(f"{delta_text}", end='', flush=True)
#                 time.sleep(0.5)
            
#             # Xử lý tool calls
#             elif hasattr(event, 'name') and event.name=='tool_called':
#                 if hasattr(event.item, 'raw_item'):
#                     print("Begin call tool:", event.item.raw_item.name, 'with input:', event.item.raw_item.arguments, '\n')

#             # Xử lý tool outputs
#             elif hasattr(event, 'name') and event.name=='tool_output':
#                 if hasattr(event.item, 'raw_item'):
#                     tool_output = json.loads(event.item.raw_item.get('output', {})) #  # out của function_calling tổ chức theo json dưới dạng text -> chuyển text thành json
#                     tool_output = json.loads(tool_output.get('text', {})) # out của tool dạng text -> chuyển thành json
#                     print("*" * 50, '\n')
#                     print("tool output:", tool_output.get('status', 'unknow status'))
#                     print('response:', tool_output.get('response', 'None'))
#                     print('prompt:', tool_output.get('prompt', 'None'))
#                     print('more_info:', tool_output.get('more_info', 'None'))
#                     print("*" * 50, '\n')

#             # SAU KHI CÓ OUTPUT THÌ TUỲ VÀO NÓ MÀ THỰC HIỆN BƯỚC TIẾP THEO

#             # Agent updates
#             elif hasattr(event, 'new_agent') and hasattr(event.new_agent, 'name'):
#                 print(f"Agent switched to: {event.new_agent.name}", '\n')


async def main():
    query = """
Hãy viết cho tôi một nội dung với các yêu cầu sau:

Loại hình giao tiếp: email
Đối tượng người nhận: khách hàng thân thiết
Giọng văn (Tone of voice): chuyên nghiệp và trang trọng
Mục tiêu chính: Thông báo về sản phẩm mới
Các ý chính cần đề cập (Key points):
Thông báo ra mắt dòng sản phẩm chăm sóc da "Pure Glow"
Nêu bật thành phần tự nhiên và công dụng làm sáng da sau 7 ngày
Tặng ưu đãi độc quyền giảm 30% và miễn phí vận chuyển cho khách hàng thân thiết
Hướng dẫn ngắn gọn cách sử dụng sản phẩm để đạt hiệu quả tốt nhất
Kêu gọi hành động (Call to Action): Khám phá ngay
Thông tin bổ sung: Ưu đãi chỉ áp dụng khi mua hàng qua website chính thức và có hiệu lực đến hết ngày 30/06/2025.
"""
    model= "gemini-2.0-flash"

    server = MCPServerSse(
        name="SSE Python Server",
        params={
            "url": "http://localhost:8000/sse",
        },
    )
    await server.connect()


    comms_agent = CommsAgent('comms_agent', model, mcp_servers=[server])
    result = await comms_agent.invoke(query, '1')
    print(result)


    await server.cleanup()

if __name__ == "__main__":
    asyncio.run(main())