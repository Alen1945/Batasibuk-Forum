import os
import time
from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from batasibuk_forum.models import Follow,Followble






def avatar_path(instance,photo_name):
	base_name,ext=os.path.splitext(photo_name)
	return f"profile_image/user/{instance.user.id}/{instance.user.username}/{time.strftime('%y_%m_%d_%H_%M_%s')}_{base_name[0:3]}{ext}"
def header_path(instance,header_name):
	base_name,ext=os.path.splitext(header_name)
	return f"profile_image/user/{instance.user.id}/{instance.user.username}/header/{time.strftime('%y_%m_%d_%H_%M_%s')}_{base_name[0:3]}{ext}"

Male=1
Female=2
class Profile(Followble):
	user=models.OneToOneField(User,on_delete=models.CASCADE)
	info=models.CharField(max_length=30,blank=True,default='Kreator Batasibuk')
	date_of_birth=models.DateField(blank=True,null=True)
	gender=models.IntegerField(choices=(
		(Male,'Male'),
		(Female,'Female')
		),blank=True,default=Male)
	user_photo=models.ImageField(default='profile_image/default_profile_normal.png',upload_to=avatar_path)
	user_header=models.ImageField(default='profile_image/default_header.jpg',upload_to=header_path)
	location = models.CharField(max_length=30, blank=True)
	website=models.URLField(blank=True)

	def __str__(self):
		return f'{self.user.username} Profile'
	def _following_self(self,user_follow):
		return self.user.id==user_follow.id

	