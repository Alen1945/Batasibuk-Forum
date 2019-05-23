from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Notification(models.Model):
	notif_for=models.ForeignKey(User,related_name='user_notif',on_delete=models.CASCADE)
	detail=models.TextField()
	url=models.URLField()
	timestamp=models.DateTimeField(auto_now_add=True)
	