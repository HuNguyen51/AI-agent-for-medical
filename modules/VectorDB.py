from langchain_community.vectorstores import FAISS

from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PyPDFLoader, TextLoader

from langchain.text_splitter import RecursiveCharacterTextSplitter

from configs.setup import save_local_path, chunk_size, chunk_overlap
class VectorDB:
    def __init__(self, embedding, 
                        chunk_size = chunk_size, 
                        chunk_overlap = chunk_overlap, 
                        save_local_path = None):
        self.embedding = embedding
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.save_local_path = save_local_path

    def _create_db(self, documents):
        chunks = self.text_splitter.split_documents(documents)
        vectorstore = FAISS.from_documents(chunks, self.embedding)
        
        if self.save_local_path:
            vectorstore.save_local(self.save_local_path)
        return vectorstore
    
    def create_db_from_texts(self, data_path):
        loader = DirectoryLoader(data_path, glob="*.txt", loader_cls = TextLoader, loader_kwargs={"encoding": "utf-8"})
        documents = loader.load()
        
        return self._create_db(documents)

    def create_db_from_pdf(self, data_path):
        loader = DirectoryLoader(data_path, glob="*.pdf", loader_cls = PyPDFLoader)
        documents = loader.load()

        return self._create_db(documents)
