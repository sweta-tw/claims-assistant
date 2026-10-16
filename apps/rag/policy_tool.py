
import json
from pathlib import Path

from langchain_core.tools import tool

from apps.rag.vector_store import PolicyVectorStore
from apps.rag.retriever import PolicyRetriever
from apps.rag.policy_qa import PolicyQA


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INDEX_PATH = PROJECT_ROOT / "apps" / "rag" / "faiss_policy_index"

_policy_qa = None


def get_policy_qa() -> PolicyQA:
    """Initialize the RAG pipeline once and reuse it."""

    global _policy_qa

    if _policy_qa is None:
        vector_store = PolicyVectorStore()
        vector_store.load(INDEX_PATH)

        retriever = PolicyRetriever(vector_store)
        _policy_qa = PolicyQA(retriever)

    return _policy_qa


@tool
def search_policy(question: str, policy_id: str) -> str:
    """Answer an insurance policy question using retrieved policy
    evidence. Use this for coverage, exclusions, waiting periods,
    room-rent limits, and required policy documents. This tool
    does not determine whether an individual claim is approved."""

    try:
        policy_qa = get_policy_qa()

        result = policy_qa.ask(
            question=question,
            policy_id=policy_id,
        )

        return json.dumps(result, ensure_ascii=False)

    except Exception:
        # Do not expose internal errors to the model or user.
        return json.dumps({
            "answer": "Policy lookup failed. Please try again.",
            "sources": [],
            "validated": False,
            "validation_reason": "Policy lookup encountered an error.",
        })
