from langchain.retrievers import RePhraseQueryRetriever
from langchain.retrievers import MultiQueryRetriever
from langchain.retrievers import ContextualCompressionRetriever

from langchain.retrievers.document_compressors import LLMChainFilter
from langchain.retrievers.document_compressors import LLMListwiseRerank
from langchain.retrievers.document_compressors import EmbeddingsFilter
from langchain.retrievers.document_compressors import DocumentCompressorPipeline
from langchain_community.document_transformers import EmbeddingsRedundantFilter
from langchain_text_splitters import CharacterTextSplitter
from langchain.retrievers.document_compressors import FlashrankRerank

from langchain.retrievers import EnsembleRetriever

from langchain_core.output_parsers import BaseOutputParser
from typing import List

from modules.Prompt import Prompt

class LineListOutputParser(BaseOutputParser[List[str]]):
    def parse(self, text: str) -> List[str]:
        lines = text.strip().split("\n")
        return list(filter(None, lines))  # Remove empty lines
    
class StringOutputParser(BaseOutputParser[str]):
    def parse(self, text: str) -> str:
        return text.strip()

# retriever biến đổi prompt
def re_phrase_retriever(base_retriever, llm):   
    template = \
"""<|im_start|>system
Bạn là trợ lý hữu ích trong lĩnh vực y tế, được giao nhiệm vụ lấy truy vấn ngôn ngữ tự nhiên từ người dùng và chuyển đổi thành truy vấn cho vectorstore. 
Trong quá trình này, hãy loại bỏ tất cả thông tin không liên quan đến nhiệm vụ truy xuất và trả về một câu hỏi mới, đơn giản để truy xuất vectorstore. 
Hãy trả lời bằng giọng văn trang nhã lịch sự, nhớ là phải trả lời ngắn gọn xúc tích nội dung chính, không dài dòng.
Đây là câu hỏi: {question}.
<|im_end|>
<|im_start|>assistant
"""
    prompt = Prompt(template, ["question"])

    llm_chain = prompt | llm | StringOutputParser()

    return RePhraseQueryRetriever(retriever=base_retriever, llm_chain=llm_chain)

def multiple_query_retriever(base_retriever, llm):
    template =   \
"""<|im_start|>system
Bạn là một trợ lý hữu ích trong lĩnh vực y tế.
Nhiệm vụ của bạn là tạo ra năm phiên bản khác nhau của câu hỏi người dùng đã cho để lấy các tài liệu có liên quan từ cơ sở dữ liệu vector. 
Bằng cách tạo ra nhiều góc nhìn về câu hỏi của người dùng, mục tiêu của bạn là giúp người dùng vượt qua một số hạn chế của tìm kiếm tương đồng dựa trên khoảng cách. 
Cung cấp các câu hỏi thay thế này được phân tách bằng dòng mới.
Đây là câu hỏi: {question}
<|im_end|>
<|im_start|>assistant
"""
    prompt = Prompt(template, ["question"])

    llm_chain = prompt | llm | LineListOutputParser()

    return MultiQueryRetriever(retriever=base_retriever, llm_chain=llm_chain)

# chuỗi retriers
def retriever_chain(base_retriever, llm, retrievers_func):
    return _create_retriever_chain(base_retriever, llm, retrievers_func, 0)
def _create_retriever_chain(base_retriever, llm, retrievers_func, i):
    if i == len(retrievers_func)-1:
        return retrievers_func[i](base_retriever, llm)
    return retrievers_func[i](_create_retriever_chain(base_retriever, llm, retrievers_func, i+1), llm)

def self_query_retriever(base_retriever, llm):
    # use for metadata
    # need to have `docs metadata` and `attributes metadata`
    pass



# retriever biến đổi docs
def _create_filter(**kwargs):
    """
    Creates a filter based on given parameters.

    Parameters
    ----------
    filter_type: str
        Type of filter to create. Options are 'llm_chain_filter', 'llm_listwise_rerank', 'embeddings_filter', and 'document_compressor_pipeline'.
    llm: LLM
        Language model to use in filter.
    top_n: int
        Number of results to return from filter.
    embeddings: Embeddings
        Embeddings to use in filter.
    similarity_threshold: float
        Similarity threshold to use in filter.
    chunk_size: int
        Chunk size to use in document compressor pipeline.
    chunk_overlap: int
        Chunk overlap to use in document compressor pipeline.
    separator: str
        Separator to use in document compressor pipeline.

    Returns
    -------
    Filter
        The created filter.
    """
    try:
        filter_type = kwargs['filter_type']
        if filter_type == 'llm_chain_filter':
            return LLMChainFilter.from_llm(kwargs['llm'])
        elif filter_type == 'llm_listwise_rerank':
            return LLMListwiseRerank.from_llm(kwargs['llm'], kwargs['top_n']) # with_structured_output model
        elif filter_type == 'embeddings_filter':
            return EmbeddingsFilter(embeddings=kwargs['embeddings'], similarity_threshold=kwargs['similarity_threshold'])
        elif filter_type == 'document_compressor_pipeline':
            splitter = CharacterTextSplitter(chunk_size=kwargs['chunk_size'], chunk_overlap=kwargs['chunk_overlap'], separator=kwargs['separator'])
            redundant_filter = EmbeddingsRedundantFilter(embeddings=kwargs['embeddings'])
            relevant_filter = EmbeddingsFilter(embeddings=kwargs['embeddings'], similarity_threshold=kwargs['similarity_threshold'])
            return DocumentCompressorPipeline(transformers=[splitter, redundant_filter, relevant_filter])
        
        elif filter_type == 'rerank':
            return FlashrankRerank()
        else:
            print("Default LLMChainFilter loaded")
            return LLMChainFilter.from_llm(kwargs['llm'])
    except:
        raise f"Paramerter Error: {kwargs.keys()}"
def contextual_compression_retriever(base_retriever, **kwargs): # nén docs sau khi tìm kếm
    _filter = _create_filter(**kwargs)
    return ContextualCompressionRetriever(base_compressor=_filter, base_retriever=base_retriever)


# combine multi retriever
def ensemble_retriever(retrievers: List, weights: List[int]):
    return EnsembleRetriever(retrievers = retrievers, weights = weights)