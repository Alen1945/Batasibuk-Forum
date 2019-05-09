from django.contrib import admin
from .models import Category,Forum,SubForum,Post,Comment,Vote,Follow
# Register your models here.
class AdminCategory(admin.ModelAdmin):
	fields=['name','channel_logo']
class AdminForum(admin.ModelAdmin):
	fields=['category','name','description','moderators','forum_logo']
class AdminPost(admin.ModelAdmin):
	readonly_fields=['post_slug']
	

admin.site.register(Category,AdminCategory)
admin.site.register(Forum,AdminForum)
admin.site.register(Post,AdminPost)
admin.site.register(SubForum)
admin.site.register(Comment)
admin.site.register(Vote)
admin.site.register(Follow)