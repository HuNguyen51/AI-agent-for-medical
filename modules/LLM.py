from langchain_community.llms import CTransformers
from langchain_openai import ChatOpenAI

class LLM:
    def __init__(self):
        self.__init__()

    @staticmethod
    def from_openai(model, base_url, api_key, temperature=None, max_tokens=None, timeout=None, max_retries=None):
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            max_retries=max_retries,
            api_key=api_key,
            base_url=base_url,
        )
    
    @staticmethod
    def from_local_transformers(model_path, model_type, max_tokens=None, temperature=None):
        return CTransformers(
            model=model_path,
            model_type=model_type,
            max_tokens=max_tokens,
            temperature=temperature
        )
