from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .forms import UserRegistrationForm, LoginForm
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render

from django.views import View
from django.contrib.auth import (
    authenticate, get_user_model, password_validation, login, logout
)
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, login as auth_login,
    logout as auth_logout, update_session_auth_hash,
)
from django.urls import reverse
from tools import message
import tools
User = get_user_model()





class RegistrationView(View):
    form_class = UserRegistrationForm
    initial = {}
    template_name = 'accounts/signup.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')
        form = self.form_class(initial=self.initial)
        data = {'form': form}
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')
        form = self.form_class(request.POST)
        if form.is_valid():
            new_user = form.save()
            new_user.active = False
            new_user.save()
            login(request, new_user)
            return HttpResponseRedirect(reverse('continue_signup'))

        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/')
        logout(request)
        return HttpResponseRedirect(reverse('login'))


class LoginView(View):
    form_class = LoginForm
    initial = {}
    template_name = 'accounts/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')
        form = self.form_class(initial=self.initial)
        data = {'form': form}
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect('/')
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.user_cache
            login(request, user)
            return HttpResponseRedirect(reverse('my_profile'))

        return render(request, self.template_name, {'form': form})
    
class UserView(View):
    form_class = LoginForm
    initial = {}
    template_name = 'accounts/user.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/')
        return render(request, self.template_name)


