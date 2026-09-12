import logging
import time
from config import LLM_ENABLED, LLM_PROVIDER, LLM_API_KEY, LLM_MODEL, EMBEDDING_MODEL

logger = logging.getLogger(__name__)

_model = None
_embeddings = None


def available() -> bool:
    return LLM_ENABLED


def get_model(temperature: float = 0.0):
    global _model
    if not LLM_ENABLED:
        return None
    if _model is None:
        if LLM_PROVIDER == "google":
            from langchain_google_genai import ChatGoogleGenerativeAI

            _model = ChatGoogleGenerativeAI(
                model=LLM_MODEL, google_api_key=LLM_API_KEY, temperature=temperature
            )
        elif LLM_PROVIDER == "openai":
            from langchain_openai import ChatOpenAI

            _model = ChatOpenAI(model=LLM_MODEL, api_key=LLM_API_KEY, temperature=temperature)
        else:
            raise ValueError(f"Unsupported LLM_PROVIDER {LLM_PROVIDER}")
    return _model


def get_embeddings():
    global _embeddings
    if not LLM_ENABLED or LLM_PROVIDER != "google":
        return None
    if _embeddings is None:
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        _embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL, google_api_key=LLM_API_KEY)
    return _embeddings


def structured(schema, temperature: float = 0.0):
    model = get_model(temperature)
    if model is None:
        return None
    return model.with_structured_output(schema)


def invoke_structured(schema, messages, temperature: float = 0.0, attempts: int = 3):
    runnable = structured(schema, temperature)
    if runnable is None:
        return None

    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            return runnable.invoke(messages)
        except Exception as error:
            last_error = error
            logger.warning("LLM call failed (attempt %s of %s): %s", attempt, attempts, error)
            if attempt < attempts:
                time.sleep(1.5 * attempt)

    logger.error("LLM call gave up after %s attempts: %s", attempts, last_error)
    return None


def extractor_tag(base: str) -> str:
    if LLM_ENABLED:
        return f"llm:{LLM_MODEL}:{base}"
    return f"fallback:dev:{base}"
