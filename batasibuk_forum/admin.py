from django.contrib import admin
from .models import Category,Forum,SubForum,Post
# Register your models here.
class AdminCategory(admin.ModelAdmin):
	fields=['name']
class AdminForum(admin.ModelAdmin):
	fields=['category','name','description','moderators','forum_logo']

admin.site.register(Category,AdminCategory)
admin.site.register(Forum,AdminForum)
admin.site.register(Post)