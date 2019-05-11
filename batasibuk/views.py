from functools import reduce
import operator
from django.db.models import Q
from django.contrib.auth.models import User
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy,reverse
from batasibuk_forum.models import Post,Forum,SubForum
from account.models import Profile

class Index(ListView):
	model=Post
	template_name='home.html'
	context_object_name='new_threads'
	paginate_by=5
	def get_context_data(self,*args,**kwargs):
		context=super().get_context_data(*args,**kwargs)
		if self.request.user.is_authenticated:
			context['title']='Home'
		else:
			context['title']='Welcome'
		return context
	def get_queryset(self):
		query=super().get_queryset()
		user=self.request.user
		if self.request.user.is_authenticated:
			return query.filter(Q(author=user) | Q(post_forum__followers__follower=user) | Q(post_subforum__followers__follower=user) | Q(author__profile__followers__follower=user)).distinct().order_by('-created')
		else:
			return query.order_by('-created')

class SearchView(ListView):
	template_name='search.html'
	context_object_name='search_result'
	model=Post
	def get_queryset(self):
		search_result=super().get_queryset()
		key=self.request.GET['s']
		if key:
			key_list=key.split()
			search_result={}
			search_result['thread']=Post.objects.filter(
				reduce(operator.and_,
					(Q(post_title__icontains=k) for k in key_list)) |
				reduce(operator.and_,
					(Q(body__icontains=k) for k in key_list)) |
				reduce(operator.and_,
					(Q(author__username__icontains=k) for k in key_list))
				)
			search_result['creator']=Profile.objects.filter(
				reduce(operator.or_,(Q(user__username__icontains=k) for k in key_list))
				)
			search_result['forum']=Forum.objects.filter(
				reduce(operator.or_,(Q(name__icontains=k) for k in key_list))
				)
			search_result['subforum']=SubForum.objects.filter(
				reduce(operator.or_,(Q(name__icontains=k) for k in key_list))
				)

		return search_result

