# api/config.py
"""
Carrega variáveis de ambiente da aplicação.
Usa pydantic-settings (compatível com Pydantic v2).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- Caminhos e configurações gerais ---
    DATA_PATH: str = "data/books.csv"
    SCRAPER_BASE_URL: str = "https://books.toscrape.com/"
    LOG_LEVEL: str = "INFO"
    ENV: str = "development"
    PORT: int = 8000

    # --- Credenciais administrativas ---
    ADMIN_USER: str = "admin"
    ADMIN_PASSWORD: str = "admin123"

    # --- JWT (Tokens) ---
    JWT_SECRET: str = "changeme"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # <-- ignora variáveis extras no .env (importante!)
    )

# Instância global de configurações
settings = Settings()
