from django.urls import path
from .chat.views import ChatBotView, FileUploadView

urlpatterns = [
    path('chat/ask/', ChatBotView.as_view(), name='chatbot-ask'),
    path('chat/upload/', FileUploadView.as_view(), name='chat-upload'),
]
