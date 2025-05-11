from typing import List, Dict, Any, Union, Type, Optional, Callable

from langchain.retrievers import (
    RePhraseQueryRetriever,
    MultiQueryRetriever,
    ContextualCompressionRetriever,
    EnsembleRetriever
)
from langchain.retrievers.document_compressors import (
    LLMChainFilter,
    LLMListwiseRerank,
    EmbeddingsFilter,
    DocumentCompressorPipeline,
    FlashrankRerank
)
from langchain_community.document_transformers import EmbeddingsRedundantFilter
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.retrievers import BaseRetriever
from langchain_core.language_models import BaseLanguageModel
from langchain_core.embeddings import Embeddings

from langchain.prompts import PromptTemplate as Prompt
from langchain_core.prompts import ChatPromptTemplate



class OutputParser:
    """Container class for output parsers"""
    
    class LineListOutputParser(BaseOutputParser[List[str]]):
        """Parse text into list of non-empty lines"""
        def parse(self, text: str) -> List[str]:
            lines = text.strip().split("\n")
            return [line for line in lines if line]  # More pythonic filter
    
    class StringOutputParser(BaseOutputParser[str]):
        """Parse and clean text"""
        def parse(self, text: str) -> str:
            return text.strip()


class RetrieverFactory:
    """Factory class for creating various retriever instances"""
    
    def __init__(self, llm: BaseLanguageModel, embeddings: Optional[Embeddings] = None):
        """
        Initialize RetrieverFactory
        
        Args:
            llm: Language model to use in retrievers
            embeddings: Embeddings to use in retrievers that require them
        """
        self.llm = llm
        self.embeddings = embeddings
        self._prompt_templates = {
            "rephrase": """Bạn là trợ lý hữu ích trong lĩnh vực y tế, được giao nhiệm vụ lấy truy vấn ngôn ngữ tự nhiên từ người dùng và chuyển đổi thành truy vấn cho vectorstore. 
Trong quá trình này, hãy loại bỏ tất cả thông tin không liên quan đến nhiệm vụ truy xuất và trả về một câu hỏi mới, đơn giản để truy xuất vectorstore. 
Hãy trả lời bằng giọng văn trang nhã lịch sự, nhớ là phải trả lời ngắn gọn xúc tích nội dung chính, không dài dòng.
Đây là câu hỏi: {question}.""",
            "multiple_query": """Bạn là một trợ lý hữu ích trong lĩnh vực y tế.
Nhiệm vụ của bạn là tạo ra năm phiên bản khác nhau của câu hỏi người dùng đã cho để lấy các tài liệu có liên quan từ cơ sở dữ liệu vector. 
Bằng cách tạo ra nhiều góc nhìn về câu hỏi của người dùng, mục tiêu của bạn là giúp người dùng vượt qua một số hạn chế của tìm kiếm tương đồng dựa trên khoảng cách. 
Cung cấp các câu hỏi thay thế này được phân tách bằng dòng mới.
Đây là câu hỏi: {question}."""
        }
    
    def create_rephrase_retriever(self, base_retriever: BaseRetriever) -> RePhraseQueryRetriever:
        """
        Create a RePhraseQueryRetriever
        
        Args:
            base_retriever: Base retriever to use
            
        Returns:
            Configured RePhraseQueryRetriever
        """
        prompt = Prompt(template=self._prompt_templates["rephrase"], input_variables=["question"])
        llm_chain = prompt | self.llm | OutputParser.StringOutputParser()
        
        return RePhraseQueryRetriever(retriever=base_retriever, llm_chain=llm_chain)
    
    def create_multiple_query_retriever(self, base_retriever: BaseRetriever) -> MultiQueryRetriever:
        """
        Create a MultiQueryRetriever
        
        Args:
            base_retriever: Base retriever to use
            
        Returns:
            Configured MultiQueryRetriever
        """
        prompt = Prompt(template=self._prompt_templates["multiple_query"], input_variables=["question"])
        llm_chain = prompt | self.llm | OutputParser.LineListOutputParser()
        
        return MultiQueryRetriever(retriever=base_retriever, llm_chain=llm_chain)
    
    def __create_document_compressor(self, compressor_config: Dict[str, Any]) -> Any:
        """
        Create a document compressor based on configuration
        
        Args:
            compressor_config: Configuration for the compressor
            
        Returns:
            Document compressor instance
        """
        compressor_type = compressor_config.get("type", "llm_chain_filter")
        
        if compressor_type == "llm_chain_filter": # Filter that drops documents that aren't relevant to the query.
            return LLMChainFilter.from_llm(self.llm)
        
        elif compressor_type == "llm_listwise_rerank": # uses a language model to rerank a list of documents based on their relevance to a query
            top_n = compressor_config.get("top_n", 3)
            return LLMListwiseRerank.from_llm(self.llm, top_n)
        
        elif compressor_type == "embeddings_filter": # Document compressor that uses embeddings to drop documents unrelated to the query.
            if not self.embeddings:
                raise ValueError("Embeddings required for embeddings_filter")
            similarity_threshold = compressor_config.get("similarity_threshold", 0.7)
            return EmbeddingsFilter(
                embeddings=self.embeddings, 
                similarity_threshold=similarity_threshold
            )
        
        elif compressor_type == "document_compressor_pipeline": # Filter that drops redundant documents by comparing their embeddings -> Document compressor that uses embeddings to drop documents unrelated to the query
            if not self.embeddings:
                raise ValueError("Embeddings required for document_compressor_pipeline")
                
            chunk_size = compressor_config.get("chunk_size", 1000)
            chunk_overlap = compressor_config.get("chunk_overlap", 200)
            separator = compressor_config.get("separator", "\n\n")
            similarity_threshold = compressor_config.get("similarity_threshold", 0.7)
            
            splitter = CharacterTextSplitter(
                chunk_size=chunk_size, 
                chunk_overlap=chunk_overlap, 
                separator=separator
            )
            redundant_filter = EmbeddingsRedundantFilter(embeddings=self.embeddings)
            relevant_filter = EmbeddingsFilter(
                embeddings=self.embeddings, 
                similarity_threshold=similarity_threshold
            )
            
            return DocumentCompressorPipeline(
                transformers=[splitter, redundant_filter, relevant_filter]
            )
        
        elif compressor_type == "rerank":
            # %pip install --upgrade --quiet  flashrank
            return FlashrankRerank()
        
        else:
            raise ValueError(f"Unknown compressor type: {compressor_type}")
    
    def create_contextual_compression_retriever(
        self, 
        base_retriever: BaseRetriever, 
        compressor_config: Dict[str, Any]
    ) -> ContextualCompressionRetriever:
        """
        Create a ContextualCompressionRetriever
        
        Args:
            base_retriever: Base retriever to use
            compressor_config: Configuration for the compressor
            
        Returns:
            Configured ContextualCompressionRetriever
        """
        compressor = self.__create_document_compressor(compressor_config)
        
        return ContextualCompressionRetriever(
            base_compressor=compressor, 
            base_retriever=base_retriever
        )
    
    def create_ensemble_retriever(
        self, 
        retrievers: List[BaseRetriever], 
        weights: Optional[List[float]] = None
    ) -> EnsembleRetriever:
        """
        Create an EnsembleRetriever
        
        Args:
            retrievers: List of retrievers to ensemble
            weights: Weights for each retriever (must match length of retrievers)
            
        Returns:
            Configured EnsembleRetriever
        """
        if weights and len(retrievers) != len(weights):
            raise ValueError("Number of retrievers must match number of weights")
            
        if not weights:
            # Equal weights if not specified
            weights = [1.0 / len(retrievers)] * len(retrievers)
            
        return EnsembleRetriever(retrievers=retrievers, weights=weights)


