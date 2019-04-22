import os
import time
from django.db import models
from django.contrib.auth.models import User,Group
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.http import JsonResponse
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.

UPVOTE=1
DOWNVOTE=2
class Category(models.Model):
	name=models.CharField(max_length=80)
	groups=models.ManyToManyField(Group,blank=True)
	position=models.IntegerField(blank=True,default=0)
	def __str__(self):
		return self.name

class Forum(models.Model):
	def image_path(instance,imagename):
		base_name,ext=os.path.splitext(imagename)
		return f"logo_image/{time.strftime('%y%m%d%H%M%S')}{ext}"
	category=models.ForeignKey(Category,related_name='forums',blank=True,null=True,on_delete=models.PROTECT)
	name=models.CharField(max_length=80)
	position=models.IntegerField(blank=True,default=0)
	description=models.TextField(blank=True,default='')
	moderators=models.ManyToManyField(User,blank=True)
	updated=models.DateTimeField(auto_now=True)
	post_count=models.IntegerField(blank=True,default=0)
	last_post=models.ForeignKey('Post',related_name='last_forum_post',blank=True,null=True,on_delete=models.CASCADE)
	forum_logo=models.ImageField(default='',upload_to=image_path)

	def __str__(self):
		return self.name

class SubForum(models.Model):
	def image_path(instance,imagename):
		base_name,ext=os.path.splitext(imagename)
		return f"logo_image/{time.strftime('%y%m%d%H%M%S')}{ext}"

	forum=models.ForeignKey(Forum,related_name='subforums',on_delete=models.CASCADE)
	name=models.CharField(max_length=80)
	leader=models.ForeignKey(User,related_name='subforum_leader',on_delete=models.CASCADE)
	position=models.IntegerField(blank=True,default=0)
	description=models.TextField(blank=True,default='')
	moderators=models.ManyToManyField(User,related_name='subforum_moderator',blank=True)
	created=models.DateTimeField(auto_now_add=True)
	updated=models.DateTimeField(auto_now=True)
	post_count=models.IntegerField(blank=True,default=0)
	last_post=models.ForeignKey('Post',related_name='last_subforum_post',blank=True,null=True,on_delete=models.CASCADE)
	forum_logo=models.ImageField(default='',upload_to=image_path)

	def __str__(self):
		return self.name
class Forum_Subscriber(models.Model):
	forum=models.ForeignKey(Forum,related_name='forum_subscribers',on_delete=models.CASCADE)
	subforum=models.ForeignKey(SubForum,related_name='subforum_subscribers',blank=True,null=True,on_delete=models.CASCADE)
	subscriber=models.ForeignKey(User,related_name='subcribe',on_delete=models.CASCADE)
	time=models.DateTimeField(auto_now=True)
	def __str__(self):
		return self.subscriber

class Vote(models.Model):
	content_type=models.ForeignKey(ContentType,on_delete=models.PROTECT)
	object_id=models.PositiveIntegerField()
	content_object=GenericForeignKey('content_type','object_id')
	voter=models.ForeignKey(User,on_delete=models.PROTECT)
	type_of_vote=models.IntegerField(choices=(
		(UPVOTE,'Upvote'),
		(DOWNVOTE,'Downvote'),
		))
	submission_time=models.DateTimeField(auto_now_add=True)
