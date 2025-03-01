from django.db import models


class User(models.Model):
    first_name = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)
    language_code = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    created = models.DateField(auto_now_add=True)
    last_activity = models.DateField(auto_now_add=True)
    notifications = models.BooleanField()

    def __str__(self):
        return f"{self.first_name} ({self.user_id})"


class Subscription(models.Model):
    user_id = models.CharField(max_length=255, blank=True, null=True)  # ID пользователя Telegram
    name = models.CharField(max_length=255, blank=True, null=True)  # Название подписки
    icon = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    cost = models.CharField(max_length=255, blank=True, null=True)
    period = models.CharField(max_length=255, blank=True, null=True)
    periodType = models.CharField(max_length=255, blank=True, null=True)
    paymentDate = models.DateField(blank=True, null=True)
    notifications = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    last_notification = models.DateField(blank=True, null=True)


    def __str__(self):
        return f"{self.name} ({self.user_id})"
