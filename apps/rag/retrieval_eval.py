
from pathlib import Path

from apps.rag.vector_store import PolicyVectorStore
from apps.rag.reranker import PolicyReranker
from apps.rag.evaluation_dataset import EVALUATION_CASES


def evaluate():
    project_root = Path(__file__).resolve().parents[2]
    index_path = (
        project_root
        / "apps"
        / "rag"
        / "faiss_policy_index"
    )

    # Load the existing FAISS index.
    vector_store = PolicyVectorStore()
    vector_store.load(index_path)

    # Initialize the reranker.
    reranker = PolicyReranker()

    baseline_hits = 0
    reranked_hits = 0
    total = len(EVALUATION_CASES)

    if total == 0:
        print("No evaluation cases found.")
        return

    for case in EVALUATION_CASES:
        question = case["question"]
        policy_id = case["policy_id"]
        expected = case["expected_text"].lower()

        print("\n" + "=" * 70)
        print(f"Question: {question}")
        print(f"Expected evidence: {case['expected_text']}")

        # 1. Retrieve the top 3 using FAISS.
        baseline_results = vector_store.search_with_scores(
            query=question,
            policy_id=policy_id,
            k=3,
        )

        baseline_text = "\n".join(
            document.page_content
            for document, _ in baseline_results
        ).lower()

        baseline_success = expected in baseline_text

        if baseline_success:
            baseline_hits += 1

        print("\n--- Original FAISS ranking ---")
        print(f"Evidence retrieved: {baseline_success}")

        for rank, (document, distance) in enumerate(
            baseline_results, start=1
        ):
            print(
                f"Rank {rank} | L2 distance: {distance:.4f} | "
                f"{document.page_content[:120]!r}"
            )

        # 2. Retrieve 10 candidates for reranking.
        candidates = vector_store.search(
            query=question,
            policy_id=policy_id,
            k=10,
        )

        # 3. Rerank candidates and retain the top 3.
        reranked_results = reranker.rerank(
            question=question,
            documents=candidates,
            top_n=3,
        )

        reranked_text = "\n".join(
            document.page_content
            for document, _ in reranked_results
        ).lower()

        reranked_success = expected in reranked_text

        if reranked_success:
            reranked_hits += 1

        print("\n--- Reranked results ---")
        print(f"Evidence retrieved: {reranked_success}")

        for rank, (document, score) in enumerate(
            reranked_results, start=1
        ):
            print(
                f"Rank {rank} | Reranker score: {score:.4f} | "
                f"{document.page_content[:120]!r}"
            )

    baseline_rate = baseline_hits / total
    reranked_rate = reranked_hits / total

    print("\n" + "=" * 70)
    print("FINAL EVALUATION")
    print("=" * 70)
    print(
        f"Original FAISS Hit Rate@3: "
        f"{baseline_hits}/{total} ({baseline_rate:.0%})"
    )
    print(
        f"Reranked Hit Rate@3: "
        f"{reranked_hits}/{total} ({reranked_rate:.0%})"
    )
    print(
        f"Change: {(reranked_rate - baseline_rate) * 100:+.1f} "
        "percentage points"
    )


if __name__ == "__main__":
    evaluate()
