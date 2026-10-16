
from apps.rag.policy_tool import search_policy


def main():
    result = search_policy.invoke({
        "question": "What is the room-rent limit?",
        "policy_id": "POL-1001",
    })

    print("RAG tool result:")
    print(result)


if __name__ == "__main__":
    main()
