from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://faceuser:facepass@localhost:5432/facedetect"
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost"
    MAX_QUEUE_SIZE: int = 2
    JPEG_QUALITY: int = 82
    DETECTION_CONFIDENCE_THRESHOLD: float = 0.6
    MAX_FRAME_BYTES: int = 2 * 1024 * 1024  # 2 MB
    STREAM_TIMEOUT_SECONDS: float = 30.0
    MAX_FPS_PER_SESSION: int = 30

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.BACKEND_CORS_ORIGINS.split(",") if o.strip()]


settings = Settings()
