from django.urls import path
from .chat.views import ChatBotView, FileUploadView, EmbeddingView, ClearSessionView

urlpatterns = [
    path('chat/ask/', ChatBotView.as_view(), name='chatbot-ask'),
    path('chat/upload/', FileUploadView.as_view(), name='chat-upload'),
    path('chat/embedding/',EmbeddingView.as_view(), name='chat-embedding'),
    path('chat/clear_session/', ClearSessionView.as_view(), name='chat-clear-session'),
]
