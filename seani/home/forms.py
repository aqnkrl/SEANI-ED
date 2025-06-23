''' uncomment this import for customize fields '''
#from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    '''
    This form customize the Login Form

    Add class attr for customize styles
    '''
    # username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Usuario'}))
    # password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))
