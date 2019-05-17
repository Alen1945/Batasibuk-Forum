from django.contrib import admin
from .models import Room,RoomMember,Message
# Register your models here.

admin.site.register(Room)
admin.site.register(RoomMember)
admin.site.register(Message)