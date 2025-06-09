import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# retriever logging
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)
logging.getLogger("langchain.retrievers.re_phraser").setLevel(logging.INFO)

from common.types import MissingAPIKeyError

from remote_agents.agent_zoo.data_agent import DataAgent
from remote_agents.base_agent import AgentWithRAGTool

from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_openai import ChatOpenAI

# load API key
import os
from dotenv import load_dotenv
load_dotenv()
if not os.getenv('GOOGLE_API_KEY'):
    raise MissingAPIKeyError('GOOGLE_API_KEY environment variable not set.')

# Read config
import yaml
with open("./configs/vectorstore.yaml") as f:
    configs: dict = yaml.safe_load(f)

with open("./configs/data.yaml") as f:
    agent_configs: dict = yaml.safe_load(f)

configs.update(agent_configs)

# Initialize
model = ChatGoogleGenerativeAI(model=agent_configs['agent_brain'])

retriever_tool = AgentWithRAGTool(model, configs).get_retriever_tool()
tools = [retriever_tool]

instructions = " ".join(agent_configs['SYSTEM_INSTRUCTIONS']) if type(agent_configs['SYSTEM_INSTRUCTIONS']) == list else agent_configs['SYSTEM_INSTRUCTIONS']

content_type = agent_configs['SUPPORTED_CONTENT_TYPES']

# Init Agent
agent = DataAgent('DataAgent', model, 
                  tools=tools, 
                  instructions=instructions, 
                  content_type=content_type)
host = agent_configs['host']
port = agent_configs['port']

if __name__ == '__main__':
    # command: python -m agents.personal_info_agent.__main__
    from remote_agents.utils.server import Runner
    Runner(agent, agent_configs).run(host, port)