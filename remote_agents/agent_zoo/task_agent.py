import os
os.environ["OPENAI_AGENTS_DISABLE_TRACING"] = "1"

from openai import AsyncOpenAI  # Thay đổi: từ AsyncOpenAI sang OpenAI
from agents import set_default_openai_client
from agents import set_default_openai_api

from dotenv import load_dotenv
load_dotenv()

api_key=os.getenv('GOOGLE_API_KEY')
base_url="https://generativelanguage.googleapis.com/v1beta/openai/"

custom_client = AsyncOpenAI(base_url=base_url, api_key=api_key)  # Thay đổi: bỏ Async
set_default_openai_client(custom_client)
set_default_openai_api("chat_completions")

from typing import Any

from agents import Agent, Runner
from agents.mcp import MCPServer, MCPServerSse
from agents.model_settings import ModelSettings

from remote_agents.base_agent import BaseAgent, ResponseFormat
import asyncio
# import nest_asyncio
# nest_asyncio.apply()

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
            # tools=self.tools if self.tools else [],
            # mcp_servers=self.servers,
            model_settings=ModelSettings(tool_choice="auto"),
        )

    def invoke(self, query, sessionId):
        return asyncio.run(self.invoke_sync(query, sessionId))
    
    async def invoke_sync(self, query, sessionId):
        input = [{"role": "user", "content": query}]

        await self.__connect()
        result = await Runner.run(starting_agent=self.agent, input=input, max_turns=5)
        await self.__cleanup()


        return result.final_output
    
    async def __connect(self):
        servers = []
        for mcp_header in self.mcp_servers:
            server = MCPServerSse(
                name=mcp_header["name"],
                params=mcp_header["params"],
            )
            await server.connect()
            servers.append(server)
    
        self.agent.mcp_servers = servers

    async def __cleanup(self):
        for server in self.agent.mcp_servers:
            await server.cleanup()

    def set_mcp_server(self, mcp_servers):
        self.mcp_servers = mcp_servers


def main():  # Thay đổi: bỏ async
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

    mcp_servers = [
        {
            "name": "SSE Python Server",
            "params": {
                "url": "http://localhost:8000/sse",
            },
        }
    ]

    comms_agent = CommsAgent('comms_agent', model, mcp_servers=mcp_servers)
    result = comms_agent.invoke(query, '1')  # Thay đổi: bỏ await
    print(result)

if __name__ == "__main__":
    main()  # Thay đổi: bỏ asyncio.run()