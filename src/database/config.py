from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: str

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @property
    def get_db_url(self) -> str:
        """
        Returns the full database URL for connecting to the PostgreSQL database
        using asyncpg for async operations.
        """
        return "postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}".format(
            user=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            name=self.DB_NAME,
        )

    @property
    def get_db_url_for_alembic(self) -> str:
        """
        Returns the database URL in a format suitable for Alembic migrations
        (does not include asyncpg).
        """
        return "postgresql://{user}:{password}@{host}:{port}/{name}".format(
            user=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            name=self.DB_NAME,
        )

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent / ".env"
    )


settings: Settings = Settings()  # type: ignore
