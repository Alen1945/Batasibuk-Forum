
from django.contrib import admin
from django.urls import path,include
from . import views as home_views
from account.views import AccountCreate,ProfileView,CreatorView
from account.forms import AccountLoginForm
from account import views as account_views
from batasibuk_forum.views import ChannelView,ThreadView
from batasibuk_forum import views as forum_views
from chat.views import ChatRoomView
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
	path('chat/',ChatRoomView.as_view(),name='chat'),
	path('search/',home_views.SearchView.as_view(),name='search'),
	path('',home_views.Index.as_view(),name='home'),
	path('thread/<slug:slug_thread>/<str:name_thread>/',ThreadView.as_view(),name='thread'),
	path('ajax/thread/<slug:slug_thread>/<str:name_thread>/',ThreadView.as_view(mode='ajax'),name='ajaxthread'),
	path('channel/<int:id_channel>/<str:name_channel>/',ChannelView.as_view(),name='channel'),
	path('forum/',include('batasibuk_forum.urls',namespace='forum')),
	path('register/',AccountCreate.as_view(),name='register'),
	path('login',auth_views.LoginView.as_view(template_name='account/login.html',authentication_form=AccountLoginForm),name='login'),
	path('profile/<user_username>',ProfileView.as_view(),name='profile'),
	path('creator/<user_username>',CreatorView.as_view(),name='creator'),
	path('logout',auth_views.LogoutView.as_view(),name='logout'),
	path('api/posts/<post_slug>/delete',forum_views.delete_thread,name='delete'),
	path('api/posts/<post_id>/vote_r',forum_views.vote_r,name='vote_r'),
	path('api/posts/<post_slug>/upvote',forum_views.upvote_post,name='upvote_post'),
	path('api/posts/<post_slug>/downvote',forum_views.downvote_post,name='downvote_post'),
	path('api/comments/<comment_id>/upvote',forum_views.upvote_comment,name='upvote_comment'),
	path('api/comments/<comment_id>/downvote',forum_views.downvote_comment,name='downvote_comment'),
	path('api/follow/<user_id>/user',account_views.account_follow,name='follow_user'),
	path('api/follow/<forum_id>/<forum_type>',forum_views.forum_follow,name='follow_forum'),
	path('api/get_replys/<comment_id>',forum_views.get_replys,name='get_replys'),
    path('admin/', admin.site.urls),
    path('ckeditor/',include('ckeditor_uploader.urls'))
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)