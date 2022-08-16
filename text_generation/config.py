from pydantic import BaseSettings, Field

from enums import EnvEnum


class AppSettings(BaseSettings):
    app_name: str = Field("Text Generation API Server", description="FastAPI App Name")
    app_version: str = Field("0.1.0", description="FastAPI App Version")
    app_env: EnvEnum = Field(EnvEnum.DEV, description="FastAPI App Environment")
    app_max_queue_size: int = Field(3, description="Number of tasks that can be processed at the same time")
    app_max_retry: int = Field(10, description="Maximum number of retries")


class ModelSettings(BaseSettings):
    model_path: str = "gpt2"
    use_fast_tokenizer: bool = True
    model_max_length: int = 1024


app_settings = AppSettings()
model_settings = ModelSettings()
