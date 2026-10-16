
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from apps.rag.embeddings import EmbeddingService


class PolicyVectorStore:
    """Build, persist, load, and search a FAISS policy index."""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.index: FAISS | None = None
    

    def build(self, chunks: list[Document]) -> None:
        if not chunks:
            raise ValueError("Cannot build an index without documents")

        self.index = FAISS.from_documents(
            documents=chunks,
            embedding=self.embedding_service.embeddings,
        )

    def save(self, path: str | Path) -> None:
        if self.index is None:
            raise RuntimeError("Build the index before saving")

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.index.save_local(str(path))

    def load(self, path: str | Path) -> None:
        path = Path(path)

        if not (path / "index.faiss").exists():
            raise FileNotFoundError(
                f"FAISS index not found: {path / 'index.faiss'}"
            )

        if not (path / "index.pkl").exists():
            raise FileNotFoundError(
                f"FAISS metadata file not found: {path / 'index.pkl'}"
            )

        self.index = FAISS.load_local(
            str(path),
            self.embedding_service.embeddings,
            allow_dangerous_deserialization=True,
        )

    def search(
        self,
        query: str,
        k: int = 3,
        policy_id: str | None = None,
    ) -> list[Document]:
        if self.index is None:
            raise RuntimeError(
                "Build or load the index before searching"
            )

        if not query.strip():
            raise ValueError("Query cannot be empty")

        if k <= 0:
            raise ValueError("k must be greater than zero")

        search_kwargs = {"k": k}

        if policy_id is not None:
            search_kwargs["filter"] = {
                "policy_id": policy_id
            }
            search_kwargs["fetch_k"] = max(k * 4, 20)

        return self.index.similarity_search(
            query,
            **search_kwargs,
        )



    def search_with_scores(
    self,
    query: str,
    k: int = 3,
    policy_id: str | None = None,):
        if self.index is None:
            raise RuntimeError("Build or load the index before searching")

        if not query.strip():
            raise ValueError("Query cannot be empty")

        if k <= 0:
            raise ValueError("k must be greater than zero")

        search_kwargs = {"k": k}

        if policy_id is not None:
            search_kwargs["filter"] = {"policy_id": policy_id}
            search_kwargs["fetch_k"] = max(k * 4, 20)

        return self.index.similarity_search_with_score(
            query,
            **search_kwargs,
    )
