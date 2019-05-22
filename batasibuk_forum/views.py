from copy import deepcopy
from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse_lazy,reverse
from django.http import HttpResponse,JsonResponse,HttpResponseNotFound
from django.views.generic import View,CreateView, ListView,DetailView
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from .forms import NewPostForm,NewCommentForm
from .models import (Category,
					SubForum,
					Forum,
					Post,ViewPost,Comment)
# Create your views here.



UPVOTE=1
DOWNVOTE=2

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
	paginate_by=5
	template_name='batasibuk_forum/forum_view.html'
	context_object_name='forum_thread'
	def get_context_data(self,*args,**kwargs):
		context=super().get_context_data(*args,**kwargs)
		context['title']=self.kwargs['name_forum']
		context['detail_forum']=(self.mode,self.kwargs['id_forum'])
		context['this_forum']=Forum.objects.filter(pk=self.kwargs['id_forum']).first()
		if self.mode=='subforum':
			context['this_forum']=SubForum.objects.filter(pk=self.kwargs['id_forum']).first()
		return context
	def get_queryset(self):
		query=super().get_queryset()
		forum_type=ContentType.objects.get_for_model(Forum)
		if self.mode=='subforum':
			forum_type=ContentType.objects.get_for_model(SubForum)
		return query.filter(forum_post_type=forum_type,forum_post_id=self.kwargs['id_forum'],status=1).order_by('-created')


class NewPostView(LoginRequiredMixin,UserPassesTestMixin,View):
	template_name='batasibuk_forum/new_thread.html'
	form_class=NewPostForm()
	mode=None
	context={}
	def get(self,*args,**kwargs):
		if self.mode=='update':
			data_thread=self.thread_update.__dict__
			self.form_class=NewPostForm(initial=data_thread,instance=self.thread_update)
		self.context={
			'title':'New Thread',
			'form':self.form_class
		}
		if kwargs.get('slug_thread',False):
			self.context['title']=f"Update : {self.thread_update.post_title}"
		return render(self.request,self.template_name,self.context)
	def post(self,*args,**kwargs):
		self.form_class=NewPostForm(self.request.POST)
		if kwargs.get('slug_thread',False):
			self.form_class=NewPostForm(self.request.POST,instance=self.thread_update)
		if self.form_class.is_valid():
			thread_post=self.form_class.save(commit=False)
			thread_post.author=self.request.user
			jenis,id_jenis=self.form_class.cleaned_data.get('select_forum').split('-')
			if jenis=='fr':
				f=Forum.objects.get(id=id_jenis)
			elif jenis=='sfr':
				f=SubForum.objects.get(id=id_jenis)
			thread_post.content_forum_post=deepcopy(f)
			if 'post' in self.request.POST:
				thread_post.status=1
			thread_post.save()
		return redirect(reverse('thread',args=(thread_post.post_slug,thread_post.post_title)))
	def test_func(self):
		if self.mode=='update':
			self.thread_update=Post.objects.filter(post_slug=self.kwargs['slug_thread']).first()
			if self.request.user==self.thread_update.author:
				return True
			else:
				return False
		else:
			return True
def record_view(request,slug_thread):
	post=get_object_or_404(Post,post_slug=slug_thread)
	if request.user.is_authenticated:
		if not ViewPost.objects.filter(post=post,session=request.session.session_key,user=request.user).exists():
			view=ViewPost(post=post,ip=request.META['REMOTE_ADDR'],session=request.session.session_key,user=request.user)
			view.save()
	return ViewPost.objects.filter(post=post).count()

class ThreadView(FormMixin,DetailView):
	model=Post
	mode=None
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
		context['comments']=self.object.post_comments.filter(comment_parent=None)
		return context
	def get_queryset(self):
		query=super().get_queryset()
		post=self.model.objects.get(post_slug=self.kwargs['slug_thread'])
		post.views=int(record_view(self.request,self.kwargs['slug_thread']))
		post.save()
		return query.filter(post_slug=self.kwargs['slug_thread'],status=1)

	def post(self,request,*args,**kwargs):
		if self.request.user.is_authenticated:
			form=self.get_form()
			if form.is_valid():
				return self.form_valid(form) 
			else:
				return self.form_invalid(form)
		return redirect(reverse('login')+"?next="+self.request.build_absolute_uri())

	def form_valid(self,form):
		post=self.get_object()
		user=self.request.user
		new_comment=form.save(commit=False)
		new_comment.post=post
		new_comment.user=user
		id_parent_comment=form.cleaned_data['id_parent_comment']
		if id_parent_comment:
			parent=Comment.objects.filter(pk=id_parent_comment).first()
			new_comment.comment_parent=parent

		new_comment.save()
		if self.mode=='ajax':
			if id_parent_comment:
				data_comment={
					'reply':[new_comment]
				}
				data_comment=render(self.request,'batasibuk_forum/reply.html',data_comment)
			else:
				data_comment={
					'all_comment':[new_comment]
				}
				data_comment=render(self.request,'batasibuk_forum/comments.html',data_comment)

			return HttpResponse(data_comment)
		return super().form_valid(form)

