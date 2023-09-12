from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class InformationUser(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE)
    Phone = models.CharField(default='0000000000', max_length=15)
    Facebook = models.CharField(max_length=100, default="")