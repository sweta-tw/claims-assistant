
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

load_dotenv()


class EmbeddingService:
    """Generate embeddings for policy documents and user queries."""

    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )

    def embed_documents(
        self,
        documents: list[Document],
    ) -> list[list[float]]:
        """Convert document chunks into numerical vectors."""

        texts = [document.page_content for document in documents]

        if not texts:
            return []

        return self.embeddings.embed_documents(texts)

    def embed_query(self, query: str) -> list[float]:
        """Convert a user question into a numerical vector."""

        if not query.strip():
            raise ValueError("Query cannot be empty")

        return self.embeddings.embed_query(query)
