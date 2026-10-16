
from pathlib import Path

from apps.rag.vector_store import PolicyVectorStore
from apps.rag.retriever import PolicyRetriever


def main():
    project_root = Path(__file__).resolve().parents[2]
    index_path = project_root / "apps" / "rag" / "faiss_policy_index"

    vector_store = PolicyVectorStore()
    vector_store.load(index_path)

    retriever = PolicyRetriever(vector_store)

    test_cases = [
        {
            "question": "What is the room-rent limit?",
            "expected_text": "INR 5,000 per day",
        },
        {
            "question": "How long is the waiting period for pre-existing diseases?",
            "expected_text": "24 months",
        },
        {
            "question": "Which documents are required for a hospitalization claim?",
            "expected_text": "discharge summary",
        },
    ]

    passed = 0

    for case in test_cases:
        documents = retriever.retrieve(
            question=case["question"],
            policy_id="POL-1001",
            k=3,
        )

        retrieved_text = " ".join(
            document.page_content.lower()
            for document in documents
        )

        success = case["expected_text"].lower() in retrieved_text

        if success:
            passed += 1

        print(f"\nQuestion: {case['question']}")
        print(f"Expected evidence: {case['expected_text']}")
        print(f"Retrieved evidence found: {success}")

        if not success:
            print("Retrieved chunks:")
            for document in documents:
                print("-", document.page_content)

    print(f"\nRetrieval evidence checks: {passed}/{len(test_cases)}")


if __name__ == "__main__":
    main()
