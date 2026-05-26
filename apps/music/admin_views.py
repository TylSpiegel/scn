from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def piece_explorer_redirect(request):
    from apps.music.models.piece import PieceIndexPage
    index = PieceIndexPage.objects.live().first()
    if index:
        return redirect(f'/admin/pages/{index.pk}/')
    return redirect('/admin/pages/')
