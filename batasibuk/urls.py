
from django.contrib import admin
from django.urls import path,include
from . import views as home_views
from account.views import AccountRegisterView
from account.forms import AccountLoginForm
from batasibuk_forum.views import ChannelView,ThreadView
from batasibuk_forum import views as forum_views
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
	path('thread/<slug:slug_thread>/<str:name_thread>/',ThreadView.as_view(),name='thread'),
	path('channel/<int:id_channel>/<str:name_channel>/',ChannelView.as_view(),name='channel'),
	path('forum/',include('batasibuk_forum.urls',namespace='forum')),
	path('register/',AccountRegisterView.as_view(),name='register'),
	path('login/',auth_views.LoginView.as_view(template_name='account/login.html',authentication_form=AccountLoginForm),name='login'),
	path('logout',auth_views.LogoutView.as_view(template_name='account/logout.html'),name='logout'),
	path('',home_views.index.as_view(),name='home'),
	path('api/posts/<post_slug>/upvote',forum_views.upvote_post,name='upvote_post'),
	path('api/posts/<post_slug>/downvote',forum_views.downvote_post,name='downvote_post'),
    path('admin/', admin.site.urls),
    path('ckeditor/',include('ckeditor_uploader.urls'))
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)