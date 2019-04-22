from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Profile(models.Model):
	user=models.ForeignKey(User,related_name='user_profile',on_delete=models.CASCADE)
	