"""Config do painel v2 — 21 modelos, congelado p/ pré-registro.

Sete labs × três tiers. Slugs OpenRouter: confirmar na página do modelo
antes da corrida full (já mudaram nomes no passado).
"""
import os

# (display_name, openrouter_slug, temperature, max_tokens)
PANEL = [
    # OpenAI — economy → standard (manuscript) → frontier
    ("GPT-4o-mini",              "openai/gpt-4o-mini",                 1.0, 4096),
    ("GPT-4o",                   "openai/gpt-4o",                      1.0, 4096),
    ("GPT-4.1",                  "openai/gpt-4.1",                     1.0, 4096),
    # Anthropic
    ("Claude Haiku 4.5",         "anthropic/claude-haiku-4.5",         1.0, 4096),
    ("Claude Sonnet 4.6",        "anthropic/claude-sonnet-4.6",        1.0, 4096),
    ("Claude Opus 4.6",          "anthropic/claude-opus-4.6",          1.0, 4096),
    # Google
    ("Gemini 2.5 Flash Lite",    "google/gemini-2.5-flash-lite",       1.0, 4096),
    ("Gemini 2.5 Flash",         "google/gemini-2.5-flash",            1.0, 4096),
    ("Gemini 2.5 Pro",           "google/gemini-2.5-pro",              1.0, 4096),
    # Meta
    ("Llama 3.1 8B Instruct",    "meta-llama/llama-3.1-8b-instruct",   1.0, 4096),
    ("Llama 3.1 70B Instruct",   "meta-llama/llama-3.1-70b-instruct",  1.0, 4096),
    ("Llama 3.3 70B Instruct",   "meta-llama/llama-3.3-70b-instruct", 1.0, 4096),
    # Mistral
    ("Mistral Small 3.2 24B",    "mistralai/mistral-small-3.2-24b-instruct", 1.0, 4096),
    ("Mistral Medium 3.1",       "mistralai/mistral-medium-3.1",       1.0, 4096),
    ("Mistral Large",            "mistralai/mistral-large",            1.0, 4096),
    # DeepSeek — V4 Flash → V3.2 → V4 Pro
    ("DeepSeek V4 Flash",        "deepseek/deepseek-v4-flash",         1.0, 4096),
    ("DeepSeek V3.2",            "deepseek/deepseek-v3.2",             1.0, 4096),
    ("DeepSeek V4 Pro",          "deepseek/deepseek-v4-pro",           1.0, 4096),
    # Qwen
    ("Qwen 2.5 72B Instruct",    "qwen/qwen-2.5-72b-instruct",         1.0, 4096),
    ("Qwen3 Max",                "qwen/qwen3-max",                     1.0, 4096),
    ("Qwen3 235B A22B",          "qwen/qwen3-235b-a22b",               1.0, 4096),
]

# Provider lab and tier metadata for intra-laboratory analyses.
MODEL_LAB = {
    "GPT-4o-mini": "OpenAI", "GPT-4o": "OpenAI", "GPT-4.1": "OpenAI",
    "Claude Haiku 4.5": "Anthropic", "Claude Sonnet 4.6": "Anthropic",
    "Claude Opus 4.6": "Anthropic",
    "Gemini 2.5 Flash Lite": "Google", "Gemini 2.5 Flash": "Google",
    "Gemini 2.5 Pro": "Google",
    "Llama 3.1 8B Instruct": "Meta", "Llama 3.1 70B Instruct": "Meta",
    "Llama 3.3 70B Instruct": "Meta",
    "Mistral Small 3.2 24B": "Mistral", "Mistral Medium 3.1": "Mistral",
    "Mistral Large": "Mistral",
    "DeepSeek V4 Flash": "DeepSeek", "DeepSeek V3.2": "DeepSeek",
    "DeepSeek V4 Pro": "DeepSeek",
    "Qwen 2.5 72B Instruct": "Qwen", "Qwen3 Max": "Qwen",
    "Qwen3 235B A22B": "Qwen",
}

MODEL_TIER = {
    "GPT-4o-mini": 1, "GPT-4o": 2, "GPT-4.1": 3,
    "Claude Haiku 4.5": 1, "Claude Sonnet 4.6": 2, "Claude Opus 4.6": 3,
    "Gemini 2.5 Flash Lite": 1, "Gemini 2.5 Flash": 2, "Gemini 2.5 Pro": 3,
    "Llama 3.1 8B Instruct": 1, "Llama 3.1 70B Instruct": 2,
    "Llama 3.3 70B Instruct": 3,
    "Mistral Small 3.2 24B": 1, "Mistral Medium 3.1": 2, "Mistral Large": 3,
    "DeepSeek V4 Flash": 1, "DeepSeek V3.2": 2, "DeepSeek V4 Pro": 3,
    "Qwen 2.5 72B Instruct": 1, "Qwen3 Max": 2, "Qwen3 235B A22B": 3,
}

# cohort do paper de valores (subset p/ comparação)
LEGACY_SEVEN = [
    "GPT-4o", "Claude Haiku 4.5", "Mistral Large", "Llama 3.3 70B Instruct",
    "DeepSeek V4 Pro", "Qwen 2.5 72B Instruct", "Gemini 2.5 Flash Lite",
]
# Values manuscript used DeepSeek V3; personality tier 2 uses V3.2 on OpenRouter.
LEGACY_DEEPSEEK_MANUSCRIPT = "DeepSeek V3"

N_SESSIONS = 30
TEMPERATURE = 1.0

IPIP_BLOCK_SIZE = 50
PID5_BLOCK_SIZE = 32
CSIV_BLOCK_SIZE = 64

RESPONSE_CONTRACT = (
    "Reply with ONLY a numbered list. Each line is '<item number> = <rating>'. "
    "Use one line per item, in order, with no extra commentary, no preamble, and "
    "no text after the list. Rate every item."
)

OPENROUTER_API_KEY_ENV = "OPENROUTER_API_KEY"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
HTTP_REFERER = "https://meusvalores.app"
APP_TITLE = "v1-study"

ROOT = os.path.dirname(os.path.abspath(__file__))
INSTRUMENTS_DIR = os.path.join(ROOT, "instruments")
OUTPUTS_DIR = os.path.join(ROOT, "outputs")

SMOKE_MODELS = ["GPT-4o", "Claude Haiku 4.5"]
SMOKE_SESSIONS = 1
SMOKE_INSTRUMENTS = ["ipip"]
