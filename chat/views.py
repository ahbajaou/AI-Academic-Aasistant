from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .ai_agent import get_response
from .models import ChatMessage

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            if not message:
                return JsonResponse({"error": "No message provided"}, status=400)
            response_text = get_response(message)
            # Include history (optional, remove if not needed)
            history = ChatMessage.objects.all().order_by('timestamp')
            history_data = [
                {"user": msg.user_input, "ai": msg.ai_response, "timestamp": msg.timestamp.isoformat()}
                for msg in history
            ]
            return JsonResponse({
                "message": message,
                "response": response_text,
                "history": history_data
            })
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Server error: {str(e)}"}, status=500)
    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)