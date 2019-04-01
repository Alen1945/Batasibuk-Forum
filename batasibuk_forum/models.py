import os
import time
from django.db import models
from django.contrib.auth.models import User,Group
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
from django.contrib.contenttypes.models import ContentType
from froala_editor.fields import FroalaField
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

	forum=models.ForeignKey(Forum,related_name='Subforums',on_delete=models.CASCADE)
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
	subforum=models.ForeignKey(SubForum,related_name='subforum_subscribers',blank=True,default=0,on_delete=models.CASCADE)
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

	def upvote(self,user):
		self._vote(user,UPVOTE)
	def downvote(self,user):
		self._vote(user,DOWNVOTE)
	def undo_vote(self,user):
		content_type=ContentType.objects.get_for_model(self)
		votes=Vote.object.filter(content_type=content_type.id,object_id=self.id,type_of_vote__in=(UPVOTE,DOWNVOTE),voter=user)

		upvotes=0
		downvotes=0
		for v in votes:
			if v.type_of_vote==UPVOTE:
				upvotes=upvotes+1
			elif v.type_of_vote==DOWNVOTE:
				downvotes=downvotes+1
			else:
				raise Exception('invalid state')
			v.delete()
		self.upvotes=F('upvotes')-upvotes
		self.downvotes=F('downvotes')-downvotes
		self.save(update_field=["upvotes","downvotes"])
	def _vote(self,user,type_of_vote):
		content_type=ContentType.objects.get_for_model(self)
		if self._already_voted(user,content_type,type_of_vote):
			return
		if self._voting_for_myself(user):
			return
		vote=Vote(content_object=self,voter=user,type_of_vote=type_of_vote)
		vote.save()
		if type_of_vote==UPVOTE:
			self.upvotes=F('upvotes')+1
		elif type_of_vote==DOWNVOTE:
			self.downvotes=F('downvotes')+1
		else:
			raise Exception('Invalid type of Vote' + type_of_vote)
		self.save(update_fields=["upvotes","downvotes"])

	def _already_voted(self,user,content_type,type_of_vote):
		return Vote.objects.filter(
			content_type=content_type.id,\
			object_id=self.id,\
			voter=user,type_of_vote=type_of_vote)\
			.exists()

class Post(Votable):
	forum=models.ForeignKey(Forum,related_name='forum_posts',null=True,on_delete=models.PROTECT)
	subforum=models.ForeignKey(SubForum,related_name='subforum_posts',blank=True,null=True,on_delete=models.PROTECT)
	author=models.ForeignKey(User,related_name='posts',on_delete=models.PROTECT)
	created=models.DateTimeField(auto_now_add=True)
	updated=models.DateTimeField(auto_now=True)
	updated_by=models.ForeignKey(User,blank=True,null=True,on_delete=models.PROTECT)
	post_title=models.CharField(max_length=255)
	body=FroalaField(blank=True)
	status=models.IntegerField(choices=(
		(0,'Draft'),
		(1,'Post')
		),default=0)
	views=models.IntegerField(blank=True,default=0)

	def _voting_for_myself(self,user):
		return self.author.id==user.id
	def __str__(self):
		return self.post_title
class Comment(Votable):
	post=models.ForeignKey(Forum,related_name='post_comments',null=True,on_delete=models.PROTECT)
	user=models.ForeignKey(User,related_name='user_comments',null=True,on_delete=models.PROTECT)
	comment_parent=models.ForeignKey('Comment',related_name='comment_reply',blank=True,null=True,on_delete=models.CASCADE)
	body=FroalaField(theme='gray',plugins=('emoticons','image','url'))
	time=models.DateTimeField(auto_now_add=True)

	def _voting_for_myself(self,user):
		return self.user.id==user.id

	def __str__(self):
		return f"{self.user} comments"

	