class RetrieverChain:
    """Class for creating chains of retrievers"""
    
    def __init__(self, factory: RetrieverFactory):
        """
        Initialize RetrieverChain
        
        Args:
            factory: RetrieverFactory instance to use for creating retrievers
        """
        self.factory = factory
    
    def create_chain(
        self, 
        base_retriever: BaseRetriever, 
        chain_config: List[Dict[str, Any]]
    ) -> BaseRetriever:
        """
        Create a chain of retrievers
        
        Args:
            base_retriever: Base retriever to start the chain
            chain_config: List of configurations for each retriever in the chain
                Each config should have a "type" key and any additional parameters
                
        Returns:
            The final retriever in the chain
        """
        current_retriever = base_retriever
        
        for config in chain_config:
            retriever_type = config.get("type")
            
            if retriever_type == "rephrase":
                current_retriever = self.factory.create_rephrase_retriever(current_retriever)
            
            elif retriever_type == "multiple_query":
                current_retriever = self.factory.create_multiple_query_retriever(current_retriever)
            
            elif retriever_type == "contextual_compression":
                compressor_config = config.get("compressor", {"type": "llm_chain_filter"})
                current_retriever = self.factory.create_contextual_compression_retriever(
                    current_retriever, 
                    compressor_config
                )
            
            else:
                raise ValueError(f"Unknown retriever type in chain: {retriever_type}")
        
        return current_retriever


