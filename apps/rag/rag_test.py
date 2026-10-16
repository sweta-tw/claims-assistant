
from pathlib import Path

from apps.rag.loader import load_policy
from apps.rag.chunker import split_documents
from apps.rag.vector_store import PolicyVectorStore
from apps.rag.retriever import PolicyRetriever
from apps.rag.policy_qa import PolicyQA


def main():
    project_root = Path(__file__).resolve().parents[2]

    policy_path = (
        project_root
        / "apps"
        / "documents"
        / "policy_POL-1001.txt"
    )

    index_path = (
        project_root
        / "apps"
        / "rag"
        / "faiss_policy_index"
    )

    # 1. Create the vector store.
    vector_store = PolicyVectorStore()

    # 2. Load an existing index or build one.
    if (
        (index_path / "index.faiss").exists()
        and (index_path / "index.pkl").exists()
    ):
        vector_store.load(index_path)
        print("Loaded saved FAISS index")

    else:
        policy = load_policy(policy_path)

        chunks = split_documents(
            [policy],
            chunk_size=500,
            chunk_overlap=80,
        )

        print("Chunks created:", len(chunks))

        vector_store.build(chunks)
        vector_store.save(index_path)

        print("Built and saved FAISS index")

    # 3. Connect retrieval to answer generation.
    retriever = PolicyRetriever(vector_store)
    policy_qa = PolicyQA(retriever)

    # 4. Ask a question.
    result = policy_qa.ask(
        question="What is the room-rent limit?",
        policy_id="POL-1001",
    )

    print("\nAnswer:")
    print(result["answer"])

    print("\nSources:")
    for source in result["sources"]:
        print("Policy:", source["policy_id"])
        print("Content:", source["content"])


if __name__ == "__main__":
    main()
