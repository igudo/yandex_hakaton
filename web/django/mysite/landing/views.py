from django.shortcuts import render
from tools import email_send


def index(request):
    data = {}
    return render(request, 'landing/index.html', data)
