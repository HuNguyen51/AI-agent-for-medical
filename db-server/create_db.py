from langchain_chroma import Chroma
from langchain_community.vectorstores import FAISS

from langchain_community.document_loaders import DirectoryLoader
from langchain_community.document_loaders import PyPDFLoader, TextLoader

from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_huggingface import HuggingFaceEmbeddings

class VectorDB:
    def __init__(self, vector_engine,
                        embedding, 
                        chunk_size, 
                        chunk_overlap):
        """
        Initialize VectorDB

        Args:
            vector_engine: Vector search library to use
            embedding: Embedding model to use
            chunk_size: Number of characters in each chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.vector_engine = vector_engine
        self.embedding = embedding
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def create_db(self, data_path, vectorstore_path=None):
        """
        Create vector database from given path.

        Args:
            data_path: Path to folder containing text and pdf files.
            vectorstore_path: Path to save vector database.

        Returns:
            VectorDB instance.
        """
        documents = self.__create_db_from_texts(data_path)
        documents += self.__create_db_from_pdf(data_path)
        chunks = self.text_splitter.split_documents(documents)
        
        if vectorstore_path is not None:
            if self.vector_engine == Chroma:
                vectorstore = self.vector_engine.from_documents(chunks, self.embedding, persist_directory=vectorstore_path)
                return vectorstore
            
            if self.vector_engine == FAISS:
                vectorstore = self.vector_engine.from_documents(chunks, self.embedding)
                vectorstore.save_local(vectorstore_path)
                return vectorstore
        
        vectorstore = self.vector_engine.from_documents(chunks, self.embedding)
        return vectorstore
    
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

if __name__ == "__main__":
    #  path: ~/db-server
    import yaml
    with open("./configs/vectorstore.yaml") as f:
        configs=yaml.safe_load(f)


    embedding_function = HuggingFaceEmbeddings(
        model_name=configs['model_name'],
        model_kwargs=configs['model_kwargs'],
        encode_kwargs=configs['encode_kwargs']
    )

    vdb = VectorDB(Chroma, embedding_function, configs['chunk_size'], configs['chunk_overlap'])
    _ = vdb.create_db(configs['data_source_path'], configs['vectorstore_path'])