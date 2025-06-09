from collections.abc import AsyncIterable
from typing import Any, Literal

from pydantic import BaseModel

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from remote_agents.utils.query_retrievers import RetrieverSystem
from langchain.tools.retriever import create_retriever_tool

# RESPONSE FORMAT
class ResponseFormat(BaseModel):
    """Respond to the user in this format."""

    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    message: str


# BASE AGENT
class BaseAgent:
    def __init__(self, 
                 name, 
                 model, 
                 tools: list = None, 
                 mcp_servers: list = None, 
                 instructions: str = None, 
                 content_type: list = None):
        
        self.name = name
        self.model = model
        self.tools = tools
        self.mcp_servers = mcp_servers

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