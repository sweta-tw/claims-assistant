
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


class EvidenceValidator:
    """Check whether an answer is supported by policy evidence."""

    def __init__(self):
        self.client = OpenAI()
        self.model = "gpt-5-nano"

    def validate(self, question: str, context: str, answer: str) -> dict:
        response = self.client.responses.create(
            model=self.model,
            input=f"""
You are a strict insurance evidence verifier.

Compare the proposed answer with the supplied policy evidence.

Question:
{question}

Policy evidence:
{context}

Proposed answer:
{answer}

Return exactly one JSON object with these fields:
{{
  "supported": true or false,
  "reason": "Brief explanation"
}}

Set supported to false if the answer contradicts the evidence,
makes a material claim not supported by the evidence, or
states a coverage limit incorrectly.
Do not assume facts that are absent from the evidence.
"""
        )

        import json

        try:
            result = json.loads(response.output_text)
            if (
                not isinstance(result, dict)
                or not isinstance(result.get("supported"), bool)
                or not isinstance(result.get("reason"), str)
            ):
                raise ValueError("Invalid verifier response")

            return result

        except (json.JSONDecodeError, ValueError):
            return {
                "supported": False,
                "reason": "Verifier returned an invalid response.",
            }