def delete_thread(request,post_slug):
	if request.user.is_authenticated:
		thread=get_object_or_404(Post,post_slug=post_slug)
		if request.user==thread.author:
			thread.delete()
			data={
				'delete':1,
				'count-posts':thread.author.posts.all().count()
			}
		else:
			data={
				'delete':0
			}
			raise PermissionDenied()
	else:
		return redirect_login(reverse('login'))

	return JsonResponse(data)

def upvote_post(request,post_slug):
	if request.user.is_authenticated:
		post=get_object_or_404(Post,post_slug=post_slug)
		post.upvote(request.user)
		data={
			'redirect_login':0,
			'upvotes':str(post.upvotes),
			'downvotes':str(post.downvotes),
		}
		if post.vote_self:
			return HttpResponseNotFound()
	else:
		data={
			'redirect_login':1
		}

	if request.is_ajax():
		return JsonResponse(data)
	else:
		return redirect(reverse('thread',args=(post.post_slug,post.post_title)))


def downvote_post(request,post_slug):
	if request.user.is_authenticated:
		post=get_object_or_404(Post,post_slug=post_slug)
		post.downvote(request.user)
		data={
			'redirect_login':0,
			'upvotes':str(post.upvotes),
			'downvotes':str(post.downvotes),
		}
		if post.vote_self:
			return HttpResponseNotFound()
	else:
		data={
			'redirect_login':1
		}

	if request.is_ajax():
		return JsonResponse(data)
	else:
		return redirect(reverse('thread',args=(post.post_slug,post.post_title)))

def upvote_comment(request,comment_id):
	if request.user.is_authenticated:
		comment=get_object_or_404(Comment,pk=comment_id)
		comment.upvote(request.user)
		data={
			'redirect_login':0,
			'upvotes':str(comment.upvotes),
			'downvotes':str(comment.downvotes),
		}
		if comment.vote_self:
			return HttpResponseNotFound()
	else:
		data={
			'redirect_login':1,
		}
	if request.is_ajax():
		return JsonResponse(data)
	else:
		post=comment.post
		return redirect(reverse('thread',args=(post.post_slug,post.post_title)))


def downvote_comment(request,comment_id):
	if request.user.is_authenticated:
		comment=get_object_or_404(Comment,pk=comment_id)
		comment.downvote(request.user)
		data={
			'redirect_login':0,
			'upvotes':str(comment.upvotes),
			'downvotes':str(comment.downvotes)
		}
		if comment.vote_self:
			return HttpResponseNotFound()
	else:
		data={
			'redirect_login':1,
		}
	if request.is_ajax():
		return JsonResponse(data)
	else:
		post=comment.post
		return redirect(reverse('thread',args=(post.post_slug,post.post_title)))

def forum_follow(request,forum_id,forum_type):
	if request.user.is_authenticated:
		if forum_type=='forum':
			forum=get_object_or_404(Forum,pk=forum_id)
		elif forum_type=='subforum':
			forum=get_object_or_404(SubForum,pk=forum_id)
		else:
			return HttpResponseNotFound()

		forum._follow(request.user)
		data={
			'redirect_login':0,
			'sum_follow':forum.sum_follow,
			'follow_state_action':forum.follow_state_action
		}
	else:
		data={
			'redirect_login':1
		}

	if request.is_ajax():
		return JsonResponse(data)
	else:
		return redirect(request.GET.get('next'))

def vote_r(request,post_id):
	if request.user.is_authenticated:
		post=get_object_or_404(Post,pk=post_id)
		action,score=post._vote_r(request.user)
		data={
			'redirect_login':0,
			'action':action,
			'score':score,
		}
	else:
		data={
			'redirect_login':1,
		}
	if request.is_ajax():
		return JsonResponse(data)
	else:
		return redirect(reverse('thread',kwargs={'slug_thread':post.post_slug,'name_thread':post.post_title}))

def get_replys(request,comment_id):
	comment=get_object_or_404(Comment,pk=comment_id)
	reply=comment.comment_reply.all()
	data={
		'reply':reply
	}	
	data=render(request,'batasibuk_forum/reply.html',data)


	return HttpResponse(data)
