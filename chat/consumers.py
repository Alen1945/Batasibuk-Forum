import json
from django.http import JsonResponse
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Room,Message
from asgiref.sync import async_to_sync



def rooms_to_json(data,user):
		result=[]
		for d in data:
			result.append(room_to_json(d,user))
		result=sorted(result,key=lambda r:r['last_msg_time'],reverse=True)
		return result
def room_to_json(data,user):
	another_member=data.room_members.exclude(member=user).first()
	messages=data.room_messages.all()
	for m in messages:
		if m.status==1:
			m.status=2
			m.save()
	count_received=messages.filter(status=2).exclude(author=user).count()
	return {
		'name':another_member.member.username,
		'room_id':data.id,
		'image_url':another_member.member.profile.user_photo.url,
		'last_msg':get_mini_msg(messages.last().text),
		'last_msg_time':str(data.room_messages.all().last().timestamp),
		'count_received':count_received
	}
def get_mini_msg(text):
	max_len=8
	if len(text)>max_len:
		return f'{text[:max_len]}...'
	return text

class RoomConsumer(AsyncWebsocketConsumer):
	async def fetch_room(self,data):
		user=self.scope['user']
		room=Room.objects.filter(room_members__member=user).distinct()
		content={
			'command':'fetch_room',
			'data_room':rooms_to_json(room,user)
		}
		await self.send(text_data=json.dumps(content))
	commands={
		'fetch_room':fetch_room
	}

	def update_room(self,event):
		async_to_sync(self.commands['fetch_room'](self,event['data']))

	async def connect(self):
		user=self.scope['user']
		self.user_room_list=f'room_list_{user.username}'
		await self.channel_layer.group_add(
			 self.user_room_list,
			 self.channel_name,
			)
		await self.accept()
	async def receive(self,text_data):
		data=json.loads(text_data)
		await self.commands[data['command']](self,data)
	async def send_room(self,data):
		await self.channel_layer.group_send(
			self.user_room_list,
			{
				'type':'send_list_room',
				'data':data
			}
			)
	async def send_list_room(self,event):
		data=event['data']
		await self.send(text_data=json.dumps(data))

	async def disconnect(self,message):
		await self.channel_layer.group_discard(
				self.user_room_list,
				self.channel_name
			)

class ChatConsumer(AsyncWebsocketConsumer):
	async def fetch_messages(self,data):
		messages=Message.objects.filter(room=self.room).order_by('-timestamp')[:10]
		count_msg=Message.objects.filter(room=self.room).count()
		all_msg=False
		if 10>=count_msg:
				all_msg=True
		if data.get('kind',False):
			get_from=data.get('num_show',0)
			get_to=get_from+10
			if get_to-1>=count_msg:
				all_msg=True
			messages=Message.objects.filter(room=self.room).order_by('-timestamp')[get_from:get_to]
		content={
			'command':'fetch_message',
			'request_user':self.scope['user'].username,
			'messages':self.messages_to_json(messages),
		}
		if data.get('kind',False):
			content['pre']=True
			content['messages'].reverse()
		if all_msg:
			content['all_msg']=True

		await self.send(text_data=json.dumps(content))

	def messages_to_json(self,messages):
		result=[]
		for m in messages:
			result.append(self.message_to_json(m))
		result.reverse()
		return result
	def message_to_json(self,message):
		if not self.scope['user']==message.author:
			if message.status==2 or message.status==1:
				message.status=3
				message.save()
		return {
			'author':message.author.username,
			'author_image':message.author.profile.user_photo.url,
			'content':message.text,
			'time':str(message.timestamp),
		}
	async def new_message(self,data):
		msg=data['msg']
		user=self.scope['user']
		message=Message.objects.create(room=self.room,author=user,text=msg)
		content={
			'command':data['command'],
			'msg':self.message_to_json(message),
		}

		await self.channel_layer.group_send(
			self.room_name,
			{
				'type':'send_message',
				'content':content
			}
			)
		await self.send_notify_room()
		

	async def send_notify_room(self):
		author=self.scope['user']
		send_to=self.room.room_members.exclude(member=author).first().member
		room_list_name=f'room_list_{send_to.username}'
		data={
			'user':send_to
		}
		await self.channel_layer.group_send(
			room_list_name,{
				'type':'fetch_room',
				'data':"",
				},
			)

	async def send_message(self,event):
		content=event['content']
		await self.send(text_data=json.dumps(content))

	commands={
		'fetch_messages':fetch_messages,
		'new_message':new_message
	}
	async def connect(self):
		user=self.scope['user']
		self.room_id=self.scope['url_route']['kwargs']['pk']
		if not Room.objects.filter(pk=self.room_id).exists() or not Room.objects.filter(pk=self.room_id).first().room_members.filter(member=user).exists():
			await self.accept()
			await self.send(text_data=json.dumps({'close':'true'}))

		self.room=Room.objects.filter(pk=self.room_id).first()
		self.room_name=f'room_{self.room_id}'
		await self.channel_layer.group_add(
			self.room_name,
			self.channel_name,
			)
		await self.accept()

	async def receive(self,text_data):
		data=json.loads(text_data)
		await self.commands[data['command']](self,data)

	async def disconnect(self,close_code):
		await self.channel_layer.group_discard(
			self.room_name,
			self.channel_name
			)


	

