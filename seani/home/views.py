from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required


from .forms import CustomLoginForm

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or request.user.is_staff:
            return redirect('home:admin')
        return redirect('exam:home')
    return render(request, 'home/home.html')

@login_required
def admin(request):
    return render(request, 'admin/home.html')


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = CustomLoginForm
