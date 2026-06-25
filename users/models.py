from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name="пользователь",
        related_name="profile",
        on_delete=models.CASCADE,
    )
    full_name = models.CharField("Ф. И. О.", max_length=255, blank=True)
    phone = models.CharField("телефон", max_length=30, unique=True, null=True, blank=True)
    avatar = models.ImageField("аватар", upload_to="avatars/", blank=True)

    created_at = models.DateTimeField("дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("дата обновления", auto_now=True)

    class Meta:
        verbose_name = "профиль"
        verbose_name_plural = "профили"

    def save(self, *args, **kwargs):
        if self.phone == "":
            self.phone = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name or self.user.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, raw=False, **kwargs):
    if raw:
        return

    if created:
        Profile.objects.create(
            user=instance,
            full_name=instance.get_full_name() or instance.username,
        )
