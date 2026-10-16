from pathlib import Path

from apps.rag.vector_store import PolicyVectorStore


def main():
    project_root = Path(__file__).resolve().parents[2]
    index_path = project_root / "apps" / "rag" / "faiss_policy_index"

    vector_store = PolicyVectorStore()
    vector_store.load(index_path)

    results = vector_store.search_with_scores(
        query="Does the policy cover pre-existing diseases?",
        policy_id="POL-1001",
        k=3,
    )

    for rank, (document, score) in enumerate(results, start=1):
        print(f"\nRank: {rank}")
        print(f"Distance: {score:.4f}")
        print(f"Policy ID: {document.metadata.get('policy_id')}")
        print(f"Content:\n{document.page_content}")


if __name__ == "__main__":
    main()