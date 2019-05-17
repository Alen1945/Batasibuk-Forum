from django.db import models
from django.contrib.auth.models import User
# Create your models here.

#tipe Room
DIRECT_MESSAGE = 1
GROUP_MESSAGE = 2

#status Pesan
SENDED=1
RECEIVED=2
READ=3
class Room(models.Model):
	name=models.CharField(max_length=100)
	kind=models.IntegerField(choices=(
		(DIRECT_MESSAGE,'Direct Message'),
		(GROUP_MESSAGE,'Group Message')
		))
	def post_messages(self,author,text):
		message=Message()
		message.room=self
		message.text=text
		message.author=author
		message.save()

class RoomMember(models.Model):
	room=models.ForeignKey(Room,related_name='room_members',on_delete=models.CASCADE)
	member=models.ForeignKey(User,on_delete=models.CASCADE)
	status=models.BooleanField(default=True)
class Message(models.Model):
	room=models.ForeignKey(Room,related_name='room_messages',on_delete=models.CASCADE)
	text=models.TextField()
	author=models.ForeignKey(User,on_delete=models.PROTECT)
	timestamp=models.DateTimeField(auto_now_add=True)
	status=models.IntegerField(choices=(
		(SENDED,'Sended'),
		(RECEIVED,'Received'),
		(READ,'Read')
		),default=SENDED)

