
from django.contrib import admin
from django.urls import path,include
from . import views as home_views
from account.views import AccountRegisterView
from account.forms import AccountLoginForm
from django.contrib.auth import views as auth_views

urlpatterns = [
	path('forum/',include('batasibuk_forum.urls',namespace='forum')),
	path('register/',AccountRegisterView.as_view(),name='register'),
	path('login/',auth_views.LoginView.as_view(template_name='account/login.html',authentication_form=AccountLoginForm),name='login'),
	path('logout',auth_views.LogoutView.as_view(template_name='account/logout.html'),name='logout'),
	path('',home_views.index.as_view(),name='home'),
    path('admin/', admin.site.urls),
    path('froala_editor/',include('froala_editor.urls'))
]
