import logging
import os
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr, ValidationError

from chathat.core.application.state import AppState, get_app_state
from chathat.core.dependencies.state import AppStateDependency, provide_app_state
from chathat.core.settings.config import Config
from chathat.main import create_app


# autouse runs the fixture automatically before every test in that file, clearing inherited CHATHAT_* variables so each test starts with isolated inputs
@pytest.fixture(autouse=True)
def isolate_config_environment(monkeypatch: pytest.MonkeyPatch):
    for name in tuple(os.environ):
        if name.upper().startswith("CHATHAT_"):
            monkeypatch.delenv(name)


def test_constructor_overrides_environment_and_environment_overrides_defaults(
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setenv("CHATHAT_ENVIRONMENT", "development")
    monkeypatch.setenv("CHATHAT_DEBUG", "true")
    from_environment = Config()  # type: ignore
    explicit = Config(environment="test", debug=False)

    assert from_environment.environment == "development"
    assert from_environment.debug is True
    assert explicit.environment == "test"
    assert explicit.debug is False
    monkeypatch.delenv("CHATHAT_DEBUG")
    assert Config().debug is False  # type: ignore


def test_dotenv_is_not_loaded_implicitly(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    (tmp_path / ".env").write_text(
        "CHATHAT_ENVIRONMENT=production\nCHATHAT_DEBUG=true\n"
    )
    monkeypatch.chdir(tmp_path)

    config = Config(environment="test")

    assert config.environment == "test"
    assert config.debug is False


@pytest.mark.parametrize(
    ("environment", "debug", "error_type", "location"),
    [
        (None, None, "missing", ("environment",)),
        ("staging", None, "literal_error", ("environment",)),
        ("test", "not-a-boolean", "bool_parsing", ("debug",)),
    ],
)
def test_invalid_configuration_prevents_app_creation(
    monkeypatch: pytest.MonkeyPatch,
    environment: str | None,
    debug: str | None,
    error_type: str,
    location: tuple[str, ...],
) -> None:
    if environment is not None:
        monkeypatch.setenv("CHATHAT_ENVIRONMENT", environment)
    if debug is not None:
        monkeypatch.setenv("CHATHAT_DEBUG", debug)

    with pytest.raises(ValidationError) as caught:
        create_app()

    errors = caught.value.errors(include_input=False)
    assert any(
        error["type"] == error_type and error["loc"] == location for error in errors
    )


@pytest.mark.parametrize(
    ("debug", "secret", "message"),
    [
        (True, "x" * 32, "Production must disable debug mode"),
        (False, None, "Production requires CHATHAT_SECRET_KEY"),
        (False, "x" * 31, "at least 32 characters"),
    ],
)
def test_production_rejects_unsafe_configuration(
    debug: bool,
    secret: str | None,
    message: str,
) -> None:
    with pytest.raises(ValidationError, match=message):
        Config(
            environment="production",
            debug=debug,
            secret_key=SecretStr(secret) if secret is not None else None,
        )


def test_production_accepts_minimum_secret_length() -> None:
    config = Config(
        environment="production",
        debug=False,
        secret_key=SecretStr("x" * 32),
    )
    app = create_app(config=config)

    assert app.debug is False
    assert get_app_state(app).config is config


@pytest.mark.parametrize("environment", ["development", "test"])
def test_nonproduction_does_not_require_a_secret(environment: str) -> None:
    config = Config(environment=environment)  # type: ignore

    assert config.secret_key is None
    assert config.debug is False


def test_secret_is_masked_in_logs_and_excluded_from_serialization(
    caplog: pytest.LogCaptureFixture,
) -> None:
    marker = "synthetic-private-value-" + "x" * 32
    config = Config(environment="test", secret_key=SecretStr(marker))

    with caplog.at_level(logging.INFO, logger="chathat.tests.config"):
        logging.getLogger("chathat.tests.config").info("Configuration: %r", config)

    assert config.secret_key is not None
    assert config.secret_key.get_secret_value() == marker
    assert str(config.secret_key) == "**********"
    assert marker not in repr(config)
    assert marker not in caplog.text
    assert "secret_key" not in config.model_dump()
    assert "secret_key" not in config.model_dump_json()


def test_validation_error_string_does_not_log_secret_input(
    caplog: pytest.LogCaptureFixture,
) -> None:
    marker = "synthetic-sensitive-input"

    with pytest.raises(ValidationError) as caught:
        Config(
            environment="production",
            debug=False,
            secret_key=SecretStr(marker),
        )

    with caplog.at_level(logging.ERROR, logger="chathat.tests.config"):
        logging.getLogger("chathat.tests.config").error(
            "Invalid configuration: %s", caught.value
        )

    assert "at least 32 characters" in caplog.text
    assert marker not in str(caught.value)
    assert marker not in caplog.text


def test_factory_snapshots_configuration_per_application(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHATHAT_ENVIRONMENT", "test")
    monkeypatch.setenv("CHATHAT_DEBUG", "false")
    first = create_app()

    monkeypatch.setenv("CHATHAT_DEBUG", "true")
    second = create_app()

    assert get_app_state(first).config.debug is False
    assert get_app_state(second).config.debug is True
    assert first.debug is False
    assert second.debug is True
    assert get_app_state(first) is not get_app_state(second)


def test_configuration_cannot_be_reassigned() -> None:
    config = Config(environment="test")

    with pytest.raises(ValidationError) as caught:
        config.debug = True

    assert caught.value.errors(include_input=False)[0]["type"] == ("frozen_instance")
    assert config.debug is False


def test_dependency_override_is_local_and_restorable() -> None:
    def build_app() -> FastAPI:
        app = create_app(config=Config(environment="test"))

        @app.get("/_test/environment")
        def read_environment(state: AppStateDependency) -> dict[str, str]:
            return {"environment": state.config.environment}

        return app

    first = build_app()
    second = build_app()
    replacement = AppState(config=Config(environment="development"))

    def override_state() -> AppState:
        return replacement

    first.dependency_overrides[provide_app_state] = override_state

    try:
        with TestClient(first) as first_client, TestClient(second) as second_client:
            assert first_client.get("/_test/environment").json() == {
                "environment": "development"
            }
            assert second_client.get("/_test/environment").json() == {
                "environment": "test"
            }

            first.dependency_overrides.clear()

            assert first_client.get("/_test/environment").json() == {
                "environment": "test"
            }

            assert get_app_state(first).config.environment == "test"
    finally:
        first.dependency_overrides.clear()


def test_public_responses_and_request_logs_do_not_expose_configuration(
    caplog: pytest.LogCaptureFixture,
) -> None:
    marker = "synthetic-private-value-" + "y" * 32
    app = create_app(config=Config(environment="test", secret_key=SecretStr(marker)))

    with caplog.at_level(logging.INFO):
        with TestClient(app) as client:
            for path, expected_status in [
                ("/health", 200),
                ("/openapi.json", 200),
                ("/missing", 404),
            ]:
                response = client.get(path)

                assert response.status_code == expected_status
                assert marker not in response.text
                assert "secret_key" not in response.text
                assert marker not in repr(dict(response.headers))

    assert marker not in caplog.text
