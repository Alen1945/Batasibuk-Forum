# from django.db.models.signals import pre_delete
# from django.db.models import ProtectedError
# from django.dispatch import receiver
# from .models import Post,Forum,SubForum

# @receiver(pre_delete,sender=Post)
# def protect_delete(sender,instance,**kwargs):
# 	if instance.forum.exists():
# 		raise ProtectedError('tidak bisa',Forum)
