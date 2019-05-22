import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Notification

def NotifConsumer(AsyncWebsocketConsumer):
	async def connect(self):
		await self.accept()
	async def receive(self,text_data):
		pass

	async def disconnect(self,close_code):
		pass