from enum import Enum
from pydantic import BaseModel, Field





class ClaimStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SETTLED = "SETTLED"

class Claim(BaseModel):
    id: str
    customer: str
    amount: float = Field(gt=0)
    status: ClaimStatus

class claimCreate(BaseModel):
    customer: str =Field(min_length=1)
    amount: float =Field(gt=0)

class ClaimStatusUpdate(BaseModel):
    status: ClaimStatus
