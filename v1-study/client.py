"""OpenRouter client: panel loop, version/date/cost logging, retry on parse failure."""
import json, os, time, datetime, requests
import config


def _headers():
    key = os.environ.get(config.OPENROUTER_API_KEY_ENV)
    if not key:
        raise RuntimeError(
            f"{config.OPENROUTER_API_KEY_ENV} not set. Export your OpenRouter "
            f"API key before running.")
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": config.HTTP_REFERER,
        "X-Title": config.APP_TITLE,
    }


def _payload(model_slug, messages, temperature, max_tokens):
    return {
        "model": model_slug,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }


def completion(model_slug, user_prompt, temperature=None, max_tokens=None,
               system=None, retries=3, backoff=4.0, timeout=180):
    """Single chat completion. Returns dict with text, usage, model_version, ms."""
    headers = _headers()
    msgs = []
    if system:
        msgs.append({"role": "system", "content": system})
    msgs.append({"role": "user", "content": user_prompt})
    body = _payload(model_slug, msgs,
                    config.TEMPERATURE if temperature is None else temperature,
                    4096 if max_tokens is None else max_tokens)
    last_err = None
    for attempt in range(retries):
        t0 = time.time()
        try:
            r = requests.post(f"{config.OPENROUTER_BASE_URL}/chat/completions",
                              headers=headers, json=body, timeout=timeout)
            r.raise_for_status()
            data = r.json()
            text = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return {
                "text": text,
                "usage": usage,
                "model_version": data.get("model", model_slug),
                "ms": int((time.time() - t0) * 1000),
                "attempts": attempt + 1,
                "ts": datetime.datetime.utcnow().isoformat() + "Z",
            }
        except Exception as e:
            last_err = str(e)
            time.sleep(backoff * (attempt + 1))
    return {"text": None, "error": last_err, "attempts": retries,
            "ts": datetime.datetime.utcnow().isoformat() + "Z"}


def estimate_cost(usage, slug):
    """Cost in USD from usage tokens. Returns None if slug is not priced."""
    table = PRICING_PER_M.get(slug)
    if not table or not usage:
        return None
    inp = usage.get("prompt_tokens", 0)
    out = usage.get("completion_tokens", 0)
    return (inp / 1_000_000) * table[0] + (out / 1_000_000) * table[1]


# Approximate USD per 1M tokens — OpenRouter, meio de 2026 (ajustar se preço mudar)
PRICING_PER_M = {
    "openai/gpt-4o-mini": (0.15, 0.60),
    "openai/gpt-4o": (2.50, 10.00),
    "openai/gpt-4.1": (2.00, 8.00),
    "anthropic/claude-haiku-4.5": (1.00, 5.00),
    "anthropic/claude-sonnet-4.6": (3.00, 15.00),
    "anthropic/claude-opus-4.6": (5.00, 25.00),
    "google/gemini-2.5-flash-lite": (0.10, 0.40),
    "google/gemini-2.5-flash": (0.30, 2.50),
    "google/gemini-2.5-pro": (1.25, 10.00),
    "meta-llama/llama-3.1-8b-instruct": (0.02, 0.03),
    "meta-llama/llama-3.1-70b-instruct": (0.40, 0.40),
    "meta-llama/llama-3.3-70b-instruct": (0.10, 0.32),
    "mistralai/mistral-small-3.2-24b-instruct": (0.075, 0.20),
    "mistralai/mistral-medium-3.1": (0.40, 2.00),
    "mistralai/mistral-large": (2.00, 6.00),
    "deepseek/deepseek-v4-flash": (0.10, 0.20),
    "deepseek/deepseek-v3.2": (0.23, 0.34),
    "deepseek/deepseek-v4-pro": (0.43, 0.87),
    "qwen/qwen-2.5-72b-instruct": (0.36, 0.40),
    "qwen/qwen3-max": (0.78, 3.90),
    "qwen/qwen3-235b-a22b": (0.45, 1.82),
}
