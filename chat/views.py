from django.http import JsonResponse
import json
import uuid
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
        
        # Get AI response
        response_text = get_response(message)
        
        # Handle user identification (authenticated or anonymous)
        if request.user.is_authenticated:
            # For authenticated users
            user = request.user
            session_id = None
            
            # Save the chat message
            chat_message = ChatMessage.objects.create(
                user=user,
                user_input=message,
                ai_response=response_text
            )
            
            # Get chat history for this user
            history = ChatMessage.objects.filter(user=user).order_by('timestamp')
        else:
            # For anonymous users
            user = None
            
            # Get or create session ID
            if not request.session.get('chat_session_id'):
                request.session['chat_session_id'] = str(uuid.uuid4())
            
            session_id = request.session['chat_session_id']
            
            # Save the chat message
            chat_message = ChatMessage.objects.create(
                session_id=session_id,
                user_input=message,
                ai_response=response_text
            )
            
            # Get chat history for this session
            history = ChatMessage.objects.filter(session_id=session_id).order_by('timestamp')
        
        # Format history data
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

@swagger_auto_schema(
    method='get',
    operation_description="Get chat history",
    responses={
        200: openapi.Response(
            description="Chat history",
            examples={
                "application/json": {
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
@api_view(['GET'])
def get_chat_history(request):
    try:
        # Get user-specific or session-specific chat history
        if request.user.is_authenticated:
            # For authenticated users
            history = ChatMessage.objects.filter(user=request.user).order_by('timestamp')
        else:
            # For anonymous users
            session_id = request.session.get('chat_session_id')
            if not session_id:
                # New session without history
                return Response({"history": []})
            
            history = ChatMessage.objects.filter(session_id=session_id).order_by('timestamp')
        
        # Format history data
        history_data = [
            {"user": msg.user_input, "ai": msg.ai_response, "timestamp": msg.timestamp.isoformat()}
            for msg in history
        ]
        
        return Response({"history": history_data})
    except Exception as e:
        return Response({"error": f"Server error: {str(e)}"}, status=500)