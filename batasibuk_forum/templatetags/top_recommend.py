from django import template
from batasibuk_forum.models import Post,Forum
from django.utils.safestring import mark_safe
from django.shortcuts import render


register=template.Library()


@register.inclusion_tag('snippets/post_recommends.html')
def top_recommend():
	posts=Post.objects.get_top_recommend()
	context={
		'posts':posts,
	}
	return context


@register.inclusion_tag('snippets/forum_recommend.html')
def forum_recommend(request):
	forum=Forum.objects.all()

	if request.user.is_authenticated:
		forum=Forum.objects.exclude(followers__follower=request.user)

	for f in forum:
		f.count_followers=f.followers.all().count()
	recommend_forum=sorted(forum,key=lambda c:c.count_followers,reverse=True)
	if len(recommend_forum)>4:
		recommend_forum=recommend_forum[0:4]
	return {'request':request,'forums':recommend_forum}