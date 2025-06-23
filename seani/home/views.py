from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView

from .forms import CustomLoginForm

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin:index')
        return redirect('exam:home')
    return render(request, 'home/home.html')


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = CustomLoginForm
