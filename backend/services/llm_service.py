import os
import json
import logging
from typing import Dict, Any, Optional

from backend.config import settings

logger = logging.getLogger(__name__)

# Try importing mistralai SDK, fallback to openai SDK if needed
try:
    from mistralai import Mistral
    HAS_MISTRAL_SDK = True
except ImportError:
    HAS_MISTRAL_SDK = False

try:
    from openai import OpenAI
    HAS_OPENAI_SDK = True
except ImportError:
    HAS_OPENAI_SDK = False

class LLMService:
    """Unified LLM service supporting Mistral AI as primary provider with OpenAI fallback."""

    def __init__(self):
        self.provider = None
        self.client = None
        self.model = None

        mistral_key = settings.MISTRAL_API_KEY or os.getenv("MISTRAL_API_KEY", "")
        openai_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY", "")

        # 1. Prefer Mistral AI if MISTRAL_API_KEY is configured
        if mistral_key:
            self.provider = "mistral"
            self.model = settings.MISTRAL_MODEL or os.getenv("MISTRAL_MODEL", "mistral-small-latest")
            if HAS_MISTRAL_SDK:
                logger.info(f"Initializing Mistral AI client with model '{self.model}' using mistralai SDK.")
                self.client = Mistral(api_key=mistral_key)
            elif HAS_OPENAI_SDK:
                logger.info(f"Initializing Mistral AI client with model '{self.model}' using OpenAI-compatible client.")
                self.client = OpenAI(api_key=mistral_key, base_url="https://api.mistral.ai/v1")
            else:
                logger.error("Neither mistralai nor openai python package is installed.")

        # 2. Fallback to OpenAI if OPENAI_API_KEY is configured
        elif openai_key and HAS_OPENAI_SDK:
            self.provider = "openai"
            self.model = settings.OPENAI_MODEL or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            base_url = settings.OPENAI_BASE_URL or os.getenv("OPENAI_BASE_URL", None)
            kwargs = {"api_key": openai_key}
            if base_url:
                kwargs["base_url"] = base_url
            logger.info(f"Initializing OpenAI client with model '{self.model}'.")
            self.client = OpenAI(**kwargs)
        else:
            logger.warning("No API key configured for Mistral AI (MISTRAL_API_KEY) or OpenAI. Using heuristic fallbacks.")

    def is_available(self) -> bool:
        return self.client is not None

    def generate_text(self, system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
        """Generates text using Mistral AI or OpenAI provider."""
        if not self.client:
            logger.warning("LLM client not configured. Returning empty string for fallback processing.")
            return ""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            if self.provider == "mistral" and HAS_MISTRAL_SDK and isinstance(self.client, Mistral):
                response = self.client.chat.complete(
                    model=self.model,
                    messages=messages,
                    temperature=temperature
                )
                return response.choices[0].message.content.strip()
            else:
                # OpenAI or OpenAI-compatible client
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature
                )
                return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error during LLM text generation ({self.provider}): {e}")
            return ""

    def generate_structured(self, system_prompt: str, user_prompt: str, schema_description: str = "") -> Optional[Dict[str, Any]]:
        """Generates structured JSON output matching requested schema."""
        if not self.client:
            logger.warning("LLM client not configured. Skipping structured generation.")
            return None

        prompt_with_json_instruction = (
            f"{user_prompt}\n\n"
            f"IMPORTANT: Respond ONLY with a valid, parsable JSON object matching this schema. "
            f"Do NOT include markdown formatting or extra commentary.\nSchema:\n{schema_description}"
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_with_json_instruction}
        ]

        try:
            if self.provider == "mistral" and HAS_MISTRAL_SDK and isinstance(self.client, Mistral):
                response = self.client.chat.complete(
                    model=self.model,
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=0.2
                )
                content = response.choices[0].message.content.strip()
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    response_format={"type": "json_object"},
                    temperature=0.2
                )
                content = response.choices[0].message.content.strip()

            # Clean markdown code block fences if present in output
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            return json.loads(content.strip())
        except Exception as e:
            logger.error(f"Error during LLM structured generation ({self.provider}): {e}")
            return None

llm_service = LLMService()
