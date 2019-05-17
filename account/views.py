import math
from django.shortcuts import render, get_object_or_404,redirect
from django.urls import reverse_lazy,reverse
from django.http import JsonResponse,HttpResponseNotFound,HttpResponse
from .forms import AccountRegisterForm,AccountProfileUpdate
from django.views.generic import CreateView,ListView
from django.views.generic.edit import FormMixin
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from .models import Profile
from batasibuk_forum.models import Post


# edit image
from PIL import Image,ImageSequence



def resize_image(path,x,y,w,h,jenis='p'):
	image=Image.open(path)
	resize_to=(120,120)
	if jenis=='h':
		resize_to=(500,175)
	width,height=image.size
	to_right=w+x
	to_bottom=h+y
	if to_right>width:
		to_right=width
	if to_bottom>height:
		to_bottom=height

	n_frames=getattr(image,'n_frames',1)
	print(n_frames)
	if n_frames>1:
		frames=[]
		for frame in ImageSequence.Iterator(image):
			resized_frame=(frame.crop((x, y,to_right, to_bottom))).resize(resize_to,Image.ANTIALIAS)
			frames.append(resized_frame)
		return frames[0].save(path,optimize=True,save_all=True,append_images=frames[1:])

	cropped_image=image.crop((x, y,to_right, to_bottom))
	resized_image=cropped_image.resize(resize_to,Image.ANTIALIAS)
	return resized_image.save(path)
	

class AccountCreate(CreateView):
	template_name='account/register.html'
	form_class=AccountRegisterForm
	success_url=reverse_lazy('login')
	extra_context={
		'title':'Register',
	}

	
	def create_profile(self,form):

		user=form.save(commit=False)

		x_p=form.cleaned_data['x_p']
		y_p=form.cleaned_data['y_p']
		w_p=form.cleaned_data['width_p']
		h_p=form.cleaned_data['height_p']

		info=form.cleaned_data['info']
		gender=form.cleaned_data['gender']
		date_of_birth=form.cleaned_data['date_of_birth']
		location=form.cleaned_data['location']
		website=form.cleaned_data['website']
		user_photo=form.cleaned_data['user_photo']
		user.save()

		new_profile=Profile()
		new_profile.user=user
		new_profile.info=info
		new_profile.date_of_birth=date_of_birth
		new_profile.location=location
		new_profile.website=website
		if user_photo:
			new_profile.user_photo=user_photo
		new_profile.save()

		if(type(x_p)!=type(None) and type(y_p)!=type(None) and type(w_p)!=type(None) and type(h_p)!=type(None)):
			resize_image(user.profile.user_photo.path,image_p,x_p,y_p,w_p,h_p)
			
				
	def form_valid(self,form):
		self.create_profile(form)
		return super().form_valid(form)



class ProfileView(LoginRequiredMixin,UserPassesTestMixin,FormMixin,ListView):
	model=Post
	context_object_name='user_thread'
	template_name='account/profile.html'
	form_class=AccountProfileUpdate
	paginate_by=5
	
	def get_success_url(self):
		return reverse('profile',kwargs={'user_username':self.request.user.username})
	def get_context_data(self,*args,**kwargs):
		context=super().get_context_data(*args,**kwargs)
		context['title']=self.request.user.username
		context['form']=AccountProfileUpdate(instance=self.request.user.profile)
		return context
	def get_queryset(self):
		query=super().get_queryset()
		return query.filter(author=self.request.user).order_by('-created')

	def post(self,request,*arg,**kwargs):
		form=AccountProfileUpdate(data=request.POST,files=request.FILES,instance=request.user.profile)
		if form.is_valid():
			return self.form_valid(form)
		else:
			return self.form_invalid(form)
	def update_profil(self,form):
		profile=form.save(commit=False)
		x_p=form.cleaned_data['x_p']
		y_p=form.cleaned_data['y_p']
		w_p=form.cleaned_data['w_p']
		h_p=form.cleaned_data['w_p']

		x_h=form.cleaned_data['x_h']
		y_h=form.cleaned_data['y_h']
		w_h=form.cleaned_data['w_h']
		h_h=form.cleaned_data['w_h']
		profile.save()

		if(type(x_p)!=type(None) and type(y_p)!=type(None) and type(w_p)!=type(None) and type(h_p)!=type(None)):
			resize_image(profile.user_photo.path,x_p,y_p,w_p,h_p)

		if(type(x_h)!=type(None) and type(y_h)!=type(None) and type(w_h)!=type(None) and type(h_h)!=type(None)):
			resize_image(profile.user_header.path,x_h,y_h,w_h,h_h,'h')

	def form_valid(self,form):
		self.update_profil(form)
		return super().form_valid(form)

	def test_func(self):
		this_user=User.objects.filter(username=self.kwargs['user_username']).first()
		if self.request.user.is_authenticated and self.request.user==this_user:
			return True
		return False
		
	def dispatch(self,request,*args,**kwargs):
		if not self.test_func():
			return redirect(reverse('creator',kwargs={'user_username':self.kwargs['user_username']}))
		return super().dispatch(request,*args,**kwargs)
class CreatorView(ListView):
	model=Post
	context_object_name='user_thread'
	template_name='account/creator.html'
	paginate_by=5
	

	def get(self,*args,**kwargs):
		this_user=User.objects.filter(username=self.kwargs['user_username']).first()
		if self.request.user.is_authenticated and self.request.user==this_user:
			return redirect(reverse('profile',kwargs={'user_username':self.kwargs['user_username']}))
		return super().get(*args,*kwargs)
	def get_context_data(self,*args,**kwargs):
		context=super().get_context_data(*args,**kwargs)
		context['title']=self.kwargs['user_username']
		context['this_user']=User.objects.filter(username=self.kwargs['user_username']).first()
		return context
	def get_queryset(self):
		query=super().get_queryset()
		this_author=User.objects.filter(username=self.kwargs['user_username']).first()
		return query.filter(author=this_author)





def account_follow(request,user_id):
	if request.user.is_authenticated:
		user=get_object_or_404(User,pk=user_id)
		user_profile=get_object_or_404(Profile,user=user)
		user_profile._follow(request.user)
		data={
			'redirect_login':0,
			'sum_follow':user_profile.sum_follow,
			'follow_state_action':user_profile.follow_state_action
		}
		if user_profile.follow_self:
			return HttpResponseNotFound()
	else:
		data={
			'redirect_login':1
		}

	if request.is_ajax():
		return JsonResponse(data)
	else:
		return redirect(request.GET.get('next'))


