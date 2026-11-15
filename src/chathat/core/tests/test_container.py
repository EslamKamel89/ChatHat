import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.request import urlopen

import pytest
import yaml


@pytest.fixture
def compose_files() -> tuple[dict, dict]:
    project_root = Path("/app")
    base = yaml.safe_load((project_root / "compose.yaml").read_text())
    development = yaml.safe_load((project_root / "compose.dev.yaml").read_text())
    return base, development


def test_development_compose_contract(compose_files: tuple[dict, dict]) -> None:
    base, development = compose_files
    api = base["services"]["api"]
    dev_api = development["services"]["api"]

    assert api["build"]["dockerfile"] == "dockerfiles/Dockerfile.api"
    assert api["init"] is True

    command = dev_api["command"]
    assert command[:2] == ["uvicorn", "chathat.main:create_app"]
    assert "--factory" in command
    assert "--reload" in command

    assert dev_api["ports"] == ["127.0.0.1:${CHATHAT_DEV_PORT:-8000}:8000"]
    assert dev_api["volumes"] == ["./src:/app/src:ro"]

    health_command = api["healthcheck"]["test"]
    assert health_command[:3] == ["CMD", "python", "-c"]
    assert "/health" in health_command[3]


def test_running_api_health() -> None:
    with urlopen("http://127.0.0.1:8000/health", timeout=5) as response:
        assert response.status == 200
        assert response.headers.get_content_type() == "application/json"
        assert json.load(response) == {"status": "ok"}


def test_container_environment() -> None:
    assert os.getuid() != 0
    assert Path(sys.prefix) == Path("/app/.venv")

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import fastapi, pydantic, uvicorn, pytest, yaml; "
                "from chathat.main import create_app; "
                "assert callable(create_app)"
            ),
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
