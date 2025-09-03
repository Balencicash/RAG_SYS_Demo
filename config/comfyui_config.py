"""
ComfyUI Configuration for RAG Document QA System.
"""

from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings


class ComfyUIConfig(BaseSettings):
    """ComfyUI configuration settings."""

    # ComfyUI Server Configuration
    comfyui_host: str = "127.0.0.1"
    comfyui_port: int = 8188
    comfyui_enabled: bool = False

    # Workflow Configuration
    default_workflow_path: str = "workflows/default.json"
    output_directory: str = "outputs/comfyui"

    # API Configuration
    api_timeout: int = 300  # 5 minutes
    max_queue_size: int = 10

    # Image Generation Settings
    default_width: int = 512
    default_height: int = 512
    default_steps: int = 20
    default_cfg: float = 7.0
    default_sampler: str = "euler"
    default_scheduler: str = "normal"

    # Model Settings
    checkpoint_model: str = "sd_xl_base_1.0.safetensors"
    vae_model: str = "sdxl_vae.safetensors"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }

    @property
    def base_url(self) -> str:
        """Get the base URL for ComfyUI API."""
        return f"http://{self.comfyui_host}:{self.comfyui_port}"

    @property
    def is_enabled(self) -> bool:
        """Check if ComfyUI is enabled."""
        return self.comfyui_enabled

    def get_workflow_config(self) -> Dict[str, Any]:
        """Get default workflow configuration."""
        return {
            "width": self.default_width,
            "height": self.default_height,
            "steps": self.default_steps,
            "cfg": self.default_cfg,
            "sampler_name": self.default_sampler,
            "scheduler": self.default_scheduler,
            "checkpoint": self.checkpoint_model,
            "vae": self.vae_model,
        }
