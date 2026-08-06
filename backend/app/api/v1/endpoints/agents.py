from typing import Any, Dict

from fastapi import APIRouter

from app.agents.coordinator import AgentCoordinator
from app.agents.providers.factory import ProviderFactory

router = APIRouter()


@router.post("/execute", response_model=Dict[str, Any])
async def execute_agent_pipeline(payload: Dict[str, Any]):
    """Execute a test agent pipeline using the AI framework."""
    provider = ProviderFactory.get_provider("dummy", config={})
    coordinator = AgentCoordinator(llm_provider=provider)
    
    # Since we don't have real agents registered yet, this would fail if we actually execute it.
    # But it demonstrates the orchestrator can be instantiated and wired up to an API endpoint.
    
    return {
        "status": "success",
        "message": "Agent framework is ready for agent registration.",
        "run_id": coordinator.run_id,
        "provider": provider.__class__.__name__
    }
