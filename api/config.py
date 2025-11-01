# api/config.py
from pydantic_settings import BaseSettings

# Módulo que centraliza todas as configurações lidas do .env
class Settings(BaseSettings):
    # caminho do dataset local (CSV)
    DATA_PATH: str = "data/books.csv"
    # URL base para o scraper
    SCRAPER_BASE_URL: str = "https://books.toscrape.com/"
    # nível de logging: DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_LEVEL: str = "INFO"
    # ambiente da aplicação
    ENV: str = "development"
    # porta padrão
    PORT: int = 8000
    # variáveis opcionais para produção (ex.: banco, S3, JWT)
    DATABASE_URL: str | None = None
    S3_BUCKET: str | None = None
    JWT_SECRET: str | None = None

    class Config:
        # arquivo .env
        env_file = ".env"
        env_file_encoding = "utf-8"

# instância global de configurações para ser importada
settings = Settings()