"""
Prompt templates for the ad generation node.
These prompts guide the LLM to generate high-converting, personalized ad creatives based on marketing strategy and user data.
"""

OPENAI_SYSTEM_PROMPT = """
You are a creative ad copywriter assistant specialized in digital marketing.
Your task is to write compelling, platform-optimized advertisements that align with the target persona and campaign strategy.
"""

OPENAI_HUMAN_PROMPT = """
Given the following campaign strategy and user persona, generate an advertisement copy:

User Persona:
{user_persona}

Campaign Strategy:
{campaign_strategy}

Guidelines:
- Write a short, engaging, and persuasive ad copy.
- Tailor the language and tone to suit the persona's preferences.
- Include a strong call-to-action (CTA).
- Keep platform constraints in mind (e.g., Instagram, Facebook).

Respond only with the ad copy text. Do not include explanations or formatting.
"""

GROQ_SYSTEM_PROMPT = OPENAI_SYSTEM_PROMPT
GROQ_HUMAN_PROMPT = OPENAI_HUMAN_PROMPT
