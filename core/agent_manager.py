import os
from typing import List, Dict, Any, Optional
from smolagents import OpenAIServerModel, ToolCallingAgent
try:
    from smolagents import LiteLLMModel as MultiModel
except ImportError:
    # If LiteLLMModel not available, fallback to OpenAIServerModel for everything OpenAI-compatible
    MultiModel = OpenAIServerModel

from openai import OpenAI
import httpx
from core.config import settings

class AgentManager:
    def __init__(self, tools: List[Any]):
        self.tools = tools
        self.model = self._setup_model()
        self.agent = self._create_agent()

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
            # Using LiteLLM style or OpenAIServerModel for HF Inference API
            # because HF Inference API is OpenAI-compatible now
            openai_client = OpenAI(
                base_url="https://api-inference.huggingface.co/v1/",
                api_key=settings.HF_API_TOKEN,
            )
            return OpenAIServerModel(model_id=settings.HF_MODEL_ID, client=openai_client)
        
        elif settings.PROVIDER == "nvidia":
            if not settings.NVIDIA_API_KEY:
                raise ValueError("NVIDIA_API_KEY is required for nvidia provider")
            # NVIDIA Nim is OpenAI compatible
            openai_client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=settings.NVIDIA_API_KEY,
            )
            return OpenAIServerModel(model_id=settings.NVIDIA_MODEL_ID, client=openai_client)
        
        else:
            raise ValueError(f"Unknown provider: {settings.PROVIDER}")

    def _create_agent(self) -> ToolCallingAgent:
        return ToolCallingAgent(
            tools=self.tools,
            model=self.model,
            max_steps=settings.MAX_STEPS,
            verbosity_level=1,
        )

    def run(self, task: str, history: List[Dict[str, str]] = None) -> Any:
        # Reset memory to avoid session leaks
        self.agent.memory.reset()
        return self.agent.run(task)

    def reset(self):
        self.agent = self._create_agent()