class RetrieverSystem:
    """Main class for working with retrievers"""
    
    def __init__(
        self, 
        llm: BaseLanguageModel,
        embeddings: Optional[Embeddings] = None
    ):
        """
        Initialize RetrieverSystem
        
        Args:
            llm: Language model to use
            embeddings: Embeddings to use (required for some retrievers)
        """
        self.factory = RetrieverFactory(llm, embeddings)
        self.chain_builder = RetrieverChain(self.factory)
    
    def create_retriever(
        self, 
        base_retriever: BaseRetriever, 
        retriever_config: Dict[str, Any]
    ) -> BaseRetriever:
        """
        Create a retriever based on configuration
        
        Args:
            base_retriever: Base retriever to use
            retriever_config: Configuration for the retriever
                Must include a "type" key
                
        Returns:
            Configured retriever
        """
        retriever_type = retriever_config.get("type")
        
        if retriever_type == "rephrase":
            return self.factory.create_rephrase_retriever(base_retriever)
        
        elif retriever_type == "multiple_query":
            return self.factory.create_multiple_query_retriever(base_retriever)
        
        elif retriever_type == "contextual_compression":
            compressor_config = retriever_config.get("compressor", {"type": "llm_chain_filter"})
            return self.factory.create_contextual_compression_retriever(
                base_retriever, 
                compressor_config
            )
        
        elif retriever_type == "chain":
            chain_config = retriever_config.get("chain", [])
            return self.chain_builder.create_chain(base_retriever, chain_config)
        
        elif retriever_type == "ensemble":
            retrievers_config = retriever_config.get("retrievers", [])
            weights = retriever_config.get("weights")
            
            retrievers = []
            for r_config in retrievers_config:
                # Recursively create each retriever in the ensemble
                retriever = self.create_retriever(base_retriever, r_config)
                retrievers.append(retriever)
                
            return self.factory.create_ensemble_retriever(retrievers, weights)
        
        else:
            raise ValueError(f"Unknown retriever type: {retriever_type}")


# Example usage:
"""
# Initialize the system
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

llm = ChatOpenAI(model="gpt-4")
embeddings = OpenAIEmbeddings()
base_retriever = your_vector_store.as_retriever()

retriever_system = RetrieverSystem(llm, embeddings)

# Create a simple rephrase retriever
rephrase_retriever = retriever_system.create_retriever(
    base_retriever, 
    {"type": "rephrase"}
)

# Create a more complex chain
chain_retriever = retriever_system.create_retriever(
    base_retriever,
    {
        "type": "chain",
        "chain": [
            {"type": "multiple_query"},
            {"type": "contextual_compression", 
             "compressor": {"type": "llm_listwise_rerank", "top_n": 5}}
        ]
    }
)

# Create an ensemble of retrievers
ensemble_retriever = retriever_system.create_retriever(
    base_retriever,
    {
        "type": "ensemble",
        "retrievers": [
            {"type": "rephrase"},
            {"type": "multiple_query"},
            {"type": "contextual_compression", 
             "compressor": {"type": "rerank"}}
        ],
        "weights": [0.3, 0.3, 0.4]
    }
)

# Use the retriever
docs = ensemble_retriever.get_relevant_documents("Câu hỏi về bệnh tiểu đường")
"""