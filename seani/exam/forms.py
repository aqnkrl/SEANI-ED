from django import forms
from career.models import Career
from .models import Stage

class CandidateForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=150)
    username = forms.CharField(max_length=100)
    email = forms.EmailField()
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)
    stage = forms.ModelChoiceField(queryset=Stage.objects.all())
    career = forms.ModelChoiceField(queryset=Career.objects.all())

class LoadCSVForm(forms.Form):
    file = forms.FileField()
    stage = forms.ModelChoiceField(queryset=Stage.objects.all())

class StageForm(forms.Form):
    stage = forms.ModelChoiceField(
        queryset=Stage.objects.all(),
        label="Selecciona una etapa",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    career = forms.ModelChoiceField(
        queryset=Career.objects.all(),
        required=False,
        label="Filtrar por carrera",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

# FORMULARIO PARA AGREGAR ETAPA
class AddStageForm(forms.ModelForm):
    class Meta:
        model = Stage
        fields = ['stage', 'application_date']
        widgets = {
            'stage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,  
                'step': 1,
                'placeholder': 'Número de etapa'
            }),
            'application_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Fecha de aplicación'
            }),
        }
        labels = {
            'stage': 'Número de Etapa',
            'application_date': 'Fecha de Aplicación',
        }
