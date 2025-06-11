import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from remote_agents.agent_zoo.data_agent import DataAgent

# Read config
import yaml
with open("./configs/base.yaml") as f:
    configs: dict = yaml.safe_load(f)

# Agent
agent = DataAgent(configs['data_agent'])

if __name__ == '__main__':
    from remote_agents.utils.server import Runner
    Runner(agent).run()