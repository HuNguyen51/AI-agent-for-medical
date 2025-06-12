from remote_agents.base_agent import LangGraphAgent
from remote_agents.base_agent import AgentWithRAGTool

# load API key
import os
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
    with open("./configs/vectorstore.yaml") as f:
        vector_configs: dict = yaml.safe_load(f)

    with open("./configs/data.yaml") as f:
        agent_configs: dict = yaml.safe_load(f)
    return vector_configs, agent_configs


class DataAgent(LangGraphAgent):
    def __init__(self, model_configs):
        vector_configs, agent_configs = read_config()
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
        retriever_tool = AgentWithRAGTool(brain, vector_configs, agent_configs).get_retriever_tool()
        tools = [retriever_tool]

        # Initialize
        super().__init__(card, skills, host, port, streaming,
                         brain, tools, 
                         instructions, content_type)

        