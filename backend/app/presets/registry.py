from typing import List, Optional
from .web import WEB_PRESETS
from .backend import BACKEND_PRESETS
from .databases import DATABASE_PRESETS
from .cms import CMS_PRESETS
from .examples import EXAMPLES_PRESETS
from . import Preset

# All presets registry
ALL_PRESETS: List[Preset] = [
    *WEB_PRESETS,
    *BACKEND_PRESETS,
    *DATABASE_PRESETS,
    *CMS_PRESETS,
    *EXAMPLES_PRESETS,
]

# Presets by category
PRESETS_BY_CATEGORY = {
    "web": WEB_PRESETS,
    "backend": BACKEND_PRESETS,
    "database": DATABASE_PRESETS,
    "cms": CMS_PRESETS,
    "examples": EXAMPLES_PRESETS,
}


def get_all_presets() -> List[dict]:
    """Get all available presets"""
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "category": p.category,
            "icon": p.icon,
            "tags": p.tags,
        }
        for p in ALL_PRESETS
    ]


def get_preset_by_id(preset_id: str) -> Optional[Preset]:
    """Get preset by ID"""
    for preset in ALL_PRESETS:
        if preset.id == preset_id:
            return preset
    return None


def get_presets_by_category(category: str) -> List[dict]:
    """Get presets by category"""
    presets = PRESETS_BY_CATEGORY.get(category, [])
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "category": p.category,
            "icon": p.icon,
            "tags": p.tags,
        }
        for p in presets
    ]


def get_categories() -> List[dict]:
    """Get all categories with counts"""
    return [
        {"id": "all", "name": "All", "count": len(ALL_PRESETS)},
        {"id": "web", "name": "Web", "count": len(WEB_PRESETS)},
        {"id": "backend", "name": "Backend", "count": len(BACKEND_PRESETS)},
        {"id": "database", "name": "Database", "count": len(DATABASE_PRESETS)},
        {"id": "cms", "name": "CMS", "count": len(CMS_PRESETS)},
        {"id": "examples", "name": "Examples", "count": len(EXAMPLES_PRESETS)},
    ]
