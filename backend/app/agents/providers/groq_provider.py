import json
import logging
from typing import Any, Dict

from groq import AsyncGroq, RateLimitError
from groq.types.chat import ChatCompletion
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from app.agents.providers.base import LLMProvider

logger = logging.getLogger(__name__)

class GroqProvider(LLMProvider):
    """LLM Provider for Groq API."""

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        api_key = self.config.get("groq_api_key")
        if not api_key:
            raise ValueError("Groq API key is missing from configuration.")
        
        self.model = self.config.get("ai_model", "openai/gpt-oss-120b")
        self.temperature = self.config.get("ai_temperature", 0.2)
        self.max_tokens = self.config.get("ai_max_output_tokens", 4096)
        
        # Groq client automatically uses GROQ_API_KEY environment variable if not passed,
        # but we explicitly pass it for clarity.
        self.client = AsyncGroq(
            api_key=api_key,
            timeout=self.config.get("ai_timeout_seconds", 30.0),
            max_retries=self.config.get("ai_max_retries", 2),
        )

    @retry(
        wait=wait_exponential(multiplier=1.5, min=2, max=10),
        stop=stop_after_attempt(4),
        retry=retry_if_exception_type(RateLimitError),
        reraise=True
    )
    async def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from a prompt."""
        try:
            response: ChatCompletion = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
                temperature=kwargs.get("temperature", self.temperature),
                max_completion_tokens=kwargs.get("max_tokens", self.max_tokens),
            )
            return response.choices[0].message.content or ""
        except RateLimitError as e:
            logger.warning(f"Groq rate limit exceeded (generate): {str(e)}. Retrying...")
            raise
        except Exception as e:
            logger.error(f"Groq API error (generate): {str(e)}")
            raise RuntimeError(f"Failed to generate text from Groq: {str(e)}")

    @retry(
        wait=wait_exponential(multiplier=1.5, min=2, max=10),
        stop=stop_after_attempt(4),
        retry=retry_if_exception_type(RateLimitError),
        reraise=True
    )
    async def generate_json(self, prompt: str, schema: Dict[str, Any] | None = None, **kwargs) -> Dict[str, Any]:
        """Generate a structured JSON response."""
        try:
            # We explicitly ask for JSON format
            system_prompt = "You must respond with valid JSON. Do not include markdown code blocks or any other text outside the JSON object."
            if schema:
                system_prompt += f"\nYour JSON must conform to this schema:\n{json.dumps(schema)}"

            response: ChatCompletion = await self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
                temperature=kwargs.get("temperature", self.temperature),
                max_completion_tokens=kwargs.get("max_tokens", self.max_tokens),
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or "{}"
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Groq JSON parse error: {str(e)}\nContent: {content}")
            raise ValueError(f"Failed to parse JSON response from Groq: {str(e)}")
        except RateLimitError as e:
            logger.warning(f"Groq rate limit exceeded (generate_json): {str(e)}. Retrying...")
            raise
        except Exception as e:
            logger.error(f"Groq API error (generate_json): {str(e)}")
            raise RuntimeError(f"Failed to generate JSON from Groq: {str(e)}")
