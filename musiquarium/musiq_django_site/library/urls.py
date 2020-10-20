from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'), # initial site redirect to index
    path('index', views.index, name='index'),
    path('profile', views.profile, name='profile'),
    path('table', views.table, name='table'),
    path('login_user', views.login_user, name='login_user'),
    path('register', views.register, name='register'),
    path('logout', views.logout, name='login')
]
