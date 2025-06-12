from langchain_mcp_adapters.client import MultiServerMCPClient

from remote_agents.base_agent import LangGraphAgent

# load API key
import yaml
from dotenv import load_dotenv
load_dotenv()

# retriever logging
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger(__name__)
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)
logging.getLogger("langchain.retrievers.re_phraser").setLevel(logging.INFO)

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI


# Read config
def read_config():
    with open("./configs/comms.yaml") as f:
        agent_configs: dict = yaml.safe_load(f)
    return agent_configs

class CommsAgent(LangGraphAgent):
    def __init__(self, model_configs):
        agent_configs = read_config()
        # Model - Brain
        if model_configs['PLATFORM'] == "GOOGLE":
            brain = ChatGoogleGenerativeAI(model=model_configs['MODEL'])

        elif model_configs['PLATFORM'] == "OPENAI":
            brain = ChatOpenAI(model=model_configs['MODEL'], base_url=model_configs['BASE_URL'])

        else:
            raise "Platform not supported"
        
        # Agent - Instructions
        card = agent_configs['card']
        skills = agent_configs['skills']
        host = agent_configs['host']
        port = agent_configs['port']
        streaming = agent_configs.get('streaming', False)
        instructions = " ".join(agent_configs['SYSTEM_INSTRUCTIONS']) if type(agent_configs['SYSTEM_INSTRUCTIONS']) == list else agent_configs['SYSTEM_INSTRUCTIONS']
        content_type = agent_configs['SUPPORTED_CONTENT_TYPES']

        # Tools - Actions
        import asyncio
        client = MultiServerMCPClient(agent_configs['mcp_server'])
        tools = asyncio.get_event_loop().run_until_complete(client.get_tools())

        # Initialize
        super().__init__(card, skills, host, port, streaming,
                         brain, tools, 
                         instructions, content_type)


async def get_result(result):
    async for r in result:
        print(r)
if __name__ == "__main__":
    import asyncio
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
    
    agent = CommsAgent({'PLATFORM': 'GOOGLE', 'MODEL': 'gemini-2.0-flash', 'BASE_URL': None})
    result = agent.stream(query, '1')
    asyncio.get_event_loop().run_until_complete(get_result(result))