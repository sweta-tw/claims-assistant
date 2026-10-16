from pathlib import Path

from apps.rag.vector_store import PolicyVectorStore
from apps.rag.reranker import PolicyReranker


def main():
    project_root = Path(__file__).resolve().parents[2]
    index_path = (
        project_root / "apps" / "rag" / "faiss_policy_index"
    )

    question = (
        "What is the waiting period for pre-existing diseases?"
    )

    vector_store = PolicyVectorStore()
    vector_store.load(index_path)

    candidates = vector_store.search(
        query=question,
        policy_id="POL-1001",
        k=10,
    )

    reranker = PolicyReranker()
    ranked = reranker.rerank(
        question=question,
        documents=candidates,
        top_n=3,
    )

    for rank, (document, score) in enumerate(ranked, start=1):
        print(f"\nRank: {rank}")
        print(f"Reranker score: {score:.4f}")
        print(document.page_content)


if __name__ == "__main__":
    main()