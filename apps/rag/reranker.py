from sentence_transformers import CrossEncoder
from langchain_core.documents import Document


class PolicyReranker:
    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
    ):
        self.model = CrossEncoder(model_name)

    def rerank(
        self,
        question: str,
        documents: list[Document],
        top_n: int = 3,
    ) -> list[tuple[Document, float]]:
        if not question.strip():
            raise ValueError("Question cannot be empty")

        if top_n <= 0:
            raise ValueError("top_n must be greater than zero")

        if not documents:
            return []

        pairs = [
            (question, document.page_content)
            for document in documents
        ]

        scores = self.model.predict(pairs)

        ranked = sorted(
            zip(documents, scores),
            key=lambda item: float(item[1]),
            reverse=True,
        )

        return [
            (document, float(score))
            for document, score in ranked[:top_n]
        ]