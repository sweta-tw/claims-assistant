from pathlib import Path

from langchain_core.documents import Document

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_policy(path: str | Path) -> Document:
    path = Path(path)

    if not path.is_absolute():
        path = PROJECT_ROOT / path

    if not path.exists():
        raise FileNotFoundError(f"Policy document not found: {path}")

    text = path.read_text(encoding="utf-8").strip()

    if not text:
        raise ValueError(f"Policy document is empty: {path}")

    policy_id = path.stem.removeprefix("policy_")

    return Document(
        page_content=text,
        metadata={
            "source": str(path),
            "document_type": "insurance_policy",
            "policy_id": policy_id,
        },
    )