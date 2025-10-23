from pathlib import Path

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="XERXES_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    vertex_project_id: str | None = Field(default=None)
    vertex_location: str = Field(default="us-central1")
    vertex_model: str = Field(default="gemini-2.0-flash-exp")
    google_application_credentials: str | None = Field(default=None)

    max_tokens: int = Field(default=3000)
    temperature: float = Field(default=0.4)

    auto_execute_readonly: bool = Field(default=True)
    confirm_destructive: bool = Field(default=True)

    @classmethod
    def get_config_dir(cls) -> Path:
        config_dir = Path.home() / ".xerxes"
        config_dir.mkdir(exist_ok=True)
        return config_dir

    @classmethod
    def get_config_file(cls) -> Path:
        return cls.get_config_dir() / "config.yaml"

    @classmethod
    def load_from_file(cls) -> "Settings":
        config_file = cls.get_config_file()

        if config_file.exists():
            with open(config_file, "r") as f:
                config_data = yaml.safe_load(f) or {}
        else:
            config_data = {}

        return cls(**config_data)

    def save_to_file(self) -> None:
        config_file = self.get_config_file()
        config_data = self.model_dump(exclude_none=True)

        with open(config_file, "w") as f:
            yaml.dump(config_data, f, default_flow_style=False)

        config_file.chmod(0o600)

    def update_setting(self, key: str, value: str) -> None:
        field_info = self.model_fields.get(key)
        if not field_info:
            raise ValueError(f"Unknown setting: {key}")

        field_type = field_info.annotation
        if field_type == bool:
            converted_value = value.lower() in ("true", "yes", "1", "on")
        elif field_type == int:
            converted_value = int(value)
        elif field_type == float:
            converted_value = float(value)
        else:
            converted_value = value

        setattr(self, key, converted_value)
        self.save_to_file()


def get_settings() -> Settings:
    return Settings.load_from_file()
