from django.conf import settings
from openai import OpenAI


SYSTEM_PROMPT = (
    "You are a helpful assistant for a developer portfolio website. "
    "Answer clearly, keep it concise, and focus on portfolio/project context."
)


def generate_chat_reply(user_prompt: str) -> str:
    if not settings.OPENAI_API_KEY:
        return "Chatbot is not configured yet. Add OPENAI_API_KEY in your .env file."

    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            temperature=0.3,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or "Sorry, no response."
    except Exception:
        return "AI service is temporarily unavailable. Please try again in a moment."
