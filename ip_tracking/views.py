# ip_tracking/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django_ratelimit.decorators import ratelimit
from .middlewares import *

@ratelimit(key=key_for_user, rate=rate_for_user, method='POST', block=True)
def login_view(request):

    # Check if user is already limited
    # HTTP 429 Too Many Requests
    if getattr(request, 'limited', False):
        return HttpResponse("Too many login attempts. Try again later.", status=429)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return HttpResponse("Invalid credentials", status=401)
    return render(request, 'login.html')
