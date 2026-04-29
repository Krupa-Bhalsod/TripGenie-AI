import os
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from app.tools.embeddings import embeddings
from app.core.config import settings

class VectorStore:
    def __init__(self):
        self.index_path = settings.FAISS_INDEX_PATH
        self.embeddings = embeddings
        self.vector_store = self._load_or_create_index()

    def _load_or_create_index(self):
        if os.path.exists(self.index_path):
            print("Loading existing FAISS index...")
            return FAISS.load_local(
                folder_path=self.index_path, 
                embeddings=self.embeddings,
                allow_dangerous_deserialization=True
            )
        else:
            print("Creating new FAISS index...")
            # Create an empty index with a dummy document so it can be saved and searched
            empty_doc = Document(page_content="empty", metadata={"source": "init"})
            store = FAISS.from_documents([empty_doc], self.embeddings)
            # Make sure the directory exists
            os.makedirs(self.index_path, exist_ok=True)
            store.save_local(self.index_path)
            return store

    def add_documents(self, documents):
        self.vector_store.add_documents(documents)
        self.vector_store.save_local(self.index_path)

    def retrieve(self, query: str, k: int = 3):
        results = self.vector_store.similarity_search(query, k=k)
        return [res.page_content for res in results if res.page_content != "empty"]

# Global instance
vector_store = VectorStore()

def retrieve_context(query: str) -> str:
    """
    Search memory and context based on user query or destination.
    Useful for finding previously saved user preferences or specific destination context.
    """
    results = vector_store.retrieve(query)
    if not results:
        return "No relevant context found."
    return "\n".join(results)
