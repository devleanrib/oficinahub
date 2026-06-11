import logging
import time
from openai import OpenAI
from openai import RateLimitError, APIError, APITimeoutError, AuthenticationError

from config import AppConfig

logger = logging.getLogger(__name__)


class AIClient:
    def __init__(self, config: AppConfig):
        self.config = config
        self.client = self._build_client()
        logger.info("AIClient inicializado - Modelo: %s | Base URL: %s", config.openai_model, config.openai_base_url)

    def _build_client(self) -> OpenAI:
        return OpenAI(
            api_key=self.config.openai_api_key,
            base_url=self.config.openai_base_url,
            timeout=self.config.openai_timeout,
        )

    def generate(self, prompt: str) -> str:
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                logger.debug("Tentativa %d/%d - Enviando prompt para IA", attempt + 1, self.config.max_retries)
                response = self.client.chat.completions.create(
                    model=self.config.openai_model,
                    messages=[
                        {"role": "system", "content": self._get_system_prompt()},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=self.config.openai_temperature,
                    max_tokens=self.config.openai_max_tokens,
                    response_format={"type": "json_object"},
                )
                content = response.choices[0].message.content
                logger.debug("Resposta recebida: %d caracteres", len(content))
                return content

            except RateLimitError as e:
                last_error = e
                wait_time = self.config.backoff_factor ** attempt
                logger.warning("Rate limit atingido. Aguardando %.1fs antes de retry...", wait_time)
                time.sleep(wait_time)

            except APITimeoutError as e:
                last_error = e
                wait_time = self.config.backoff_factor ** attempt
                logger.warning("Timeout na API. Aguardando %.1fs antes de retry...", wait_time)
                time.sleep(wait_time)

            except APIError as e:
                last_error = e
                logger.error("Erro na API OpenAI: %s", e)
                if attempt == self.config.max_retries - 1:
                    break
                time.sleep(self.config.backoff_factor ** attempt)

            except AuthenticationError as e:
                logger.error("Erro de autenticação: Verifique sua OPENAI_API_KEY")
                raise RuntimeError("Falha de autenticação com a API OpenAI") from e

            except Exception as e:
                last_error = e
                logger.exception("Erro inesperado ao chamar IA")
                if attempt == self.config.max_retries - 1:
                    break
                time.sleep(self.config.backoff_factor ** attempt)

        raise RuntimeError(f"Falha apos {self.config.max_retries} tentativas: {last_error}")

    def _get_system_prompt(self) -> str:
        from prompts import SYSTEM_PROMPT
        return SYSTEM_PROMPT