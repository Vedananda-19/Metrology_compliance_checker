import logging
import time
from config import (
    LLM_ENABLED,
    LLM_PROVIDER,
    LLM_API_KEY,
    LLM_MODEL,
    LLM_BASE_URL,
    EMBEDDING_MODEL,
)

logger = logging.getLogger(__name__)

_models = {}
_embeddings = None


def available() -> bool:
    return LLM_ENABLED


def build_model(provider: str, api_key: str, model: str, temperature: float):
    if provider == "google":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(model=model, google_api_key=api_key, temperature=temperature)
    if provider in ("openai", "openrouter"):
        from langchain_openai import ChatOpenAI

        base_url = LLM_BASE_URL if provider == "openrouter" else None
        return ChatOpenAI(model=model, api_key=api_key, base_url=base_url, temperature=temperature)
    raise ValueError(f"Unsupported LLM provider {provider}")


def get_model(temperature: float = 0.0, provider: str | None = None, api_key: str | None = None, model: str | None = None):
    provider = LLM_PROVIDER if provider is None else provider
    api_key = LLM_API_KEY if api_key is None else api_key
    model = LLM_MODEL if model is None else model
    if not api_key:
        return None

    key = (provider, model, temperature)
    if key not in _models:
        _models[key] = build_model(provider, api_key, model, temperature)
    return _models[key]


def get_embeddings():
    global _embeddings
    from config import EMBEDDING_API_KEY

    if not EMBEDDING_API_KEY:
        return None
    if _embeddings is None:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        _embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL, google_api_key=EMBEDDING_API_KEY)
    return _embeddings


def structured(schema, temperature: float = 0.0, **options):
    model = get_model(temperature, **options)
    if model is None:
        return None
    provider = options.get("provider") or LLM_PROVIDER
    if provider in ("openai", "openrouter"):
        try:
            return model.with_structured_output(schema, method="json_schema")
        except Exception:
            return model.with_structured_output(schema)
    return model.with_structured_output(schema)


def invoke_structured(schema, messages, temperature: float = 0.0, attempts: int = 4, **options):
    runnable = structured(schema, temperature, **options)
    if runnable is None:
        return None

    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            result = runnable.invoke(messages)
            if result is not None:
                return result
            last_error = "model returned an empty result"
        except Exception as error:
            last_error = error
        logger.warning("LLM structured call attempt %s of %s failed: %s", attempt, attempts, last_error)
        if attempt < attempts:
            time.sleep(1.5 * attempt)

    logger.error("LLM call gave up after %s attempts: %s", attempts, last_error)
    return None


def extractor_tag(base: str) -> str:
    if LLM_ENABLED:
        return f"llm:{LLM_MODEL}:{base}"
    return f"fallback:dev:{base}"
