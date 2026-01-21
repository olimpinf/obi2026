# app/routing.py
from django.urls import path
from .lsp_consumer import LspConsumer

websocket_urlpatterns = [
    path("ws/lsp/<str:language_id>/", LspConsumer.as_asgi()),
]
