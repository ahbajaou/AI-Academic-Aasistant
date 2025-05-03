from django.http import JsonResponse
import json
from .ai_agent import get_response
from .models import ChatMessage
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from drf_yasg import openapi

@swagger_auto_schema(
    method='post',
    operation_description="Chat with the AI agent",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'message': openapi.Schema(type=openapi.TYPE_STRING, description='User message')
        },
        required=['message']
    ),
    responses={
        200: openapi.Response(
            description="Response from AI agent",
            examples={
                "application/json": {
                    "message": "Hello, AI!",
                    "response": "Hello! How can I assist you today?",
                    "history": [
                        {
                            "user": "Hi!",
                            "ai": "Hello! How can I assist you today?",
                            "timestamp": "2025-05-03T12:00:00Z"
                        }
                    ]
                }
            }
        )
    }
)
@api_view(['POST'])
def chat(request):
    try:
        data = request.data
        message = data.get('message', '')
        if not message:
            return Response({"error": "No message provided"}, status=400)
        response_text = get_response(message)
        history = ChatMessage.objects.all().order_by('timestamp')
        history_data = [
            {"user": msg.user_input, "ai": msg.ai_response, "timestamp": msg.timestamp.isoformat()}
            for msg in history
        ]
        return Response({
            "message": message,
            "response": response_text,
            "history": history_data
        })
    except Exception as e:
        return Response({"error": f"Server error: {str(e)}"}, status=500)