from pathlib import Path
from . import Preset

EXAMPLES_DIR = Path(__file__).parent / "examples"


def load_example_preset(
    example_id: str, name: str, description: str, icon: str, tags: list
) -> Preset:
    """Load preset from example directory."""
    example_path = EXAMPLES_DIR / example_id
    compose_file = example_path / "docker-compose.yml"

    return Preset(
        id=example_id,
        name=name,
        description=description,
        category="examples",
        icon=icon,
        compose_content=compose_file.read_text(),
        default_env_vars={},
        tags=tags,
    )


FLASK_HELLO = load_example_preset(
    "flask-hello",
    "Flask Hello World",
    "Working Flask REST API (single service)",
    "🔴",
    ["flask", "python", "api", "example"],
)

FASTAPI_HELLO = load_example_preset(
    "fastapi-hello",
    "FastAPI Hello World",
    "Working FastAPI with auto docs (single service)",
    "⚡",
    ["fastapi", "python", "api", "example"],
)

EXPRESS_HELLO = load_example_preset(
    "express-hello",
    "Express Hello World",
    "Working Express REST API (single service)",
    "🟢",
    ["express", "nodejs", "api", "example"],
)

FULLSTACK_HELLO = load_example_preset(
    "fullstack-hello",
    "Full Stack Hello World",
    "Frontend (Nginx) + Backend (Flask) with API routing",
    "🎯",
    ["fullstack", "nginx", "flask", "multi-service", "example"],
)

EXAMPLES_PRESETS = [FLASK_HELLO, FASTAPI_HELLO, EXPRESS_HELLO, FULLSTACK_HELLO]
