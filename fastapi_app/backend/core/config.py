from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

class RunConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000

class ApiPrefix(BaseModel):
    prefix: str = "/api"

class DatabaseConfig(BaseModel):

    database: str 
    user: str
    password: str 
    name: str 
    domen_name: str 
    port: int 
    echo: bool = False
    echo_pool: bool = False 
    pool_size: int = 50
    max_overflow: int = 10
    def get_url(cls):
        url: PostgresDsn = f"{
            cls.database}://{cls.user}:{cls.password}@{
                cls.domen_name}:{cls.port}/{cls.name}" 
        return url

    

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file =("fastapi_app/backend/.env.template","fastapi_app/backend/.env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
    )
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig 


settings = Settings()


