"""
Traefik labels management service
Generates and injects Traefik routing labels into docker-compose.yml
"""

from __future__ import annotations

import yaml
import re
from typing import Optional


class TraefikService:
    """Service for managing Traefik labels and configuration"""

    @staticmethod
    def generate_labels(domain: str, slug: str, internal_port: int = 80) -> list[str]:
        """
        Generate Traefik labels for a project

        Args:
            domain: Project domain (e.g., "example.com")
            slug: Project slug (URL-safe identifier)
            internal_port: Internal container port (default: 80)

        Returns:
            List of Traefik label strings
        """
        # Sanitize slug for Traefik router name (only alphanumeric and hyphens)
        router_name = re.sub(r"[^a-z0-9-]", "-", slug.lower())

        return [
            "traefik.enable=true",
            f"traefik.http.routers.{router_name}.rule=Host(`{domain}`)",
            f"traefik.http.routers.{router_name}.entrypoints=web",
            f"traefik.http.services.{router_name}.loadbalancer.server.port={internal_port}",
        ]

    @staticmethod
    def detect_internal_port(compose_content: str) -> int:
        """
        Detect internal port from docker-compose.yml

        Args:
            compose_content: Docker Compose YAML content

        Returns:
            Internal port number (default: 80)
        """
        try:
            compose_data = yaml.safe_load(compose_content)

            if not compose_data or "services" not in compose_data:
                return 80

            services = compose_data.get("services", {})

            # Get first service
            if not services:
                return 80

            first_service = list(services.values())[0]

            # Check 'expose' section first
            if "expose" in first_service:
                expose = first_service["expose"]
                if expose and len(expose) > 0:
                    port = str(expose[0]).split(":")[-1].split("/")[0]
                    try:
                        return int(port)
                    except ValueError:
                        pass

            # Check 'ports' section
            if "ports" in first_service:
                ports = first_service["ports"]
                if ports and len(ports) > 0:
                    port_mapping = str(ports[0])
                    # Parse "8080:80" or "${PORT}:80" -> extract internal port
                    # (after :)
                    if ":" in port_mapping:
                        internal = port_mapping.split(":")[-1].split("/")[0]
                        try:
                            return int(internal)
                        except ValueError:
                            pass

            # Default to 80
            return 80

        except Exception:
            # If parsing fails, default to 80
            return 80

    @staticmethod
    def inject_labels_to_compose(
        compose_content: str,
        domain: str,
        slug: str,
        force_internal_port: Optional[int] = None,
    ) -> tuple[str, Optional[str]]:
        """
        Inject Traefik labels into docker-compose.yml

        Args:
            compose_content: Original docker-compose.yml content
            domain: Project domain
            slug: Project slug
            force_internal_port: Force specific internal port (optional)

        Returns:
            Tuple of (modified_compose_content, error_message)
        """
        try:
            compose_data = yaml.safe_load(compose_content)

            if not compose_data:
                return compose_content, "Empty compose file"

            if "services" not in compose_data:
                return compose_content, "No services found in compose file"

            services = compose_data["services"]
            if not services:
                return compose_content, "Services section is empty"

            # Detect internal port or use forced value
            if force_internal_port:
                internal_port = force_internal_port
            else:
                internal_port = TraefikService.detect_internal_port(compose_content)

            # Generate labels
            labels = TraefikService.generate_labels(domain, slug, internal_port)

            # Inject labels into first service
            first_service_name = list(services.keys())[0]
            first_service = services[first_service_name]

            # Add labels
            if "labels" not in first_service:
                first_service["labels"] = []

            # Ensure labels is a list
            if not isinstance(first_service["labels"], list):
                first_service["labels"] = []

            # Remove existing Traefik labels
            first_service["labels"] = [
                label
                for label in first_service["labels"]
                if not label.startswith("traefik.")
            ]

            # Add new Traefik labels
            first_service["labels"].extend(labels)

            # Ensure network is added
            if "networks" not in first_service:
                first_service["networks"] = []

            if not isinstance(first_service["networks"], list):
                first_service["networks"] = []

            if "docklite-network" not in first_service["networks"]:
                first_service["networks"].append("docklite-network")

            # Remove 'ports' section to avoid port conflicts (Traefik handles
            # routing)
            if "ports" in first_service:
                # Keep only expose if needed
                if "expose" not in first_service and internal_port:
                    first_service["expose"] = [str(internal_port)]
                del first_service["ports"]

            # Add networks section at root level
            if "networks" not in compose_data:
                compose_data["networks"] = {}

            compose_data["networks"]["docklite-network"] = {"external": True}

            # Convert back to YAML
            modified_yaml = yaml.dump(
                compose_data, default_flow_style=False, sort_keys=False
            )

            return modified_yaml, None

        except yaml.YAMLError as e:
            return compose_content, f"YAML parsing error: {str(e)}"
        except Exception as e:
            return compose_content, f"Error injecting labels: {str(e)}"

    @staticmethod
    def update_labels_in_compose(
        compose_content: str,
        domain: str,
        slug: str,
        internal_port: Optional[int] = None,
    ) -> tuple[str, Optional[str]]:
        """
        Update Traefik labels in existing docker-compose.yml
        (alias for inject_labels_to_compose for consistency)

        Args:
            compose_content: Original docker-compose.yml content
            domain: Project domain
            slug: Project slug
            internal_port: Internal container port (optional)

        Returns:
            Tuple of (modified_compose_content, error_message)
        """
        return TraefikService.inject_labels_to_compose(
            compose_content, domain, slug, internal_port
        )
