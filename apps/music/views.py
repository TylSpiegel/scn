from django.views.generic import DetailView

from .models import Piece


class PieceDetailView(DetailView):
    model = Piece
    template_name = 'music/piece_detail.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    context_object_name = 'piece'
