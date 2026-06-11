import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AppConfig:
    openai_api_key: str
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.1
    openai_max_tokens: int = 3000
    openai_timeout: int = 60
    max_retries: int = 3
    backoff_factor: float = 1.5
    log_level: str = "DEBUG"
    output_dir: str = "output"
    input_dir: str = "input"


def load_config() -> AppConfig:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY nao encontrada. Configure a variavel de ambiente ou crie um arquivo .env"
        )

    return AppConfig(
        openai_api_key=api_key,
        openai_base_url=os.getenv("BASE_URL", "https://api.openai.com/v1"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4"),
        openai_temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.1")),
        openai_max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "3000")),
        openai_timeout=int(os.getenv("OPENAI_TIMEOUT", "60")),
        max_retries=int(os.getenv("MAX_RETRIES", "3")),
        backoff_factor=float(os.getenv("BACKOFF_FACTOR", "1.5")),
        log_level=os.getenv("LOG_LEVEL", "DEBUG"),
        output_dir=os.getenv("OUTPUT_DIR", "output"),
        input_dir=os.getenv("INPUT_DIR", "input"),
    )