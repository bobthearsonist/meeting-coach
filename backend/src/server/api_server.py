"""
REST API server for Meeting Coach configuration and prompt inspection.
Phase 1.5: Transparency and debugging endpoints.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
import time
from pathlib import Path

from src.config import ModelConfig
from src.core import prompts
from src.core.model_factory import ModelProviderFactory

# Create FastAPI app
app = FastAPI(
    title="Meeting Coach API",
    description="Configuration and prompt inspection for Meeting Coach",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state
_model_config = None


def get_config() -> ModelConfig:
    """Get or create ModelConfig instance."""
    global _model_config
    if _model_config is None:
        _model_config = ModelConfig()
    return _model_config


@app.get("/health")
async def health() -> Dict[str, Any]:
    """
    Health check endpoint.
    
    Returns:
        Health status information
    """
    return {
        "status": "ok",
        "mode": "embedded",
        "model_mode": get_config().get_mode(),
        "timestamp": time.time()
    }


@app.get("/api/v1/config")
async def get_configuration() -> Dict[str, Any]:
    """
    Get current model configuration (without sensitive data).
    
    Returns:
        Current configuration settings
    """
    config = get_config()
    
    response = {
        "model_mode": config.get_mode(),
        "config_file": str(config.config_path),
        "analysis": config.get_analysis_config()
    }
    
    # Add mode-specific config
    if config.get_mode() == "self_hosted":
        self_hosted = config.get_self_hosted_config()
        response["self_hosted"] = {
            "endpoint": self_hosted.get("endpoint"),
            "model": self_hosted.get("model"),
            "timeout": self_hosted.get("timeout")
        }
    elif config.get_mode() == "local":
        local = config.get_local_config()
        response["local"] = {
            "model_path": local.get("model_path"),
            "threads": local.get("threads"),
            "context_size": local.get("context_size")
        }
    
    return response


@app.get("/api/v1/prompts")
async def get_all_prompts() -> Dict[str, Any]:
    """
    Get all prompts for transparency.
    Allows users to see exactly what prompts are being sent to models.
    
    Returns:
        All prompt templates and metadata
    """
    return prompts.get_all_prompts()


@app.get("/api/v1/prompts/{prompt_name}")
async def get_prompt(prompt_name: str) -> Dict[str, Any]:
    """
    Get specific prompt template.
    
    Args:
        prompt_name: Name of the prompt (e.g., 'emotion_analysis')
    
    Returns:
        Prompt template and metadata
    
    Raises:
        HTTPException: If prompt not found
    """
    all_prompts = prompts.get_all_prompts()
    
    if prompt_name not in all_prompts["prompts"]:
        raise HTTPException(
            status_code=404,
            detail=f"Prompt '{prompt_name}' not found. Available prompts: {list(all_prompts['prompts'].keys())}"
        )
    
    return all_prompts["prompts"][prompt_name]


@app.get("/api/v1/modes")
async def get_available_modes() -> Dict[str, Any]:
    """
    Get information about available model modes.
    
    Returns:
        Available modes and their status
    """
    return ModelProviderFactory.get_available_modes()


@app.post("/api/v1/reload-config")
async def reload_configuration() -> Dict[str, Any]:
    """
    Reload configuration from file.
    Useful for applying config changes without restarting.
    
    Returns:
        New configuration
    """
    global _model_config
    _model_config = ModelConfig()
    
    return {
        "status": "reloaded",
        "config": await get_configuration()
    }


# Main entry point for running standalone
if __name__ == "__main__":
    import uvicorn
    
    print("Starting Meeting Coach API Server...")
    print("API documentation: http://localhost:3003/docs")
    print("Health check: http://localhost:3003/health")
    
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=3003,
        log_level="info"
    )
