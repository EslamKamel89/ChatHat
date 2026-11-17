from typing import Literal, Self

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CHATHAT_",
        # prevents Pydantic from automatically loading a .env file. Compose supplies the container environment explicitly
        env_file=None,
        frozen=True,
        hide_input_in_errors=True,
    )
    environment: Literal["development", "test", "production"]
    debug: bool = False
    """
    print(secret)                # **********
    secret.get_secret_value()    # "my-secret"
    """
    secret_key: SecretStr | None = Field(default=None, exclude=True)

    @model_validator(mode="after")
    def check_environment(self) -> Self:
        if self.environment == "production":
            if self.debug:
                raise ValueError("Production must disable debug mode")

            if self.secret_key is None:
                raise ValueError("Production requires CHATHAT_SECRET_KEY")

            if len(self.secret_key.get_secret_value()) < 32:
                raise ValueError(
                    "Production requires a secret key of at least 32 characters"
                )
        return self
