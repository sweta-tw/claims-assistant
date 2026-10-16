
from apps.rag.vector_store import PolicyVectorStore
from apps.rag.retriever import PolicyRetriever
from apps.rag.policy_qa import PolicyQA
from apps.rag.pipeline_eval_dataset import PIPELINE_CASES


def main():
    vector_store = PolicyVectorStore()

    from pathlib import Path

    project_root = Path(__file__).resolve().parents[2]
    index_path = project_root / "apps" / "rag" / "faiss_policy_index"
    vector_store.load(index_path)

    retriever = PolicyRetriever(vector_store)
    policy_qa = PolicyQA(retriever)

    total = len(PIPELINE_CASES)
    answerability_correct = 0
    answer_content_correct = 0
    citation_valid_count = 0

    for case in PIPELINE_CASES:
        print("\n" + "=" * 70)
        print("Question:", case["question"])

        try:
            result = policy_qa.ask(
                question=case["question"],
                policy_id=case["policy_id"],
            )
        except Exception as exc:
            print("ERROR:", type(exc).__name__, str(exc))
            continue

        answer = result.get("answer", "")
        sources = result.get("sources", [])
        validated = result.get("validated", False)

        print("Answer:", answer)
        print("Validated:", validated)

        abstained = (
            not validated
            or "could not find sufficient evidence" in answer.lower()
            or "could not find relevant evidence" in answer.lower()
            or "could not validate" in answer.lower()
        )

        expected_answerable = case["should_answer"]
        actual_answerable = not abstained

        if actual_answerable == expected_answerable:
            answerability_correct += 1

        expected = case["expected_answer_contains"]

        if expected and expected.lower() in answer.lower():
            answer_content_correct += 1

        citation_ids = {
            source.get("id")
            for source in sources
            if source.get("id")
        }

        import re
        cited_ids = set(re.findall(r"\[(S\d+)\]", answer))

        if cited_ids and cited_ids.issubset(citation_ids):
            citation_valid_count += 1

    print("\n" + "=" * 70)
    print("PIPELINE EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Cases: {total}")
    print(
        f"Answerability accuracy: "
        f"{answerability_correct}/{total} "
        f"({answerability_correct / total:.0%})"
    )
    print(
        f"Expected-answer phrase found: "
        f"{answer_content_correct}/{total}"
    )
    print(
        f"Answers with valid source references: "
        f"{citation_valid_count}/{total}"
    )


if __name__ == "__main__":
    main()
