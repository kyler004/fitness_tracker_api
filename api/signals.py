from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Docstring for create_user_profile
    
    Automatically create a userProfile when a new User is created
    This ensures that every user has a fitness profile
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_prodile(sender, instance, **kwargs):
    """
    Docstring for save_user_prodile
    
    :Save the UserProfile whenever the User is saved 
    Thsi hnadles cases where the profile needs to be updated
    """
    # Checks if the user profile exists, if not creates it
    if not hasattr(instance, 'fitness_profile'): 
        UserProfile.objects.create(User=instance)
    else:
        instance.fitness_profile.save()
    