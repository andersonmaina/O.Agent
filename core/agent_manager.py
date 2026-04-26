import os
import requests
from typing import List, Dict, Any, Optional
from smolagents import OpenAIServerModel, ToolCallingAgent, Tool
try:
    from smolagents import LiteLLMModel as MultiModel
except ImportError:
    MultiModel = OpenAIServerModel

from openai import OpenAI
import httpx
from core.config import settings


class AgentManager:
    def __init__(self, tools: List[Any]):
        self.tools = tools
        self.model = self._setup_model()
        self.agent = self._create_agent()

    # ── Model setup ───────────────────────────────────────────────────────────

    def _setup_model(self):
        if settings.PROVIDER == "ollama":
            _http = httpx.Client(
                headers={"ngrok-skip-browser-warning": "1"},
                transport=httpx.HTTPTransport(retries=2),
                timeout=float(settings.TIMEOUT),
            )
            openai_client = OpenAI(
                base_url=f"{settings.OLLAMA_BASE_URL}/v1",
                api_key="ollama",
                http_client=_http,
                timeout=float(settings.TIMEOUT),
            )
            return OpenAIServerModel(model_id=settings.OLLAMA_MODEL, client=openai_client)

        elif settings.PROVIDER == "huggingface":
            if not settings.HF_API_TOKEN:
                raise ValueError("HF_API_TOKEN is required for huggingface provider")
            openai_client = OpenAI(
                base_url="https://api-inference.huggingface.co/v1/",
                api_key=settings.HF_API_TOKEN,
            )
            return OpenAIServerModel(model_id=settings.HF_MODEL_ID, client=openai_client)

        elif settings.PROVIDER == "nvidia":
            if not settings.NVIDIA_API_KEY:
                raise ValueError("NVIDIA_API_KEY is required for nvidia provider")
            openai_client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=settings.NVIDIA_API_KEY,
            )
            return OpenAIServerModel(model_id=settings.NVIDIA_MODEL_ID, client=openai_client)

        else:
            raise ValueError(f"Unknown provider: {settings.PROVIDER}")

    def _create_agent(self) -> ToolCallingAgent:
        # Build a tools manifest so the model knows what it has
        tool_names = ", ".join(t.name for t in self.tools) if self.tools else "none"
        system_prompt_addition = (
            f"You have access to {len(self.tools)} tools: {tool_names}. "
            "Always prefer using the available tools rather than saying you cannot do something."
        )
        return ToolCallingAgent(
            tools=self.tools,
            model=self.model,
            max_steps=settings.MAX_STEPS,
            verbosity_level=1,
        )

    # ── Model / Provider switching ────────────────────────────────────────────

    def switch_model(self, model_id: str, provider: str = None) -> str:
        """Hot-swap the active model (and optionally provider) without restart."""
        provider = provider or settings.PROVIDER
        old = f"{settings.PROVIDER}/{settings.OLLAMA_MODEL}"

        settings.PROVIDER = provider
        if provider == "ollama":
            settings.OLLAMA_MODEL = model_id
        elif provider == "huggingface":
            settings.HF_MODEL_ID = model_id
        elif provider == "nvidia":
            settings.NVIDIA_MODEL_ID = model_id
        else:
            return f"Unknown provider '{provider}'"

        try:
            self.model = self._setup_model()
            self.agent = self._create_agent()
            return f"Switched: {old}  →  {provider}/{model_id}"
        except Exception as e:
            return f"Switch failed: {e}"

    def current_model_info(self) -> str:
        provider = settings.PROVIDER
        if provider == "ollama":
            model = settings.OLLAMA_MODEL
        elif provider == "huggingface":
            model = settings.HF_MODEL_ID
        elif provider == "nvidia":
            model = settings.NVIDIA_MODEL_ID
        else:
            model = "unknown"
        return f"{provider.upper()} / {model}"

    # ── Ollama-specific model management ─────────────────────────────────────

    def list_ollama_models(self) -> List[Dict[str, Any]]:
        """Fetch available models from the Ollama API."""
        try:
            resp = requests.get(
                f"{settings.OLLAMA_BASE_URL}/api/tags",
                headers={"ngrok-skip-browser-warning": "1"},
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json().get("models", [])
        except Exception as e:
            return [{"error": str(e)}]

    def delete_ollama_model(self, model_name: str) -> str:
        """Delete a model from Ollama local storage."""
        try:
            resp = requests.delete(
                f"{settings.OLLAMA_BASE_URL}/api/delete",
                json={"name": model_name},
                headers={"ngrok-skip-browser-warning": "1"},
                timeout=30,
            )
            if resp.status_code == 200:
                return f"Deleted model: {model_name}"
            else:
                return f"Delete failed ({resp.status_code}): {resp.text[:200]}"
        except Exception as e:
            return f"Delete error: {e}"

    # ── Execution ─────────────────────────────────────────────────────────────

    def run(self, task: str, history: List[Dict[str, str]] = None) -> Any:
        # Reset memory to avoid session leaks
        self.agent.memory.reset()
        return self.agent.run(task)

    def reset(self):
        self.agent = self._create_agent()
