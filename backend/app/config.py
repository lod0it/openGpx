from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    graphhopper_url: str = "http://localhost:8989"

    model_config = {"env_file": ".env"}


settings = Settings()
