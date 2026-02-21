import json

from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .models import ChatMessage
from .services.openai_client import generate_chat_reply


def _is_rate_limited(ip: str, limit: int = 20, seconds: int = 60) -> bool:
    key = f"chat-rate-{ip}"
    try:
        requests = cache.get(key, 0)
        if requests >= limit:
            return True
        cache.set(key, requests + 1, timeout=seconds)
        return False
    except Exception:
        # If cache backend is down, do not break chatbot endpoint.
        return False


@csrf_exempt
@require_POST
def chat_api_view(request):
    ip = request.META.get("REMOTE_ADDR", "unknown")
    if _is_rate_limited(ip):
        return JsonResponse({"error": "Rate limit exceeded. Try again."}, status=429)

    try:
        payload = json.loads(request.body.decode("utf-8"))
        prompt = payload.get("message", "").strip()
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    if not prompt:
        return JsonResponse({"error": "Message is required."}, status=400)
    if len(prompt) > 1200:
        return JsonResponse({"error": "Message is too long."}, status=400)

    answer = generate_chat_reply(prompt)
    ChatMessage.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key or "",
        user_message=prompt,
        assistant_message=answer,
    )
    return JsonResponse({"reply": answer})
