from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/bookleaf"
    jwt_secret: str = "dev-secret-change-me"
    jwt_expire_minutes: int = 480

    gemini_api_key: str = ""
    ai_model: str = "gemini-3.8-flash"
    ai_timeout_seconds: float = 15.0
    max_ticket_chars_for_ai: int = 2000  # cost control, cut very long tickets

    cors_origins: str = "http://localhost:3000"
    max_tickets_per_hour: int = 10  # per author


settings = Settings()