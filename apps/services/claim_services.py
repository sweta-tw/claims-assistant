
import logging

from apps.cache.redis_cache import delete_key, get_json, set_json
from apps.database.connection import get_connection
from apps.exceptions import InvalidClaimStatusError
from apps.models.claims import Claim
from apps.repositories.claim_repository import ClaimRepository


logger = logging.getLogger(__name__)

VALID_STATUSES = {
    "SUBMITTED",
    "UNDER_REVIEW",
    "APPROVED",
    "REJECTED",
    "SETTLED",
}

ALLOWED_TRANSITIONS = {
    "SUBMITTED": {"UNDER_REVIEW"},
    "UNDER_REVIEW": {"APPROVED", "REJECTED"},
    "APPROVED": {"SETTLED"},
    "REJECTED": set(),
    "SETTLED": set(),
}

CACHE_TTL_SECONDS = 60


class ClaimService:

    def __init__(self):
        self.repository = ClaimRepository()
    

    def delete_claim(self, claim_id: str) -> bool:
        deleted = self.repository.delete(claim_id)

        if deleted:
            delete_key(f"claim:{claim_id}")
            logger.info("Deleted claim %s", claim_id)

        return deleted

        
        
        
            



    def get_claim(self, claim_id):
        cache_key = f"claim:{claim_id}"

        # 1. Try Redis first.
        cached_claim = get_json(cache_key)

        if cached_claim is not None:
            try:
                return Claim.model_validate(cached_claim)
            except (ValueError, TypeError):
                logger.warning(
                    "Invalid cached claim for %s; reading from SQLite",
                    claim_id,
                )
                delete_key(cache_key)

        # 2. On a cache miss, read from SQLite.
        claim = self.repository.get_by_id(claim_id)

        if claim is None:
            return None

        # 3. Populate Redis. A Redis failure must not break the read.
        set_json(
            cache_key,
            claim.model_dump(mode="json"),
            ttl_seconds=CACHE_TTL_SECONDS,
        )

        return claim

    def get_all_claims(self):
        # List caching is intentionally not implemented yet.
        return self.repository.get_all()

    def create_claim(self, customer, amount):
        claim = Claim(
            id=f"CLM-{len(self.repository.get_all()) + 1001}",
            customer=customer,
            amount=amount,
            status="SUBMITTED",
        )

        created_claim = self.repository.create(claim)

        # Clear the new claim's key in case it was cached earlier.
        delete_key(f"claim:{created_claim.id}")

        return created_claim

    def update_claim_status(self, claim_id, new_status):
        # Read from SQLite directly so validation uses current persisted state.
        claim = self.repository.get_by_id(claim_id)

        if claim is None:
            return None

        if new_status not in VALID_STATUSES:
            raise InvalidClaimStatusError(
                f"Invalid status: {new_status}"
            )

        current_status = claim.status

        if new_status not in ALLOWED_TRANSITIONS[current_status]:
            raise InvalidClaimStatusError(
                f"Cannot change status from "
                f"{current_status} to {new_status}"
            )

        # Persist the change before invalidating the cache.
        self.repository.update_status(claim_id, new_status)

        claim.status = new_status

        # The next read will fetch the updated claim from SQLite.
        delete_key(f"claim:{claim_id}")

        return claim
