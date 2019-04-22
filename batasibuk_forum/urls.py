
from django.urls import path
from .views import (NewPostView,
				   HomeForumsView,
				   ForumView,
				   ThreadView,
				   )

app_name='batasibuk_forum'

urlpatterns=[
	path('',HomeForumsView.as_view(),name='home'),
	path('fr-<int:id_forum>/<str:name_forum>/',ForumView.as_view(mode='forum'),name='forumview'),
	path('sfr-<int:id_forum>/<str:name_forum>/',ForumView.as_view(mode='subforum'),name='subforumview'),
	path('newthread/',NewPostView.as_view(),name='newthread'),
]