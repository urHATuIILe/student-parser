from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    
    DATABASE_URL: str
    BOT_TOKEN: str
    TELEGRAM_API_ID: int
    TELEGRAM_API_HASH: str
    CHANNEL_ID: str
    CHATS_TO_MONITOR: str = ""

    # ===== VK =====
    VK_TOKEN: str = ""
    VK_GROUPS: str = ""
    VK_POLLING_INTERVAL: int = 300
    VK_POSTS_PER_POLL: int = 30
    VK_COMMENTS_PER_POST: int = 100
    VK_POSTS_FOR_COMMENTS: int = 10

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

    @property
    def vk_groups_list(self) -> list:
        result = []
        for g in self.VK_GROUPS.split(","):
            g = g.strip()
            if g:
                try:
                    result.append(int(g))
                except ValueError:
                    result.append(g)
        return result
    
    
    
    
settings = Settings()

