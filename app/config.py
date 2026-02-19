from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    APP_NAME: str = "Universal Data Connector"
    MAX_RESULTS: int = 10
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 50
    HUGGINGFACE_API_KEY: str | None = None


settings = Settings()
