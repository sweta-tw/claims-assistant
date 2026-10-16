
PIPELINE_CASES = [
    {
        "question": "What is the room-rent limit?",
        "policy_id": "POL-1001",
        "expected_answer_contains": "INR 5,000 per day",
        "should_answer": True,
    },
    {
        "question": "What is the waiting period for pre-existing diseases?",
        "policy_id": "POL-1001",
        "expected_answer_contains": "24 months",
        "should_answer": True,
    },
    {
        "question": "How long must a patient be hospitalized?",
        "policy_id": "POL-1001",
        "expected_answer_contains": "24 hours",
        "should_answer": True,
    },
    {
        "question": "Which documents are required for a hospitalization claim?",
        "policy_id": "POL-1001",
        "expected_answer_contains": "discharge summary",
        "should_answer": True,
    },
    {
        "question": "Does this policy cover dental implants?",
        "policy_id": "POL-1001",
        "expected_answer_contains": None,
        "should_answer": False,
    },
    {
        "question": "What is the capital of France?",
        "policy_id": "POL-1001",
        "expected_answer_contains": None,
        "should_answer": False,
    },
]
