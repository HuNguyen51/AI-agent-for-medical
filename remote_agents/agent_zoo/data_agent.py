from remote_agents.base_agent import LangGraphAgent

import yaml
with open("./configs/data.yaml") as f:
    configs: dict = yaml.safe_load(f)

name = configs['agent_name']

instructions = " ".join(configs['SYSTEM_INSTRUCTIONS']) if type(configs['SYSTEM_INSTRUCTIONS']) == list else configs['SYSTEM_INSTRUCTIONS']
content_type = configs['SUPPORTED_CONTENT_TYPES']

host = configs['host']
port = configs['port']

class DataAgent(LangGraphAgent):
    def __init__(self, 
                 model, 
                 tools: list=None):
        
        super().__init__(name, model, tools, instructions, content_type)

        self.host = host
        self.port = port