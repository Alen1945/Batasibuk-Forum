from django import template
from django.utils.safestring import mark_safe
from batasibuk_forum.models import Post,Recommend


register=template.Library()
UPVOTE=1
DOWNVOTE=2

@register.filter(name='is_user_vote_r')
def user_is_vote_r(post,request):

	if request.user.is_authenticated and\
		Recommend.objects.filter(post=post,\
	 	recommender=request.user).exists():
		return 'active'
	else:
		return ''


@register.filter(name='is_user_upvote')
def user_is_upvote(data,request):
	if request.user.is_authenticated:
		v=data.votes.filter(voter=request.user).first()
		if v and v.type_of_vote==UPVOTE:
			return 'active'
	else:
		return ''
@register.filter(name='is_user_downvote')
def user_is_downvote(data,request):
	if request.user.is_authenticated:
		v=data.votes.filter(voter=request.user).first()
		if v and v.type_of_vote==DOWNVOTE:
			return 'active'
	else:
		return ''


@register.simple_tag(name='is_user_follow')
def user_is_follow(to_follow,request,text=''):
	if request.user.is_authenticated and\
		to_follow.followers.filter(follower=request.user).exists():
			if text=='get_text':
				return mark_safe('<i class="fa fa-check-circle-o fa-lg"></i> Follow')
			return 'active'
	else:
		if text=='get_text':
			return 'Follow'
		return ''