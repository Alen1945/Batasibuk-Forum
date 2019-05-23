from django.shortcuts import render
from django.contrib.auth.models import User
from django.views.generic import ListView
from account.models import Profile
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Room,RoomMember
# Create your views here.

class ChatRoomView(LoginRequiredMixin,ListView):
	template_name='chat/chatroom.html'
	context_object_name='room_list'

	def get_context_data(self,*args,**kwargs):
		context=super().get_context_data(*args,**kwargs)
		context['title']='Room Chat'
		context['contact']=User.objects.filter(profile__followers__follower=self.request.user,roommember__member=self.request.user).distinct()
		return context
	def get_queryset(self,*args,**kwargs):
		room_list=Room.objects.filter(room_members__member=self.request.user)
		return room_list