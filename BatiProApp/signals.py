# from django.db.models.signals import post_save
# from django.dispatch import receiver

# from .models import Client , User # Import the Client model

# @receiver(post_save, sender=User)
# def create_client_profile(sender, instance, created, **kwargs):
#     if created:
#         # Only create a Client instance if a new User was created
#         Client.objects.create(user_ptr=instance)
