"""
ComfyUI Service for RAG Document QA System.
Integrates ComfyUI for AI image generation capabilities.
"""

import json
import uuid
import websockets
import aiohttp
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from config.comfyui_config import ComfyUIConfig
from src.core.exceptions import ComfyUIError
from src.utils.logger import get_logger
from src.utils.watermark import protect_class

logger = get_logger(__name__)


@protect_class
class ComfyUIWorkflow:
    """ComfyUI workflow management."""

    def __init__(self, workflow_data: Dict[str, Any]):
        self.workflow_data = workflow_data
        self.client_id = str(uuid.uuid4())

    def update_prompt(self, prompt: str, node_id: str = "6") -> None:
        """Update the text prompt in the workflow."""
        if node_id in self.workflow_data:
            self.workflow_data[node_id]["inputs"]["text"] = prompt

    def update_settings(self, **kwargs) -> None:
        """Update generation settings."""
        # Update KSampler settings (typically node 3)
        if "3" in self.workflow_data:
            sampler_node = self.workflow_data["3"]["inputs"]
            if "steps" in kwargs:
                sampler_node["steps"] = kwargs["steps"]
            if "cfg" in kwargs:
                sampler_node["cfg"] = kwargs["cfg"]
            if "sampler_name" in kwargs:
                sampler_node["sampler_name"] = kwargs["sampler_name"]
            if "scheduler" in kwargs:
                sampler_node["scheduler"] = kwargs["scheduler"]

        # Update Empty Latent Image settings (typically node 5)
        if "5" in self.workflow_data:
            latent_node = self.workflow_data["5"]["inputs"]
            if "width" in kwargs:
                latent_node["width"] = kwargs["width"]
            if "height" in kwargs:
                latent_node["height"] = kwargs["height"]

    def get_prompt_dict(self) -> Dict[str, Any]:
        """Get the workflow as a prompt dictionary."""
        return {"prompt": self.workflow_data, "client_id": self.client_id}


