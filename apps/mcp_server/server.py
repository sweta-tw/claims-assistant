from mcp.server import MCPServer

from apps.models.claims import claimCreate
from apps.services.claim_services import ClaimService




mcp = MCPServer("Claims Assistant")

claim_service = ClaimService()


@mcp.tool()
def get_claim(claim_id: str):
    """Get a claim by its ID."""

    claim = claim_service.get_claim(claim_id)

    if claim is None:
        return {
            "error": f"Claim {claim_id} not found"
        }

    return claim.model_dump()


@mcp.tool()
def create_claim(request: claimCreate):
    """Create a new insurance claim."""

    claim = claim_service.create_claim(
        request.customer,
        request.amount
    )

    return claim.model_dump()


@mcp.tool()
def update_claim_status(
    claim_id: str,
    new_status: str
):
    """Update the status of an insurance claim."""

    try:
        claim = claim_service.update_claim_status(
            claim_id,
            new_status
        )

        if claim is None:
            return {
                "error": f"Claim {claim_id} not found"
            }

        return claim.model_dump()

    except ValueError as error:
        return {
            "error": str(error)
        }


if __name__ == "__main__":
    mcp.run()