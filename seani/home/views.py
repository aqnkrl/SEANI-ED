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
    if not request.user.is_superuser:
        return redirect('home')

    modulos = [
        {
            'id': 1,
            'nombre': 'Comprensión lectora',
            'svg': '''
                <svg class="mod-svg lectura" viewBox="0 0 64 64" stroke="currentColor" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect x="12" y="16" width="40" height="32" rx="4" ry="4"/>
                  <line x1="20" y1="24" x2="44" y2="24"/>
                  <line x1="20" y1="32" x2="44" y2="32"/>
                  <line x1="20" y1="40" x2="36" y2="40"/>
                </svg>
            '''
        },
        {
            'id': 2,
            'nombre': 'Estructura de la lengua',
            'svg': '''
                <svg class="mod-svg lengua" viewBox="0 0 64 64" stroke="currentColor" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M16 32c0-8 8-16 16-16s16 8 16 16-8 16-16 16-16-8-16-16z"/>
                  <path d="M24 32c0 4 4 8 8 8s8-4 8-8"/>
                </svg>
            '''
        },
        {
            'id': 3,
            'nombre': 'Pensamiento matemático',
            'svg': '''
                <svg class="mod-svg matematico" viewBox="0 0 64 64" stroke="currentColor" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <text x="10" y="28" font-size="24">+</text>
                  <text x="30" y="28" font-size="24">−</text>
                  <text x="10" y="54" font-size="24">×</text>
                  <text x="30" y="54" font-size="24">÷</text>
                </svg>
            '''
        },
        {
            'id': 4,
            'nombre': 'Pensamiento analítico',
            'svg': '''
                <svg class="mod-svg analitico" viewBox="0 0 64 64" stroke="currentColor" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="32" cy="32" r="20"/>
                  <path d="M32 20v24M20 32h24"/>
                </svg>
            '''
        }
    ]

    return render(request, 'admin/home.html', {
        'modulos': modulos,
        'user': request.user
    })


# Vista personalizada para login con formulario propio
class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = CustomLoginForm
