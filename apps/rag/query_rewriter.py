
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class QueryRewriter:
    def __init__(self):
        self.client = OpenAI()
        self.model = "gpt-5-nano"

    def rewrite(
        self,
        question: str,
        policy_id: str,
    ) -> str:
        if not question.strip():
            raise ValueError("Question cannot be empty")

        if not policy_id.strip():
            raise ValueError("Policy ID cannot be empty")

        response = self.client.responses.create(
            model=self.model,
            input=f"""
Rewrite the user's insurance policy question into a
clear search query for semantic retrieval.

Policy ID: {policy_id}
Original question: {question}

Rules:
- Preserve the user's original intent.
- Do not answer the question.
- Do not invent policy facts.
- Use relevant insurance terminology when appropriate.
- Return only the rewritten query.
"""
        )

        rewritten = response.output_text.strip()

        if not rewritten:
            raise ValueError("Query rewriting returned an empty query")

        return rewritten
