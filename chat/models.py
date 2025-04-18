from django.db import models


class ChatMessage(models.Model):
    user_input = models.TextField()
    ai_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User: {self.user_input} | AI: {self.ai_response}"