import logging
import os

from agents.utils.base_agent import BaseAgent
from agents.utils.task_manager import AgentTaskManager

from common.server import A2AServer
from common.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    MissingAPIKeyError,
)
from common.utils.push_notification_auth import PushNotificationSenderAuth
from dotenv import load_dotenv


load_dotenv()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Runner:
    def __init__(self, agent: BaseAgent, configs):
        self.agent = agent
        self.configs = configs

    def run(self, host='localhost', port=10000):
        """Start the server."""
        try:
            if not os.getenv('GOOGLE_API_KEY'):
                raise MissingAPIKeyError(
                    'GOOGLE_API_KEY environment variable not set.'
                )

            capabilities = AgentCapabilities(streaming=True, pushNotifications=True)
            skills = []
            for skill in self.configs['skills']:
                skills.append(
                    AgentSkill(
                        id=skill['id'],
                        name=skill['name'],
                        description=skill['description'],
                        tags=skill['tags'],
                        examples=skill['examples'],
                    )
                )

            agent_card = AgentCard(
                name=self.configs['card']['name'],
                description=self.configs['card']['description'],
                url=f'http://{host}:{port}/',
                version=self.configs['card']['version'],
                defaultInputModes=self.agent.SUPPORTED_CONTENT_TYPES,
                defaultOutputModes=self.agent.SUPPORTED_CONTENT_TYPES,
                capabilities=capabilities,
                skills=skills,
            )

            notification_sender_auth = PushNotificationSenderAuth()
            notification_sender_auth.generate_jwk()
            server = A2AServer(
                agent_card=agent_card,
                task_manager=AgentTaskManager(
                    agent=self.agent,
                    notification_sender_auth=notification_sender_auth,
                ),
                host=host,
                port=port,
            )

            server.app.add_route(
                '/.well-known/jwks.json',
                notification_sender_auth.handle_jwks_endpoint,
                methods=['GET'],
            )

            logger.info(f'Starting server on {host}:{port}')
            server.start()
        except MissingAPIKeyError as e:
            logger.error(f'Error: {e}')
            exit(1)
        except Exception as e:
            logger.error(f'An error occurred during server startup: {e}')
            exit(1)


if __name__ == '__main__':
    import yaml
    with open("./configs/medical-info-agent.yaml") as f:
        configs=yaml.safe_load(f)
    print(configs)