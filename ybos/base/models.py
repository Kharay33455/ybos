from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    email = models.TextField()

    def __str__(self):
        return self.user.username


class EmailCode(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length = 6, default = 000000)
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(default = datetime.now())

    def __str__(self):
        return f'{self.email} verification code.'