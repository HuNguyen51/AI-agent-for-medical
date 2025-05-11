from langchain_community.vectorstores import FAISS

from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PyPDFLoader, TextLoader

from langchain.text_splitter import RecursiveCharacterTextSplitter

class VectorDB:
    def __init__(self, embedding, 
                        chunk_size, 
                        chunk_overlap):
        """
        Initialize VectorDB

        Args:
            embedding: Embedding model to use
            chunk_size: Number of characters in each chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.embedding = embedding
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def create_db(self, data_path):
        """
        Create vector database from given path.

        Args:
            data_path: Path to folder containing text and pdf files.

        Returns:
            VectorDB instance.
        """
        documents = self.__create_db_from_texts(data_path)
        documents += self.__create_db_from_pdf(data_path)

        chunks = self.text_splitter.split_documents(documents)
        vectorstore = FAISS.from_documents(chunks, self.embedding)
        return vectorstore # vectorstore.save_local(self.save_local_path)
    
    def __create_db_from_texts(self, data_path):
        
        """
        Create vector database from text files in given path.

        Args:
            data_path: Path to folder containing text files.

        Returns:
            List of documents.
        """
        loader = DirectoryLoader(data_path, glob="*.txt", loader_cls = TextLoader, loader_kwargs={"encoding": "utf-8"})
        documents = loader.load()
        
        return documents

    def __create_db_from_pdf(self, data_path):
        """
        Create vector database from pdf files in given path.

        Args:
            data_path: Path to folder containing pdf files.

        Returns:
            List of documents.
        """
        loader = DirectoryLoader(data_path, glob="*.pdf", loader_cls = PyPDFLoader)
        documents = loader.load()

        return documents
