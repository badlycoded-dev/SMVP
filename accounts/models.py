from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="User")
    bio = models.TextField(max_length=500, blank=True, verbose_name="Bio")
    avatar = models.ImageField(upload_to='avatar/', blank=True, null=True, verbose_name="Avatar")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Date of Birth")
    location = models.CharField(max_length=50, blank=True, verbose_name="City")
    website = models.URLField(blank=True, verbose_name="Website")
    email_notifications = models.BooleanField(default=False, verbose_name="Duplicate notifications to email")

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"Profile {self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    Profile.objects.get_or_create(user=instance)
    instance.profile.save()