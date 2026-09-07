from django.shortcuts import render, get_object_or_404

from core.models import Domain


def domain_tracks_view(request, domain_id):
    domain = get_object_or_404(Domain.objects.prefetch_related('tracks'), id=domain_id)
    return render(request, 'core/domain_tracks.html', {'domain': domain})