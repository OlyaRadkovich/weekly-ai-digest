import httpx
from datetime import datetime
from loguru import logger
from .config import config

PROMPT_REGULAR = (
    "Role: Senior AI Tech Lead. Task: Generate a WEEKLY DIGEST (4-5 items) from the LAST 7 DAYS for QA/SDETs.\n"
    "Target Audience: SDETs, QA Engineers, Developers.\n"
    "\n"
    "SCOPE (AI ONLY):\n"
    "1. AI Automation: Tools using LLMs/Agents (ZeroStep, AI self-healing). IGNORING standard Cypress/Selenium updates.\n"
    "2. Dev Tools & Models: Major updates in coding assistants (Cursor, Copilot) and Tier-1 LLMs (OpenAI, Claude, Gemini, DeepSeek, Mistral, Llama, Qwen, Local LLMs, etc.) specifically impacting code generation or testing.\n"
    "3. Strategy: Global outages/downtimes of major AI providers, AI tool data leaks or source code breaches, changes in API pricing/billing models (e.g., usage-based limits), and major vendor policy shifts.\n"
    "\n"
    "OUTPUT RULES:\n"
    "1. LINKS: Use inline Markdown [Source](URL) ONLY. NO footnotes like [1]. If a deep link fails, use the root URL.\n"
    "2. FORMAT & TEMPLATES (Follow Strictly):\n"
    "   - For News/Updates:  * **Title** (Date: DD.MM): Summary... [Source Name](URL)\n"
    "3. QUANTITY: 4-5 items total.\n"
    "4. TIMEFRAME: Strict 7-day lookback for News.\n"
    "5. LANGUAGE: Russian."
)

PROMPT_WITH_GUIDES = (
    "Role: Senior AI Tech Lead. Task: Generate a WEEKLY DIGEST (4-5 items) from the LAST 7 DAYS for QA/SDETs.\n"
    "Target Audience: SDETs, QA Engineers, Developers.\n"
    "\n"
    "SCOPE (AI ONLY):\n"
    "1. AI Automation: Tools using LLMs/Agents (ZeroStep, AI self-healing). IGNORING standard Cypress/Selenium updates.\n"
    "2. Dev Tools & Models: Major updates in coding assistants (Cursor, Copilot) and Tier-1 LLMs (OpenAI, Claude, Gemini, DeepSeek, Mistral, Llama, Qwen, Local LLMs, etc.) specifically impacting code generation or testing.\n"
    "3. Strategy: Global outages/downtimes of major AI providers, AI tool data leaks or source code breaches, changes in API pricing/billing models (e.g., usage-based limits), and major vendor policy shifts.\n"
    "4. Education: High-value engineering tutorials/guides on AI in QA (no marketing fluff).\n"
    "\n"
    "OUTPUT RULES:\n"
    "1. LINKS: Use inline Markdown [Source](URL) ONLY. NO footnotes like [1]. If a deep link fails, use the root URL.\n"
    "2. FORMAT & TEMPLATES (Follow Strictly):\n"
    "   - For News:  * **Title** (Date: DD.MM): Summary... [Source Name](URL)\n"
    "   - For Guides: * **Title** (Type: Guide): Summary... [Source Name](URL)\n"
    "3. QUANTITY: 4-5 items total. Prioritize News, fill gap with 1-2 Guides.\n"
    "4. TIMEFRAME: Strict 7-day lookback for News. Guides can be older if timeless and high-value.\n"
    "5. LANGUAGE: Russian."
)


async def fetch_ai_news() -> str:
    current_date = datetime.now()
    current_date_str = current_date.strftime("%Y-%m-%d")

    is_first_monday = current_date.day <= 7

    if is_first_monday:
        logger.info("First Monday of the month: Looking for news and guides.")
        system_prompt = PROMPT_WITH_GUIDES
        user_prompt =f"Generate a Weekly AI Digest for QA/SDET for the week ending {current_date_str}. MUST include 1 educational guide."
    else:
        logger.info("Typical Monday: Looking only for news.")
        system_prompt = PROMPT_REGULAR
        user_prompt = f"Generate a Weekly AI Digest for QA/SDET for the week ending {current_date_str}."

    headers = {
        "Authorization": f"Bearer {config.openrouter_api_key.get_secret_value()}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/OlyaRadkovich/weekly-ai-digest",
        "X-Title": "Weekly AI Digest for QA",
    }

    payload = {
        "model": config.model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2,
    }

    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Error requesting OpenRouter: {e}")
            raise
