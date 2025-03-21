from langchain_community.embeddings import GPT4AllEmbeddings

class Embedding(GPT4AllEmbeddings):
    def __init__(self, embedding_path):
        super().__init__(model_path = embedding_path)