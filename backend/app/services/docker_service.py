"""Docker service for managing containers."""

from __future__ import annotations

import subprocess
import json
from typing import Optional


class DockerService:
    """Service for interacting with Docker via CLI."""

    def __init__(self) -> None:
        """Initialize Docker service."""
        # Test Docker is available
        try:
            subprocess.run(
                ["docker", "version"], capture_output=True, check=True, timeout=5
            )
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ) as e:
            raise Exception(f"Docker is not available: {str(e)}")

    def list_all_containers(self, all: bool = True) -> list[dict]:
        """
        List all Docker containers.

        Args:
            all: If True, show all containers (default). If False, show only running.

        Returns:
            List of container dictionaries
        """
        try:
            cmd = ["docker", "ps", "--format", "{{json .}}"]
            if all:
                cmd.append("--all")

            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, timeout=10
            )

            containers = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    container_data = json.loads(line)
                    containers.append(self._format_container(container_data))

            return containers
        except subprocess.CalledProcessError as e:
            raise Exception(f"Failed to list containers: {e.stderr}")
        except Exception as e:
            raise Exception(f"Failed to list containers: {str(e)}")

    def get_container(self, container_id: str) -> Optional[dict]:
        """
        Get a specific container by ID or name.

        Args:
            container_id: Container ID or name

        Returns:
            Container dictionary or None if not found
        """
        try:
            cmd = ["docker", "inspect", container_id]
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, timeout=10
            )

            data = json.loads(result.stdout)
            if data:
                return self._format_inspect_data(data[0])
            return None
        except subprocess.CalledProcessError:
            return None
        except Exception as e:
            raise Exception(f"Failed to get container: {str(e)}")

    def start_container(self, container_id: str) -> tuple[bool, Optional[str]]:
        """
        Start a container.

        Args:
            container_id: Container ID or name

        Returns:
            Tuple of (success, error_message)
        """
        try:
            subprocess.run(
                ["docker", "start", container_id],
                capture_output=True,
                text=True,
                check=True,
                timeout=30,
            )
            return True, None
        except subprocess.CalledProcessError as e:
            return (
                False,
                (e.stderr.strip() if e.stderr else None)
                or f"Failed to start container '{container_id}'",
            )
        except Exception as e:
            return False, f"Docker error: {str(e)}"

    def stop_container(
        self, container_id: str, timeout: int = 10
    ) -> tuple[bool, Optional[str]]:
        """
        Stop a container.

        Args:
            container_id: Container ID or name
            timeout: Seconds to wait before killing

        Returns:
            Tuple of (success, error_message)
        """
        try:
            subprocess.run(
                ["docker", "stop", "-t", str(timeout), container_id],
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout + 10,
            )
            return True, None
        except subprocess.CalledProcessError as e:
            return (
                False,
                (e.stderr.strip() if e.stderr else None)
                or f"Failed to stop container '{container_id}'",
            )
        except Exception as e:
            return False, f"Docker error: {str(e)}"

    def restart_container(
        self, container_id: str, timeout: int = 10
    ) -> tuple[bool, Optional[str]]:
        """
        Restart a container.

        Args:
            container_id: Container ID or name
            timeout: Seconds to wait before killing

        Returns:
            Tuple of (success, error_message)
        """
        try:
            subprocess.run(
                ["docker", "restart", "-t", str(timeout), container_id],
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout + 10,
            )
            return True, None
        except subprocess.CalledProcessError as e:
            return (
                False,
                (e.stderr.strip() if e.stderr else None)
                or f"Failed to restart container '{container_id}'",
            )
        except Exception as e:
            return False, f"Docker error: {str(e)}"

    def remove_container(
        self, container_id: str, force: bool = False
    ) -> tuple[bool, Optional[str]]:
        """
        Remove a container.

        Args:
            container_id: Container ID or name
            force: Force remove even if running

        Returns:
            Tuple of (success, error_message)
        """
        try:
            cmd = ["docker", "rm", container_id]
            if force:
                cmd.insert(2, "-f")

            subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
            return True, None
        except subprocess.CalledProcessError as e:
            return (
                False,
                (e.stderr.strip() if e.stderr else None)
                or f"Failed to remove container '{container_id}'",
            )
        except Exception as e:
            return False, f"Docker error: {str(e)}"

    def get_container_logs(
        self, container_id: str, tail: int = 100, timestamps: bool = True
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Get container logs.

        Args:
            container_id: Container ID or name
            tail: Number of lines from the end (default 100)
            timestamps: Include timestamps

        Returns:
            Tuple of (logs, error_message)
        """
        try:
            cmd = ["docker", "logs", "--tail", str(tail)]
            if timestamps:
                cmd.append("--timestamps")
            cmd.append(container_id)

            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, timeout=30
            )
            return result.stdout + result.stderr, None
        except subprocess.CalledProcessError as e:
            return (
                None,
                (e.stderr.strip() if e.stderr else None)
                or f"Failed to get logs for '{container_id}'",
            )
        except Exception as e:
            return None, f"Docker error: {str(e)}"

    def get_container_stats(
        self, container_id: str
    ) -> tuple[Optional[dict], Optional[str]]:
        """
        Get container resource usage statistics.

        Args:
            container_id: Container ID or name

        Returns:
            Tuple of (stats_dict, error_message)
        """
        try:
            # Get stats in JSON format (no-stream for single snapshot)
            cmd = [
                "docker",
                "stats",
                "--no-stream",
                "--format",
                "{{json .}}",
                container_id,
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, timeout=10
            )

            if result.stdout.strip():
                stats_data = json.loads(result.stdout.strip())

                # Parse CPU percentage (remove %)
                cpu_str = stats_data.get("CPUPerc", "0%").rstrip("%")
                cpu_percent = float(cpu_str) if cpu_str else 0.0

                # Parse memory (format: "100MiB / 2GiB")
                mem_usage_str = stats_data.get("MemUsage", "0B / 0B")
                mem_perc_str = stats_data.get("MemPerc", "0%").rstrip("%")
                mem_percent = float(mem_perc_str) if mem_perc_str else 0.0

                # Parse network I/O (format: "1.5kB / 2kB")
                net_io = stats_data.get("NetIO", "0B / 0B")

                return {
                    "cpu_percent": round(cpu_percent, 2),
                    "memory_usage": mem_usage_str.split(" / ")[0],
                    "memory_limit": (
                        mem_usage_str.split(" / ")[1]
                        if " / " in mem_usage_str
                        else "0B"
                    ),
                    "memory_percent": round(mem_percent, 2),
                    "network_io": net_io,
                }, None

            return None, "No stats available"
        except subprocess.CalledProcessError as e:
            return (
                None,
                (e.stderr.strip() if e.stderr else None)
                or f"Failed to get stats for '{container_id}'",
            )
        except Exception as e:
            return None, f"Docker error: {str(e)}"

    def _format_container(self, data: dict) -> dict:
        """
        Format docker ps JSON output to our format.

        Args:
            data: Docker ps JSON output

        Returns:
            Formatted container dictionary
        """
        # Extract info from docker ps format
        name = data.get("Names", "")
        image = data.get("Image", "")
        status = data.get("Status", "").lower()
        ports = data.get("Ports", "")

        # Determine state from status
        state = "running" if "up" in status else "exited"

        # Parse project from name (docker-compose naming:
        # project_service_number)
        project = ""
        service = ""
        is_system = name.startswith("docklite-")

        if "_" in name and not is_system:
            parts = name.split("_")
            if len(parts) >= 2:
                project = parts[0]
                service = parts[1]

        # Format ports list
        ports_list = []
        if ports:
            ports_list = [p.strip() for p in ports.split(",") if p.strip()]

        return {
            "id": data.get("ID", "")[:12],
            "name": name,
            "image": image,
            "status": state,
            "state": state,
            "created": data.get("CreatedAt", ""),
            "started": "",  # Not available in ps output
            "ports": ports_list,
            "project": project,
            "service": service,
            "is_system": is_system,
            "labels": {},
        }

    def _format_inspect_data(self, data: dict) -> dict:
        """
        Format docker inspect JSON output to our format.

        Args:
            data: Docker inspect JSON output

        Returns:
            Formatted container dictionary
        """
        config = data.get("Config", {})
        state = data.get("State", {})
        network_settings = data.get("NetworkSettings", {})
        labels = config.get("Labels", {})

        name = data.get("Name", "").lstrip("/")
        project = labels.get("com.docker.compose.project", "")
        service = labels.get("com.docker.compose.service", "")
        is_system = name.startswith("docklite-")

        # Format ports
        ports = []
        port_bindings = network_settings.get("Ports", {})
        if port_bindings:
            for container_port, host_bindings in port_bindings.items():
                if host_bindings:
                    for binding in host_bindings:
                        host_ip = binding.get("HostIp", "0.0.0.0")
                        host_port = binding.get("HostPort", "")
                        ports.append(f"{host_ip}:{host_port}->{container_port}")
                else:
                    ports.append(container_port)

        return {
            "id": data.get("Id", "")[:12],
            "name": name,
            "image": config.get("Image", ""),
            "status": state.get("Status", ""),
            "state": state.get("Status", ""),
            "created": data.get("Created", ""),
            "started": state.get("StartedAt", ""),
            "ports": ports,
            "project": project,
            "service": service,
            "is_system": is_system,
            "labels": labels,
        }
