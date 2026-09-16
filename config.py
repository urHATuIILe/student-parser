from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    
    DATABASE_URL: str
    BOT_TOKEN: str
    TELEGRAM_API_ID: int
    TELEGRAM_API_HASH: str
    CHANNEL_ID: str

    # ===== VK =====
    VK_TOKEN: str = ""
    VK_POLLING_INTERVAL: int = 300
    VK_POSTS_PER_POLL: int = 30
    VK_COMMENTS_PER_POST: int = 100
    VK_POSTS_FOR_COMMENTS: int = 10


settings = Settings()

