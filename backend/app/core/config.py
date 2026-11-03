from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    secret_key: str = "dev-only-change-me"
    access_token_expire_minutes: int = 1440
    database_url: str = "sqlite:///./helpmate2.db"
    device_ingest_key: str = "dev-device-key"
    frontend_origin: str = "http://localhost:5173"
    upload_dir: str = "uploads"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
