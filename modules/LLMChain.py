from langchain.chains import RetrievalQA

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

class LLMChain:
    def __init__(self, llm):
        self.llm = llm

    def infer(self, question, prompt, retriever):
        llm_chain = RetrievalQA.from_chain_type(
            llm = self.llm,
            retriever = retriever,
            chain_type_kwargs= {'prompt': prompt},
            chain_type= "stuff",
            return_source_documents = False
        )

        response = llm_chain.invoke({"query": question})
        return response['result']