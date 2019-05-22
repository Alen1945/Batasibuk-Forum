import os
import time
import datetime
import math
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
	def image_path(instance,imagename):
		base_name,ext=os.path.splitext(imagename)
		return f"logo_channel/{time.strftime('%y%m%d%H%M%S')}{ext}"
	name=models.CharField(max_length=80)
	groups=models.ManyToManyField(Group,blank=True)
	position=models.IntegerField(blank=True,default=0)
	channel_logo=models.ImageField(default='',blank=True,upload_to=image_path)

	def __str__(self):
		return self.name

class Vote(models.Model):
	vote_type=models.ForeignKey(ContentType,on_delete=models.PROTECT,related_name='_votes')
	vote_id=models.PositiveIntegerField()
	content_vote=GenericForeignKey('vote_type','vote_id')
	voter=models.ForeignKey(User,on_delete=models.PROTECT)
	type_of_vote=models.IntegerField(choices=(
		(UPVOTE,'Upvote'),
		(DOWNVOTE,'Downvote'),
		))
	submission_time=models.DateTimeField(auto_now_add=True)
class Votable(models.Model):

	class Meta:
		abstract=True
	votes=GenericRelation(Vote,content_type_field='vote_type',object_id_field='vote_id')
	upvotes=models.IntegerField(default=0,blank=True)
	downvotes=models.IntegerField(default=0,blank=True)
	vote_self=False
	def upvote(self,user):
		self._vote(user,UPVOTE)
	def downvote(self,user):
		self._vote(user,DOWNVOTE)
	def undo_vote(self,user,type_of_vote):
		vote_type=ContentType.objects.get_for_model(self)
		vote=Vote.objects.filter(vote_type=vote_type.id,vote_id=self.id,type_of_vote=type_of_vote,voter=user).first()
		vote.delete()
		self.upvotes=int(Vote.objects.filter(vote_type=vote_type.id,vote_id=self.id,type_of_vote=UPVOTE).count())
		self.downvotes=int(Vote.objects.filter(vote_type=vote_type.id,vote_id=self.id,type_of_vote=DOWNVOTE).count())
		self.save(update_fields=["upvotes","downvotes"])
	def change_vote(self,user,type_of_vote):
		vote_type=ContentType.objects.get_for_model(self)
		vote=Vote.objects.get(vote_type=vote_type.id,vote_id=self.id,voter=user)
		vote.type_of_vote=type_of_vote
		vote.save()
		self.upvotes=int(Vote.objects.filter(vote_type=vote_type.id,vote_id=self.id,type_of_vote=UPVOTE).count())
		self.downvotes=int(Vote.objects.filter(vote_type=vote_type.id,vote_id=self.id,type_of_vote=DOWNVOTE).count())
		self.save(update_fields=['upvotes','downvotes'])
	def _vote(self,user,type_of_vote):
		vote_type=ContentType.objects.get_for_model(self)
		if self._already_voted(user,vote_type):
			ready_voted=Vote.objects.filter(vote_type=vote_type.id,vote_id=self.id,voter=user,type_of_vote=type_of_vote)
			if ready_voted:
				return self.undo_vote(user,type_of_vote)
			else:
				return self.change_vote(user,type_of_vote)
		if self._voting_for_myself(user):
			self.vote_self=True
			return
		vote=Vote(content_vote=self,voter=user,type_of_vote=type_of_vote)
		vote.save()
		print(self)
		self.upvotes=int(Vote.objects.filter(vote_type=vote_type.id,vote_id=self.id,type_of_vote=UPVOTE).count())
		self.downvotes=int(Vote.objects.filter(vote_type=vote_type.id,vote_id=self.id,type_of_vote=DOWNVOTE).count())
		self.save(update_fields=["upvotes","downvotes"])

	def _already_voted(self,user,vote_type):
		return Vote.objects.filter(
			vote_type=vote_type.id,\
			vote_id=self.id,\
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

class PostsManager(models.Manager):
	def get_top_recommend(self):
		posts=Post.objects.all()
		for post in posts:
			c_recommends=post.post_recommends.all().count()
			time_since=math.floor((datetime.datetime.now().timestamp()-post.created.timestamp())/3600)
			post.score=(c_recommends)/(time_since+2)**1.8
			if c_recommends==0:
				post.score=(c_recommends-1)/(time_since+2)**1.8
		posts=sorted(posts,key=lambda t:t.score,reverse=True)
		if len(posts)>10:
			return posts[0:7]
		return posts

class Post(Votable):
	objects=PostsManager()
	forum_post_type=models.ForeignKey(ContentType,on_delete=models.PROTECT,related_name='_forum_posts')
	forum_post_id=models.PositiveIntegerField()
	content_forum_post=GenericForeignKey('forum_post_type','forum_post_id')
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

	def _vote_r(self,user):
		if Recommend.objects.filter(post=self,recommender=user).exists():
			Recommend.objects.filter(post=self,recommender=user).delete()
			return ('cancel',Recommend.objects.filter(post=self).count())
		else:
			Recommend.objects.create(post=self,recommender=user)
			return ('vote',Recommend.objects.filter(post=self).count())

class Recommend(models.Model):
	post=models.ForeignKey(Post,related_name='post_recommends',on_delete=models.CASCADE)
	recommender=models.ForeignKey(User,related_name='user_recommends',on_delete=models.CASCADE)
	time=models.DateTimeField(auto_now_add=True)


class ViewPost(models.Model):
	post=models.ForeignKey(Post,related_name='post_views',on_delete=models.CASCADE)
	user=models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True)
	ip=models.CharField(max_length=40)
	session=models.CharField(max_length=40)
	created=models.DateTimeField(default=timezone.now)

