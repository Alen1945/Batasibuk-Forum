from django.shortcuts import render
from django.urls import reverse_lazy
from .forms import AccountRegisterForm
from django.views.generic import CreateView
# Create your views here.

class AccountRegisterView(CreateView):
	form_class=AccountRegisterForm
	success_url=reverse_lazy('login')
	extra_context={
		'title':'Register'
	}
	template_name='account/register.html'
	