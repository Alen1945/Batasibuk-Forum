import asyncio
from django.db.models.signals import post_save
from .models import Room,Message
from django.dispatch import receiver
from .consumers import rooms_to_json,room_to_json
from channels.layers import get_channel_layer
from asgiref.sync import AsyncToSync





	
# @receiver(post_save,sender=Message)
# def send_notify_msg(sender,instance,created,**kwargs):
# 	if created:
# 		channel_layer=get_channel_layer()
# 		author=instance.author
# 		room=instance.room
# 		send_to=room.room_members.exclude(member=author).first().member
# 		room_list_name=f'room_list_{send_to.username}'
# 		data={
# 			'user':send_to
# 		}
# 		AsyncToSync(channel_layer.group_send)(
# 			room_list_name,{
# 				'type':'fetch_room',
# 				'data':author,
# 				}
# 			)