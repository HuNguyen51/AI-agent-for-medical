import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# retriever logging
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)
logging.getLogger("langchain.retrievers.re_phraser").setLevel(logging.INFO)


from agents.personal_info_agent.agent import PersonalInfoAgent
from agents.utils.master_agent import AgentWithRAGTool

from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_openai import ChatOpenAI

# Read config
import yaml
with open("./configs/vectorstore.yaml") as f:
    configs: dict = yaml.safe_load(f)

with open("./configs/medical-info-agent.yaml") as f:
    agent_configs: dict = yaml.safe_load(f)

configs.update(agent_configs)

# Initialize
llm = ChatGoogleGenerativeAI(model=agent_configs['agent_brain'])

retriever_tool = AgentWithRAGTool(llm, configs).get_retriever_tool()
tools = [retriever_tool]

instruction = " ".join(agent_configs['SYSTEM_INSTRUCTIONS']) if type(agent_configs['SYSTEM_INSTRUCTIONS']) == list else agent_configs['SYSTEM_INSTRUCTIONS']

content_type = agent_configs['SUPPORTED_CONTENT_TYPES']

# Init Agent
agent = PersonalInfoAgent(llm, tools, instruction, content_type)
host = agent_configs['host']
port = agent_configs['port']

if __name__ == '__main__':
    from agents.utils.server import Runner
    Runner(agent, agent_configs).run(host, port)
