import os
from django.db import models
from django.contrib.auth.models import User,Group
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from froala_editor.fields import FroalaField
# Create your models here.


class Category(models.Model):
	name=models.CharField(max_length=80)
	groups=models.ManyToManyField(Group,blank=True,null=True)
	position=models.IntegerField(blank=True,default=0)

	def __str__(self):
		return self.name

class Forum(models.Model):
	def image_path(instance,imagename):
		base_name,ext=os.path.splitext(imagename)
		return f"logo_image/{time.strftime('%y%m%d%H%M%S')}{ext}"
	category=models.ForeignKey(Category,related_name='forums',on_delete=models.SET_NULL)
	name=models.CharField(max_length=80)
	position=models.IntegerField(blank=True,default=0)
	description=models.TextField(blank=True,default='')
	moderators=models.ManyToManyField(User,blank=True,null=True)
	updated=models.DateTimeField(auto_now=True)
	post_count=models.IntegerField(blank=True,default=0)
	last_post=models.ForeignKey('Post',related_name='last_forum_post',blank=True,null=True)
	forum_logo=models.ImageField(default='',upload_to=image_path)

	def __str__(self):
		return self.name

class SubForum(models.Model):
	def image_path(instance,imagename):
		base_name,ext=os.path.splitext(imagename)
		return f"logo_image/{time.strftime('%y%m%d%H%M%S')}{ext}"

	forum=models.ForeignKey(Forum,related_name='Subforums',on_delete=models.CASCADE)
	name=models.CharField(max_length=80)
	leader=models.ForeignKey(User,on_delete=models.CASCADE)
	position=models.IntegerField(blank=True,default=0)
	description=models.TextField(blank=True,default='')
	moderators=models.ManyToManyField(User,blank=True,null=True)
	created=models.DateTimeField(auto_now_add=True)
	updated=models.DateTimeField(auto_now=True)
	post_count=models.IntegerField(blank=True,default=0)
	last_post=models.ForeignKey('Post',related_name='last_forum_post',blank=True,null=True)
	forum_logo=models.ImageField(default='',upload_to=image_path)

	def __str__(self):
		return self.name
class Forum_Subscriber(models.Model):
	forum=models.ForeignKey(Forum,related_name='forum_subscribers',on_delete=models.CASCADE)
	subforum=models.ForeignKey(SubForum,related_name='subforum_subscribers',blank=True,default=0,on_delete=models.CASCADE)
	subscriber=models.ForeignKey(User,related_name='subcribe',on_delete=models.CASCADE)
	time=models.DateTimeField(auto_now=True)
	def __str__(self):
		return self.subscriber
class Votable(models.Model):

	class Meta:
		abstract=True
	votes=GenericRelation(Vote)
	upvotes=models.IntegerField(default=0)
	downvotes=models.IntegerField(default=0)

	def upvote(self,user):
		pass
	def downvote(self,user):
		pass
class Post(Votable)
	forum=models.ForeignKey(Forum,related_name='forum_posts',on_delete=models.SET_NULL)
	subforum=models.ForeignKey(SubForum,related_name='subforum_posts',on_delete=models.SET_NULL)
	author=models.ForeignKey(User,related_name='posts',on_delete=models.SET_NULL)
	created=models.DateTimeField(auto_now_add=True)
	updated=models.DateTimeField(auto_now=True)
	updated_by=models.ForeignKey(User)
	post_title=models.CharField(max_length=255)
	body=FroalaField(theme='gray',plugins=('emoticons','image'))
	views=models.IntegerField(blank=True,default=0)
	
class Comment(Votable)
	post=models.ForeignKey(Forum,related_name='post_comments',on_delete=models.SET_NULL)
	user=models.ForeignKey(User,related_name='user_comments',on_delete=models.SET_NULL)
	comment_parent=models.ForeignKey('Comment',blank=True,default=0,on_delete=models.CASCADE)
	body=FroalaField(theme='gray',plugins=('emoticons','image','url'))
	time=models.DateTimeField(auto_now_add=True)

class Vote(models.Model):
	content_type=models.ForeignKey(ContentType,on_delete=models.PROTECT)
	object_id=models.PositiveIntegerField()
	content_object=GenericForeignKey('content_type','object_id')
	voter=models.ForeignKey(User,on_delete=models.PROTECT)
	type_of_vote=models.IntegerField(choices=
		(UPVOTE,'Upvote'),
		(DOWNVOTE,'Downvote'),
		)
	Submission_time=models.DateTimeField(auto_now_add=True)
	