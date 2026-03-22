from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a UserProfile when a new User is created.
    Also save the UserProfile whenever the User is saved.
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'fitness_profile'):
            instance.fitness_profile.save()
    