@protect_class
class ComfyUIClient:
    """ComfyUI API client for image generation."""

    def __init__(self, config: Optional[ComfyUIConfig] = None):
        self.config = config or ComfyUIConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.websocket = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.api_timeout)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.websocket:
            await self.websocket.close()
        if self.session:
            await self.session.close()

    async def connect_websocket(self) -> None:
        """Connect to ComfyUI websocket."""
        try:
            ws_url = f"ws://{self.config.comfyui_host}:{self.config.comfyui_port}/ws"
            self.websocket = await websockets.connect(ws_url)
            logger.info("Connected to ComfyUI websocket")
        except Exception as e:
            logger.error(f"Failed to connect to ComfyUI websocket: {e}")
            raise ComfyUIError(f"Websocket connection failed: {e}") from e

    async def check_health(self) -> bool:
        """Check if ComfyUI server is healthy."""
        try:
            async with self.session.get(
                f"{self.config.base_url}/system_stats"
            ) as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"ComfyUI health check failed: {e}")
            return False

    async def get_queue_info(self) -> Dict[str, Any]:
        """Get queue information."""
        try:
            async with self.session.get(f"{self.config.base_url}/queue") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise ComfyUIError(f"Failed to get queue info: {response.status}")
        except Exception as e:
            logger.error(f"Error getting queue info: {e}")
            raise ComfyUIError(f"Queue info request failed: {e}") from e

    async def queue_prompt(self, workflow: ComfyUIWorkflow) -> str:
        """Queue a prompt for generation."""
        try:
            prompt_data = workflow.get_prompt_dict()

            async with self.session.post(
                f"{self.config.base_url}/prompt", json=prompt_data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    prompt_id = result.get("prompt_id")
                    if prompt_id:
                        logger.info(f"Queued prompt with ID: {prompt_id}")
                        return prompt_id
                    else:
                        raise ComfyUIError("No prompt ID returned")
                else:
                    error_text = await response.text()
                    raise ComfyUIError(
                        f"Failed to queue prompt: {response.status} - {error_text}"
                    )
        except Exception as e:
            logger.error(f"Error queuing prompt: {e}")
            raise ComfyUIError(f"Prompt queuing failed: {e}") from e

    async def wait_for_completion(self, prompt_id: str) -> Dict[str, Any]:
        """Wait for prompt completion and return results."""
        if not self.websocket:
            await self.connect_websocket()

        try:
            while True:
                message = await self.websocket.recv()
                data = json.loads(message)

                if data.get("type") == "executing":
                    executing_data = data.get("data", {})
                    if (
                        executing_data.get("node") is None
                        and executing_data.get("prompt_id") == prompt_id
                    ):
                        # Execution completed
                        logger.info(f"Prompt {prompt_id} completed")
                        break

                elif data.get("type") == "execution_error":
                    error_data = data.get("data", {})
                    if error_data.get("prompt_id") == prompt_id:
                        raise ComfyUIError(f"Execution error: {error_data}")

            # Get the generated images
            return await self.get_images(prompt_id)

        except Exception as e:
            logger.error(f"Error waiting for completion: {e}")
            raise ComfyUIError(f"Completion wait failed: {e}") from e

    async def get_images(self, prompt_id: str) -> Dict[str, Any]:
        """Get generated images for a prompt ID."""
        try:
            async with self.session.get(
                f"{self.config.base_url}/history/{prompt_id}"
            ) as response:
                if response.status == 200:
                    history = await response.json()

                    if prompt_id in history:
                        outputs = history[prompt_id].get("outputs", {})
                        images = []

                        for node_output in outputs.values():
                            if "images" in node_output:
                                for image_info in node_output["images"]:
                                    image_url = f"{self.config.base_url}/view"
                                    image_params = {
                                        "filename": image_info["filename"],
                                        "subfolder": image_info.get("subfolder", ""),
                                        "type": image_info.get("type", "output"),
                                    }
                                    images.append(
                                        {
                                            "filename": image_info["filename"],
                                            "url": image_url,
                                            "params": image_params,
                                        }
                                    )

                        return {
                            "prompt_id": prompt_id,
                            "images": images,
                            "status": "completed",
                        }
                    else:
                        raise ComfyUIError(f"Prompt {prompt_id} not found in history")
                else:
                    raise ComfyUIError(f"Failed to get history: {response.status}")
        except Exception as e:
            logger.error(f"Error getting images: {e}")
            raise ComfyUIError(f"Image retrieval failed: {e}") from e


@protect_class
class ComfyUIService:
    """Main ComfyUI service for image generation."""

    def __init__(self, config: Optional[ComfyUIConfig] = None):
        self.config = config or ComfyUIConfig()
        self.default_workflow = self._load_default_workflow()

    def _load_default_workflow(self) -> Dict[str, Any]:
        """Load the default workflow JSON."""
        workflow_path = Path(self.config.default_workflow_path)

        if workflow_path.exists():
            try:
                with open(workflow_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load workflow from {workflow_path}: {e}")

        # Return a basic SDXL workflow if file not found
        return self._get_basic_workflow()

    def _get_basic_workflow(self) -> Dict[str, Any]:
        """Get a basic SDXL workflow."""
        return {
            "3": {
                "inputs": {
                    "seed": 42,
                    "steps": 20,
                    "cfg": 7.0,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0],
                },
                "class_type": "KSampler",
            },
            "4": {
                "inputs": {"ckpt_name": self.config.checkpoint_model},
                "class_type": "CheckpointLoaderSimple",
            },
            "5": {
                "inputs": {"width": 512, "height": 512, "batch_size": 1},
                "class_type": "EmptyLatentImage",
            },
            "6": {
                "inputs": {
                    "text": "beautiful landscape, high quality, detailed",
                    "clip": ["4", 1],
                },
                "class_type": "CLIPTextEncode",
            },
            "7": {
                "inputs": {"text": "low quality, blurry, distorted", "clip": ["4", 1]},
                "class_type": "CLIPTextEncode",
            },
            "8": {
                "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
                "class_type": "VAEDecode",
            },
            "9": {
                "inputs": {"filename_prefix": "rag_generated", "images": ["8", 0]},
                "class_type": "SaveImage",
            },
        }

    async def generate_image(
        self, prompt: str, negative_prompt: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Generate an image based on text prompt."""
        if not self.config.is_enabled:
            raise ComfyUIError("ComfyUI is not enabled")

        try:
            # Create workflow
            workflow = ComfyUIWorkflow(self.default_workflow.copy())
            workflow.update_prompt(prompt)

            if negative_prompt and "7" in workflow.workflow_data:
                workflow.workflow_data["7"]["inputs"]["text"] = negative_prompt

            # Update settings
            config_kwargs = self.config.get_workflow_config()
            config_kwargs.update(kwargs)
            workflow.update_settings(**config_kwargs)

            # Generate image
            async with ComfyUIClient(self.config) as client:
                # Check health
                if not await client.check_health():
                    raise ComfyUIError("ComfyUI server is not healthy")

                # Queue prompt
                prompt_id = await client.queue_prompt(workflow)

                # Wait for completion
                result = await client.wait_for_completion(prompt_id)

                return {
                    "success": True,
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "prompt_id": prompt_id,
                    "images": result.get("images", []),
                    "timestamp": datetime.now().isoformat(),
                    "settings": config_kwargs,
                }

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt,
                "timestamp": datetime.now().isoformat(),
            }

    async def get_status(self) -> Dict[str, Any]:
        """Get ComfyUI service status."""
        if not self.config.is_enabled:
            return {"enabled": False, "status": "disabled"}

        try:
            async with ComfyUIClient(self.config) as client:
                healthy = await client.check_health()
                queue_info = await client.get_queue_info() if healthy else {}

                return {
                    "enabled": True,
                    "healthy": healthy,
                    "base_url": self.config.base_url,
                    "queue_info": queue_info,
                    "default_settings": self.config.get_workflow_config(),
                }
        except Exception as e:
            return {"enabled": True, "healthy": False, "error": str(e)}


# Global instance
comfyui_service = ComfyUIService()
