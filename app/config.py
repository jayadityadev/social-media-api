from pydantic_settings import BaseSettings, SettingsConfigDict

# postgresql://<username>:<password>@<ip-addr (or) hostname>:<port>/<dbname>

class Settings(BaseSettings):
    db_username: str
    db_password: str
    db_hostname: str
    db_port: str
    db_name: str

    jwt_secret_key: str
    jwt_algorithm: str
    jwt_expire_time: int


    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()

db_url = f"postgresql+psycopg://{settings.db_username}:{settings.db_password}@{settings.db_hostname}:{settings.db_port}/{settings.db_name}"
