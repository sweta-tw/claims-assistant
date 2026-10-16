
import re

from apps.rag.retriever import PolicyRetriever
from apps.rag.answer_generator import PolicyAnswerGenerator
from apps.rag.evidence_validator import EvidenceValidator
from apps.rag.evidence_checker import EvidenceChecker
from apps.rag.query_rewriter import QueryRewriter


class PolicyQA:
    def __init__(self, retriever: PolicyRetriever):
        self.retriever = retriever
        self.answer_generator = PolicyAnswerGenerator()
        self.evidence_checker = EvidenceChecker()
        self.evidence_validator = EvidenceValidator()
        self.query_rewriter = QueryRewriter()

    def ask(self, question: str, policy_id: str) -> dict:
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        if not policy_id or not policy_id.strip():
            raise ValueError("Policy ID cannot be empty")

        # 1. Retrieve and rerank policy chunks.
        ranked_documents = self.retriever.retrieve(
            question=question,
            policy_id=policy_id,
            candidate_k=10,
            top_n=3,
        )

        if not ranked_documents:
            return {
                "answer": (
                    "I could not find relevant evidence in the "
                    "specified policy."
                ),
                "sources": [],
                "validated": False,
                "validation_reason": "No evidence was retrieved.",
            }

        # 2. Extract documents from (document, score) pairs.
        documents = [
            document
            for document, score in ranked_documents
        ]

        # 3. Build source references and evidence context.
        sources = []
        context_parts = []

        for i, document in enumerate(documents, start=1):
            source_id = f"S{i}"

            source = {
                "id": source_id,
                "policy_id": document.metadata.get("policy_id"),
                "source": document.metadata.get("source"),
                "content": document.page_content,
            }

            sources.append(source)

            context_parts.append(
                f"[{source_id}]\n"
                f"Policy ID: {source['policy_id']}\n"
                f"Content:\n{source['content']}"
            )

        context = "\n\n---\n\n".join(context_parts)

        # 4. Check whether the evidence is sufficient.
        try:
            sufficiency = self.evidence_checker.check(
                question=question,
                context=context,
            )
        except Exception:
            return {
                "answer": (
                    "I could not verify whether the retrieved "
                    "policy evidence is sufficient. Please review "
                    "the policy sources."
                ),
                "sources": sources,
                "validated": False,
                "validation_reason": (
                    "Evidence sufficiency check failed."
                ),
            }

        if sufficiency.get("sufficient") is not True:
            return {
                "answer": (
                    "I could not find sufficient evidence in the "
                    "retrieved policy passages to answer this "
                    "question reliably."
                ),
                "sources": sources,
                "validated": False,
                "validation_reason": sufficiency.get(
                    "reason",
                    "Evidence was insufficient.",
                ),
            }

        # 5. Generate an answer grounded in the evidence.
        try:
            answer = self.answer_generator.generate(
                question=question,
                context=context,
            )
        except Exception:
            return {
                "answer": (
                    "Policy answer generation failed. Please try "
                    "again or review the retrieved sources."
                ),
                "sources": sources,
                "validated": False,
                "validation_reason": (
                    "Answer generation failed."
                ),
            }

        # 6. Verify that citations reference retrieved sources.
        cited_ids = set(re.findall(r"\[(S\d+)\]", answer))
        valid_ids = {source["id"] for source in sources}

        if not cited_ids or not cited_ids.issubset(valid_ids):
            return {
                "answer": (
                    "I could not validate the answer's source "
                    "references. Please review the policy evidence."
                ),
                "sources": sources,
                "validated": False,
                "validation_reason": (
                    "Missing or invalid source citations."
                ),
            }

        # 7. Validate the answer against the evidence.
        try:
            verification = self.evidence_validator.validate(
                question=question,
                context=context,
                answer=answer,
            )
        except Exception:
            return {
                "answer": (
                    "I could not verify that the answer is fully "
                    "supported by the retrieved policy evidence."
                ),
                "sources": sources,
                "validated": False,
                "validation_reason": (
                    "Evidence validation failed."
                ),
            }

        supported = verification.get("supported") is True
        reason = verification.get(
            "reason",
            "No validation reason provided.",
        )

        if not supported:
            return {
                "answer": (
                    "I could not verify that the proposed answer "
                    "is fully supported by the retrieved policy "
                    "evidence. Please review the sources."
                ),
                "sources": sources,
                "validated": False,
                "validation_reason": reason,
            }

        # 8. Return the validated result and its sources.
        return {
            "answer": answer,
            "sources": sources,
            "validated": True,
            "validation_reason": reason,
        }
