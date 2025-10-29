from dataclasses import dataclass


@dataclass
class Preset:
    """Template preset for docker-compose projects"""

    id: str
    name: str
    description: str
    category: str
    icon: str
    compose_content: str
    default_env_vars: dict
    tags: list = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
