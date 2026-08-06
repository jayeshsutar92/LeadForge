import logging
import uuid
from typing import Any, Dict

from app.agents.context import SharedContext
from app.agents.registry import AgentRegistry
from app.core.redis import build_redis_key, get_redis_client


class AgentCoordinator:
    """Orchestrates agent execution and manages shared context and redis state."""

    def __init__(self, run_id: str | None = None, llm_provider: Any = None):
        self.run_id = run_id or str(uuid.uuid4())
        self.context = SharedContext({"run_id": self.run_id})
        self.llm_provider = llm_provider
        self.redis = get_redis_client()
        self.logger = logging.getLogger("AgentCoordinator")

    def _state_key(self) -> str:
        return build_redis_key("agent_run", self.run_id)

    async def execute_agent(self, agent_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Dynamically instantiate and execute a registered agent."""
        
        self.logger.info(f"[{self.run_id}] Executing agent: {agent_name}")
        
        try:
            agent_class = AgentRegistry.get(agent_name)
        except ValueError as e:
            self.logger.error(str(e))
            raise
            
        agent = agent_class(
            name=agent_name,
            context=self.context,
            llm_provider=self.llm_provider
        )
        
        result = await agent.run(input_data)
        
        # Merge result into shared context
        for k, v in result.items():
            self.context.set(k, v)
            
        return result

    async def execute_pipeline(self, agents: list[str], initial_input: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a sequential pipeline of agents, passing the updated context forward."""
        self.logger.info(f"[{self.run_id}] Starting pipeline with agents: {agents}")
        
        current_input = initial_input
        
        for agent_name in agents:
            current_input = await self.execute_agent(agent_name, current_input)
            
        return self.context.as_dict()
