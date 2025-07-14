from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required

from .forms import CustomLoginForm

# Vista para la página principal pública o de bienvenida
def home(request):
    if request.user.is_authenticated:
        # Si es administrador o staff, redirige al panel admin
        if request.user.is_superuser or request.user.is_staff:
            return redirect('home:admin')
        # Si es otro usuario, redirige a otra app (ejemplo: exam)
        return redirect('exam:home')
    # Si no está autenticado, muestra página pública
    return render(request, 'home/home.html')

# Vista para el panel de administración
@login_required
def admin(request):
    # Pasa el usuario autenticado para mostrar nombre en plantilla
    return render(request, 'admin/home.html', {'user': request.user})

# Vista personalizada para login con formulario propio
class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = CustomLoginForm
