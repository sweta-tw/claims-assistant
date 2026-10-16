
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from apps.api.claim import router as claims_router
from apps.api.chat import router as chat_router
from apps.database.init_db import initialize_database
from langgraph_agent import initialize_agent, shutdown_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()

    # Fail startup if AI configuration or MCP connection is invalid.
    await initialize_agent()

    try:
        yield
    finally:
        await shutdown_agent()


app = FastAPI(
    title="Insurance Claims Assistant",
    description="Claims API and authenticated LangGraph/MCP assistant.",
    version="1.1.0",
    lifespan=lifespan,
)

app.include_router(claims_router)
app.include_router(chat_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": "claims-assistant",
    }
