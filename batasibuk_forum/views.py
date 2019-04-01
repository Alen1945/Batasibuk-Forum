from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import NewPostForm
# Create your views here.




class NewPostView(CreateView):
	form_class=NewPostForm
	extra_context={
		'title':'New Thread'
	}
	template_name='batasibuk_forum/new_post.html'
	success_url=reverse_lazy('home')
	def form_valid(self,form):
		form.instance.author=self.request.user
		if 'post' in self.request.POST:
			form.instance.status=1
		return super().form_valid(form)