
from django.urls import path
from .views import NewPostView

app_name='batasibuk_forum'

urlpatterns=[
	path('newthread/',NewPostView.as_view(),name='newthread'),
]