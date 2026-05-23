from django.urls import path

from .views import PieceDetailView

urlpatterns = [
    path('<slug:slug>/', PieceDetailView.as_view(), name='piece-detail'),
]
