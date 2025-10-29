from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any
from app.presets.registry import (
    get_all_presets,
    get_preset_by_id,
    get_presets_by_category,
    get_categories,
)

router = APIRouter(prefix="/presets", tags=["presets"])


@router.get("", response_model=List[Dict[str, Any]])
async def list_presets(category: str = None):
    """Get all presets or filter by category"""
    if category and category != "all":
        return get_presets_by_category(category)
    return get_all_presets()


@router.get("/categories", response_model=List[Dict[str, Any]])
async def list_categories():
    """Get all available categories"""
    return get_categories()


@router.get("/{preset_id}")
async def get_preset(preset_id: str):
    """Get preset details including compose content and env vars"""
    preset = get_preset_by_id(preset_id)

    if not preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preset '{preset_id}' not found",
        )

    return {
        "id": preset.id,
        "name": preset.name,
        "description": preset.description,
        "category": preset.category,
        "icon": preset.icon,
        "compose_content": preset.compose_content,
        "default_env_vars": preset.default_env_vars,
        "tags": preset.tags,
    }
