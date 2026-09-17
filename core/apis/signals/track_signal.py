from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models.core import Domain, Track

@receiver(post_save, sender=Domain)
def attach_default_tracks(sender, instance, created, **kwargs):
    if created:
        default_tracks = Track.objects.all()
        instance.tracks.set(default_tracks)