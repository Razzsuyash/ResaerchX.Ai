from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Deep Research Agent API"
    app_version: str = "2.0.0"
    environment: str = "development"

    #ollama_model: str = "llama3:latest"
    openrouter_api_key: str
    openrouter_model: str = "google/gemini-3.1-flash-lite"
    #gemini_api_key: str
    #gemini_model: str = "gemini-3.7-flash"
    tavily_api_key: str
    

    database_url: str = "sqlite:///./research.db"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    max_research_iterations: int = 2
    max_sub_questions: int = 5
    max_search_results: int = 5
    max_sources_for_synthesis: int = 30
    max_content_chars: int = 2500
    graph_recursion_limit: int = 50

    allowed_origins: str = "http://localhost:8501"
    rate_limit_research: str = "10/minute"
    rate_limit_auth: str = "5/minute"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [x.strip() for x in self.allowed_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