class Votable(models.Model):

	class Meta:
		abstract=True
	votes=GenericRelation(Vote)
	upvotes=models.IntegerField(default=0,blank=True)
	downvotes=models.IntegerField(default=0,blank=True)
	vote_self=False
	def upvote(self,user):
		self._vote(user,UPVOTE)
	def downvote(self,user):
		self._vote(user,DOWNVOTE)
	def undo_vote(self,user,type_of_vote):
		content_type=ContentType.objects.get_for_model(self)
		vote=Vote.objects.filter(content_type=content_type.id,object_id=self.id,type_of_vote=type_of_vote,voter=user)
		vote.delete()
		self.upvotes=int(Vote.objects.filter(content_type=content_type.id,object_id=self.id,type_of_vote=UPVOTE).count())
		self.downvotes=int(Vote.objects.filter(content_type=content_type.id,object_id=self.id,type_of_vote=DOWNVOTE).count())
		self.save(update_fields=["upvotes","downvotes"])
	def change_vote(self,user,type_of_vote):
		content_type=ContentType.objects.get_for_model(self)
		vote=Vote.objects.get(content_type=content_type.id,object_id=self.id,voter=user)
		vote.type_of_vote=type_of_vote
		vote.save()
		self.upvotes=int(Vote.objects.filter(content_type=content_type.id,object_id=self.id,type_of_vote=UPVOTE).count())
		self.downvotes=int(Vote.objects.filter(content_type=content_type.id,object_id=self.id,type_of_vote=DOWNVOTE).count())
		self.save(update_fields=['upvotes','downvotes'])
	def _vote(self,user,type_of_vote):
		content_type=ContentType.objects.get_for_model(self)
		if self._already_voted(user,content_type):
			ready_voted=Vote.objects.filter(content_type=content_type.id,object_id=self.id,voter=user,type_of_vote=type_of_vote)
			if ready_voted:
				return self.undo_vote(user,type_of_vote)
			else:
				return self.change_vote(user,type_of_vote)
		if self._voting_for_myself(user):
			self.vote_self=True
			return
		vote=Vote(content_object=self,voter=user,type_of_vote=type_of_vote)
		vote.save()
		self.upvotes=int(Vote.objects.filter(content_type=content_type.id,object_id=self.id,type_of_vote=UPVOTE).count())
		self.downvotes=int(Vote.objects.filter(content_type=content_type.id,object_id=self.id,type_of_vote=DOWNVOTE).count())
		self.save(update_fields=["upvotes","downvotes"])

	def _already_voted(self,user,content_type):
		return Vote.objects.filter(
			content_type=content_type.id,\
			object_id=self.id,\
			voter=user)\
			.exists()

def slug_save(obj):
	if not obj.post_slug:
		maximal_loop=50
		count_loop=0
		get_str=13
		slug_status=True
		while slug_status:
			slug_status=False
			if count_loop>maximal_loop:
				get_str=get_str+1
			obj.post_slug=get_random_string(get_str)
			other_post_slug=type(obj).objects.filter(post_slug=obj.post_slug)
			if other_post_slug:
				slug_status=True
				count_loop=count_loop+1 
class Post(Votable):
	forum=models.ForeignKey(Forum,related_name='forum_posts',null=True,on_delete=models.PROTECT)
	subforum=models.ForeignKey(SubForum,related_name='subforum_posts',blank=True,null=True,on_delete=models.PROTECT)
	author=models.ForeignKey(User,related_name='posts',on_delete=models.PROTECT)
	created=models.DateTimeField(auto_now_add=True)
	updated=models.DateTimeField(auto_now=True)
	updated_by=models.ForeignKey(User,blank=True,null=True,on_delete=models.PROTECT)
	post_title=models.CharField(max_length=255)
	body=RichTextUploadingField(blank=True,	
								config_name='post_thread',
								external_plugin_resources=[(
									'emoji',
									'/static/ckeditor_plugins/emoji/',
									'plugin.js')]
								)
	post_slug=models.SlugField(max_length=255,blank=True,editable=False)
	status=models.IntegerField(choices=(
		(0,'Draft'),
		(1,'Post')
		),default=0)
	views=models.IntegerField(blank=True,default=0)

	def _voting_for_myself(self,user):
		return self.author.id==user.id
	def __str__(self):
		return self.post_title
	def save(self,*args,**kwargs):
		slug_save(self)
		super().save(*args,**kwargs)
class Comment(Votable):
	post=models.ForeignKey(Post,related_name='post_comments',null=True,on_delete=models.PROTECT)
	user=models.ForeignKey(User,related_name='user_comments',null=True,on_delete=models.PROTECT)
	comment_parent=models.ForeignKey('Comment',related_name='comment_reply',blank=True,null=True,on_delete=models.CASCADE)
	body=RichTextUploadingField(config_name='comment_thread',
								external_plugin_resources=[(
									'emoji',
									'/static/ckeditor_plugins/emoji/',
									'plugin.js')])
	time=models.DateTimeField(auto_now_add=True)

	def _voting_for_myself(self,user):
		return self.user.id==user.id

	def __str__(self):
		return f"{self.user} comments"

class ViewPost(models.Model):
	post=models.ForeignKey(Post,related_name='post_views',on_delete=models.CASCADE)
	ip=models.CharField(max_length=40)
	session=models.CharField(max_length=40)
	created=models.DateTimeField(default=timezone.now)
