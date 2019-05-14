# _*_ coding:utf-8 _*_
from django.urls import path
from .views import *

urlpatterns = [  # урлы
    path('logout/', LogoutView.as_view(), name='logout'),
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', RegistrationView.as_view(), name='signup'),
    path('profile/', UserView.as_view(), name='profile'),
]
