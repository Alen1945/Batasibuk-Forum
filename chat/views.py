from django.shortcuts import render
from django.views.generic import ListView
from account.models import Profile
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Room
# Create your views here.

class ChatRoomView(LoginRequiredMixin,ListView):
	template_name='chat/chatroom.html'
	context_object_name='room_list'

	def get_context_data(self,*args,**kwargs):
		context=super().get_context_data(*args,**kwargs)
		context['title']='Room Chat'
		context['contact']=Profile.objects.filter(followers__follower=self.request.user)
		return context
	def get_queryset(self,*args,**kwargs):
		room_list=Room.objects.filter(room_members__member=self.request.user)
		return room_list