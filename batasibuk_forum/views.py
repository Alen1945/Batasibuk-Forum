from django.shortcuts import render,get_object_or_404
from django.urls import reverse_lazy,reverse
from django.http import HttpResponse,JsonResponse,HttpResponseNotFound
from django.views.generic import CreateView, ListView,DetailView
from django.views.generic.edit import FormMixin
from .forms import NewPostForm,NewCommentForm
from .models import (Category,
					SubForum,
					Forum,
					Post,ViewPost)
# Create your views here.



UPVOTE=1
DOWNVOTE=2


class NewPostView(CreateView):
	form_class=NewPostForm
	extra_context={
		'title':'New Thread'
	}
	template_name='batasibuk_forum/new_thread.html'
	success_url=reverse_lazy('home')
	def form_valid(self,form):
		form.instance.author=self.request.user
		jenis,id_jenis=form.cleaned_data.get('select_forum').split('-')
		if jenis=='fr':
			forum=Forum.objects.get(id=id_jenis)
		elif jenis=='sfr':
			subforum=SubForum.objects.get(id=id_jenis)
			forum=subforum.forum
		form.instance.forum=forum
		if 'subforum' in locals():
			form.instance.subforum=subforum
		if 'post' in self.request.POST:
			form.instance.status=1
		post=form.save()
		if 'post' in self.request.POST:
			if 'subforum' in locals():
				subforum.last_post=post
				subforum.save()
			forum.last_post=post
			forum.save()
		return super().form_valid(form)
class HomeForumsView(ListView):
	model= Category
	template_name='batasibuk_forum/home.html'
	context_object_name='categorys'
	extra_context={
		'title':'forum'
	}
class ChannelView(ListView):
	model=Forum
	template_name='batasibuk_forum/channel_view.html'
	context_object_name='channel_forums'
	def get_context_data(self,*args,**kwargs):
		context=super().get_context_data(*args,**kwargs)
		context['title']=self.kwargs['name_channel']
		return context
	def get_queryset(self):
		query=super().get_queryset()
		category=Category.objects.get(id=self.kwargs['id_channel'])
		return query.filter(category=category)

class ForumView(ListView):
	model=Post
	mode=None
	template_name='batasibuk_forum/forum_view.html'
	context_object_name='forum_thread'
	def get_context_data(self,*args,**kwargs):
		context=super().get_context_data(*args,**kwargs)
		context['title']=self.kwargs['name_forum']
		return context
	def get_queryset(self):
		query=super().get_queryset()
		forum=Forum.objects.get(id=self.kwargs['id_forum'])
		if self.mode=='subforum':
			subforum=SubForum.objects.get(id=self.kwargs['id_forum'])
			return query.filter(subforum=subforum,status=1)
		return query.filter(forum=forum,status=1,subforum=None)


def record_view(request,slug_thread):
	post=get_object_or_404(Post,post_slug=slug_thread)
	if not ViewPost.objects.filter(post=post,session=request.session.session_key):
		view=ViewPost(post=post,ip=request.META['REMOTE_ADDR'],session=request.session.session_key)
		view.save()
	return ViewPost.objects.filter(post=post).count()

def this_user_vote(data,user):
	v=data.votes.filter(type_of_vote__in=(UPVOTE,DOWNVOTE),voter=user).first()
	if v and v.type_of_vote==UPVOTE:
		data.user_up_vote=True
	elif v and v.type_of_vote==DOWNVOTE:
		data.user_down_vote=True
class ThreadView(FormMixin,DetailView):
	model=Post
	template_name='batasibuk_forum/thread_view.html'
	context_object_name='thread'
	slug_url_kwarg='slug_thread'
	slug_field='post_slug'
	form_class=NewCommentForm

	def get_success_url(self):
		return reverse('thread',kwargs={'slug_thread':self.kwargs['slug_thread'],'name_thread':self.kwargs['name_thread']})
	def get_context_data(self,*args,**kwargs):
		context=super().get_context_data(*args,**kwargs)
		context['title']=self.kwargs['name_thread']
		context['forms_comment']=NewCommentForm()
		context['comments']=self.object.post_comments.filter(comment_parent=None).order_by('-time')
		for c in context['comments']:
			this_user_vote(c,self.request.user)
			c.replys=c.comment_reply.all()
			if c.replys:
				for reply in c.replys:
					this_user_vote(reply,self.request.user)
		this_user_vote(self.object,self.request.user)
		return context
	def get_queryset(self):
		query=super().get_queryset()
		post=self.model.objects.get(post_slug=self.kwargs['slug_thread'])
		post.views=int(record_view(self.request,self.kwargs['slug_thread']))
		post.save()
		return query.filter(post_slug=self.kwargs['slug_thread'])

	def post(self,request,*args,**kwargs):
		form=self.get_form()
		if form.is_valid():
			return self.form_valid(form) 
		else:
			return self.form_invalid(form)

	def form_valid(self,form):
		post=self.get_object()
		user=self.request.user
		
		new_comment=form.save(commit=False)
		new_comment.post=post
		new_comment.user=user
		new_comment.save()
		return super().form_valid(new_comment)





def upvote_post(request,post_slug):
	post=get_object_or_404(Post,post_slug=post_slug)
	post.upvote(request.user)
	data={
		'cancel':'down',
		'upvotes':str(post.upvotes),
		'downvotes':str(post.downvotes),
	}
	if post.vote_self:
		return HttpResponseNotFound()
	return JsonResponse(data)

def downvote_post(request,post_slug):
	post=get_object_or_404(Post,post_slug=post_slug)
	post.downvote(request.user)
	data={
		'cancel':'up',
		'upvotes':str(post.upvotes),
		'downvotes':str(post.downvotes),
	}
	if post.vote_self:
		return HttpResponseNotFound()
	return JsonResponse(data)
