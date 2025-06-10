from remote_agents.utils.query_retrievers import RetrieverSystem

from collections.abc import AsyncIterable
from typing import Any, Literal

from pydantic import BaseModel

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain_core.messages import AIMessage, ToolMessage

from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
memory = MemorySaver()

# BASE AGENT
class BaseAgent:
    def __init__(self, 
                 name, 
                 model, 
                 tools: list = None, 
                 instructions: str = None, 
                 content_type: list = None):
        
        self.name = name
        self.model = model
        self.tools = tools

        if instructions:
            self.SYSTEM_INSTRUCTION = instructions
        if content_type:
            self.SUPPORTED_CONTENT_TYPES = content_type

    def invoke(self, query, sessionId) -> str:
        raise NotImplementedError ("This object is not fully implemented")

    async def stream(self, query, sessionId) -> AsyncIterable[dict[str, Any]]:
        raise NotImplementedError ("This object is not fully implemented")

    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']
    SYSTEM_INSTRUCTION = "Bạn là một trợ lý hữu ích."


# LANGGRAPH AGENT
class LangGraphAgent(BaseAgent):
    def __init__(self, 
                 name,
                 model, 
                 tools: list=[], 
                 instructions: str="Bạn là một trợ lý hữu ích.", 
                 content_type: list=['text', 'text/plain']):
        
        super().__init__(name, model, tools, instructions, content_type)

        self.graph = create_react_agent(
            model=self.model,
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
                    'content': 'Looking up data...',
                }
            elif isinstance(message, ToolMessage):
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': 'Processing data..',
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

# RESPONSE FORMAT
class ResponseFormat(BaseModel):
    """Respond to the user in this format."""

    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    message: str

# RAG
class AgentWithRAGTool:
    def __init__(self, llm, configs):
        self.__llm = llm
        self.__configs = configs
        self.__initialize()
    def __initialize(self):
        # Tạo embedding
        embedding_function = HuggingFaceEmbeddings(
                model_name=self.__configs['embedding']['model_name'],
                model_kwargs=self.__configs['embedding']['model_kwargs'],
                encode_kwargs=self.__configs['embedding']['encode_kwargs']
            )
        
        # Tạo vectorstore
        vectordb = Chroma(persist_directory=self.__configs['agent_vectorstore'], embedding_function=embedding_function)
        
        # Tạo retriever
        base_retriever = vectordb.as_retriever()
        retriever_system = RetrieverSystem(self.__llm, embedding_function)
        
        retriever = retriever_system.create_retriever(
            base_retriever,
            self.__configs['retriever_system']
        )

        self.__retriever_tool = create_retriever_tool(
            retriever=retriever,
            name=self.__configs['retriever_tool']['name'], # do not use vietnamese name
            description=self.__configs['retriever_tool']['description'],
        )
    
    def get_llm(self):
        return self.__llm
    
    def get_retriever_tool(self):
        return self.__retriever_tool