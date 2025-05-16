from collections.abc import AsyncIterable
from typing import Any, Literal

import httpx

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.tools.retriever import create_retriever_tool

# Set logging for the queries
import logging
logging.basicConfig()
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)
logging.getLogger("langchain.retrievers.re_phraser").setLevel(logging.INFO)

from agents.MedicalInfoAgent.query_retrievers import RetrieverSystem

memory = MemorySaver()

class ResponseFormat(BaseModel):
    """Respond to the user in this format."""

    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    message: str

import yaml
with open("./configs/vectorstore.yaml") as f:
    configs=yaml.safe_load(f)

with open("./configs/medical-info-agent.yaml") as f:
    agent_configs = yaml.safe_load(f)

# Tạo LLM
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash')

embedding_function = HuggingFaceEmbeddings(
        model_name=configs['model_name'],
        model_kwargs=configs['model_kwargs'],
        encode_kwargs=configs['encode_kwargs']
    )
# Tạo vectorstore
vectordb = Chroma(persist_directory=configs['vectorstore_path'], embedding_function=embedding_function)
base_retriever = vectordb.as_retriever()

retriever_system = RetrieverSystem(llm, embedding_function)
# Tạo retriever
retriever = retriever_system.create_retriever(
    base_retriever,
    agent_configs['retriever_system']
)

retriever_tool = create_retriever_tool(
    retriever=retriever,
    name=agent_configs['retriever_tool']['name'], # do not use vietnamese name
    description=agent_configs['retriever_tool']['description'],
)

class MedicalInfoAgent:
    if type(agent_configs['SYSTEM_INSTRUCTIONS']) == list:
        SYSTEM_INSTRUCTION = ' '.join(agent_configs['SYSTEM_INSTRUCTIONS'])
    else:    
        SYSTEM_INSTRUCTION = str(agent_configs['SYSTEM_INSTRUCTIONS'])

    def __init__(self):
        self.model = llm
        self.tools = [retriever_tool]

        self.graph = create_react_agent(
            self.model,
            tools=self.tools,
            checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION,
            response_format=ResponseFormat,
        )

    def invoke(self, query, sessionId) -> str:
        config = {'configurable': {'thread_id': sessionId}}
        self.graph.invoke({'messages': [('user', query)]}, config)
        return self.get_agent_response(config)

    async def stream(self, query, sessionId) -> AsyncIterable[dict[str, Any]]:
        inputs = {'messages': [('user', query)]}
        config = {'configurable': {'thread_id': sessionId}}

        for item in self.graph.stream(inputs, config, stream_mode='values'):
            message = item['messages'][-1]
            if (
                isinstance(message, AIMessage)
                and message.tool_calls
                and len(message.tool_calls) > 0
            ):
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': 'Looking up the exchange rates...',
                }
            elif isinstance(message, ToolMessage):
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': 'Processing the exchange rates..',
                }

        yield self.get_agent_response(config)

    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)
        structured_response = current_state.values.get('structured_response')
        if structured_response and isinstance(
            structured_response, ResponseFormat
        ):
            if (
                structured_response.status == 'input_required'
                or structured_response.status == 'error'
            ):
                return {
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.message,
                }
            if structured_response.status == 'completed':
                return {
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': structured_response.message,
                }

        return {
            'is_task_complete': False,
            'require_user_input': True,
            'content': 'We are unable to process your request at the moment. Please try again.',
        }

    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']
