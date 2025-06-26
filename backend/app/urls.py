from django.urls import path
from .chat.views import ChatBotView, DocumentUploadView, CodeUploadView, EmbeddingView, ClearSessionView

urlpatterns = [
    path('chat/ask/', ChatBotView.as_view(), name='chatbot-ask'),
    path('chat/upload/docs/', DocumentUploadView.as_view(), name='chat-document-upload'),
    path('chat/upload/code/', CodeUploadView.as_view(), name='chat-code-upload'),
    path('chat/embedding/',EmbeddingView.as_view(), name='chat-embedding'),
    path('chat/clear_session/', ClearSessionView.as_view(), name='chat-clear-session'),
]