class Comment(Votable):
	post=models.ForeignKey(Post,related_name='post_comments',null=True,on_delete=models.CASCADE)
	user=models.ForeignKey(User,related_name='user_comments',null=True,on_delete=models.SET_NULL)
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





# related_name='_followers'
class Follow(models.Model):
	forum_type=models.ForeignKey(ContentType,on_delete=models.PROTECT)
	forum_id=models.PositiveIntegerField()
	content_forum=GenericForeignKey('forum_type','forum_id')
	follower=models.ForeignKey(User,on_delete=models.PROTECT)
	time=models.DateTimeField(auto_now=True)


class Followble(models.Model):
	class Meta:
		abstract=True
	followers=GenericRelation(Follow,content_type_field='forum_type',object_id_field='forum_id')
	def _following_self(self,user):
		return False
	def _already_follow(self,user,forum_type):
		return Follow.objects.filter(forum_type=forum_type.id,forum_id=self.id,follower=user).exists()
	def _unfollow(self,user,forum_type):
		follow=Follow.objects.filter(forum_type=forum_type.id,forum_id=self.id,follower=user).first()
		follow.delete()
		self.sum_follow=self.followers.all().count()
		self.follow_state_action='Follow'
	def _follow(self,user):
		self.follow_self=False
		self.sum_follow=self.followers.all().count()
		self.follow_state_action=''
		forum_type=ContentType.objects.get_for_model(self)
		if self._already_follow(user,forum_type):
			return self._unfollow(user,forum_type)
		if self._following_self(user):
			self.follow_self=True
			return
		follow=Follow(content_forum=self,follower=user)
		follow.save()
		self.sum_follow=self.followers.all().count()
		self.follow_state_action='<i class="fa fa-check-circle-o fa-lg"></i> Follow'
class Forum(Followble):
	def image_path(instance,imagename):
		base_name,ext=os.path.splitext(imagename)
		return f"logo_image/{time.strftime('%y%m%d%H%M%S')}{ext}"
	category=models.ForeignKey(Category,related_name='forums',blank=True,null=True,on_delete=models.PROTECT)
	name=models.CharField(max_length=80)
	position=models.IntegerField(blank=True,default=0)
	description=models.TextField(blank=True,default='')
	moderators=models.ManyToManyField(User,blank=True)
	updated=models.DateTimeField(auto_now=True)
	posts=GenericRelation(Post,content_type_field='forum_post_type',object_id_field='forum_post_id',related_query_name='post_forum')
	post_count=models.IntegerField(blank=True,default=0)
	forum_logo=models.ImageField(default='',upload_to=image_path)

	def __str__(self):
		return self.name

class SubForum(Followble):
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
	posts=GenericRelation(Post,content_type_field='forum_post_type',object_id_field='forum_post_id',related_query_name='post_subforum')
	post_count=models.IntegerField(blank=True,default=0)
	forum_logo=models.ImageField(default='',upload_to=image_path)


	def __str__(self):
		return self.name


