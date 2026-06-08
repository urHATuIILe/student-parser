from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    
    DATABASE_URL: str
    BOT_TOKEN: str
    TELEGRAM_API_ID: int
    TELEGRAM_API_HASH: str
    CHANNEL_ID: str
    CHATS_TO_MONITOR: str = ""
    
    @property
    def chats_list(self) -> list:
        result = []
        for c in self.CHATS_TO_MONITOR.split(","):
            c = c.strip()
            if c:
                try:
                    result.append(int(c))
                except ValueError:
                    result.append(c)
        return result
    
    
    
    
settings = Settings()

