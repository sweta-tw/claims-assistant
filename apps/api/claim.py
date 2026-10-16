
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from apps.models.claims import Claim, ClaimStatusUpdate, claimCreate
from apps.services.claim_services import ClaimService
from apps.security.login_rate_limit import (
    check_login_rate_limit,
    record_failed_login,
    reset_login_rate_limit,
)


router = APIRouter()
claim_service = ClaimService()
bearer_scheme = HTTPBearer(auto_error=False)

JWT_ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 30
MINIMUM_SIGNING_KEY_BYTES = 32

VALID_ROLES = {"viewer", "claims-agent", "admin"}
WRITE_ROLES = {"claims-agent", "admin"}


class LoginRequest(BaseModel):
    username: str
    password: str


def get_signing_key() -> str:
    key = os.getenv("JWT_SECRET_KEY")

    if not key or len(key.encode("utf-8")) < MINIMUM_SIGNING_KEY_BYTES:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not configured correctly",
        )

    return key


def get_configured_role() -> str:
    role = os.getenv("API_USER_ROLE", "viewer")

    if role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Invalid configured user role",
        )

    return role


def create_access_token(username: str, role: str) -> str:
    if not username or role not in VALID_ROLES:
        raise ValueError("A valid username and role are required")

    now = datetime.now(timezone.utc)

    payload = {
        "sub": username,
        "role": role,
        "iat": now,
        "exp": now + timedelta(minutes=TOKEN_EXPIRE_MINUTES),
    }

    return jwt.encode(
        payload,
        get_signing_key(),
        algorithm=JWT_ALGORITHM,
    )


def unauthorized(detail: str = "Invalid or expired authentication token"):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> dict:
    if credentials is None:
        raise unauthorized("Authentication required")

    try:
        payload = jwt.decode(
            credentials.credentials,
            get_signing_key(),
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "role", "iat", "exp"]},
        )
    except jwt.InvalidTokenError:
        raise unauthorized() from None

    username = payload.get("sub")
    role = payload.get("role")

    if (
        not isinstance(username, str)
        or not username.strip()
        or not isinstance(role, str)
        or role not in VALID_ROLES
    ):
        raise unauthorized("Invalid authentication token")

    return {"username": username, "role": role}


def require_role(*allowed_roles: str):
    def role_checker(
        user: Annotated[dict, Depends(get_current_user)],
    ) -> dict:
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this operation",
            )

        return user

    return role_checker


@router.post("/auth/token")
def login(request: Request, login_request: LoginRequest):
    expected_username = os.getenv("API_USERNAME")
    expected_password = os.getenv("API_PASSWORD")

    if not expected_username or not expected_password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Login is not configured",
        )

    signing_key = get_signing_key()
    configured_role = get_configured_role()

    # Check existing failed-attempt counters before validating credentials.
    check_login_rate_limit(request, login_request.username)

    username_matches = secrets.compare_digest(
        login_request.username.encode("utf-8"),
        expected_username.encode("utf-8"),
    )
    password_matches = secrets.compare_digest(
        login_request.password.encode("utf-8"),
        expected_password.encode("utf-8"),
    )

    if not (username_matches and password_matches):
        record_failed_login(request, login_request.username)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Only issue a token after successful authentication and counter reset.
    reset_login_rate_limit(request, login_request.username)

    access_token = create_access_token(
        login_request.username,
        configured_role,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": TOKEN_EXPIRE_MINUTES * 60,
    }


@router.get("/claims", response_model=list[Claim])
def list_claims(
    user: Annotated[dict, Depends(require_role(*VALID_ROLES))],
):
    return claim_service.get_all_claims()


@router.get("/claims/{claim_id}", response_model=Claim)
def get_claim(
    claim_id: str,
    user: Annotated[dict, Depends(require_role(*VALID_ROLES))],
):
    claim = claim_service.get_claim(claim_id)

    if claim is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found",
        )

    return claim


@router.post("/claims", response_model=Claim)
def create_claim(
    claim: claimCreate,
    user: Annotated[dict, Depends(require_role(*WRITE_ROLES))],
):
    return claim_service.create_claim(claim.customer, claim.amount)


@router.put("/claims/{claim_id}/status", response_model=Claim)
def update_claim_status(
    claim_id: str,
    request: ClaimStatusUpdate,
    user: Annotated[dict, Depends(require_role(*WRITE_ROLES))],
):
    claim = claim_service.update_claim_status(
        claim_id,
        request.status,
    )

    if claim is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found",
        )

    return claim



@router.delete("/claims/{claim_id}")
def delete_claim(
    claim_id: str,
    user: Annotated[dict, Depends(require_role(*WRITE_ROLES))],
):
    deleted = claim_service.delete_claim(claim_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim {claim_id} not found",
        )

    return {
        "message": f"Claim {claim_id} deleted successfully",
        "claim_id": claim_id,
    }

