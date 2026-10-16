
from langchain_core.documents import Document

from apps.rag.vector_store import PolicyVectorStore
from apps.rag.reranker import PolicyReranker


class PolicyRetriever:
    def __init__(self, vector_store: PolicyVectorStore):
        self.vector_store = vector_store
        self.reranker = PolicyReranker()

    def retrieve(
        self,
        question: str,
        policy_id: str | None = None,
        candidate_k: int = 10,
        top_n: int = 3,
    ) -> list[tuple[Document, float]]:
        if not question.strip():
            raise ValueError("Question cannot be empty")

        candidates = self.vector_store.search(
            query=question,
            policy_id=policy_id,
            k=candidate_k,
        )

        return self.reranker.rerank(
            question=question,
            documents=candidates,
            top_n=top_n,
        )
