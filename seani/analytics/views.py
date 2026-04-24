from django.shortcuts import render
from django.db.models import Avg
from exam.models import Exam, Stage
from career.models import Career
import numpy as np

def analitica_view(request):
    # Diccionario con las 8 ED y sus aplicaciones específicas en SEANI
    ed_models = {
        'separables': {
            'titulo': 'Variables Separables', 
            'desc': 'Modelado de la Ley del Olvido: Predice la pérdida de información del aspirante conforme pasa el tiempo sin repaso.', 
            'meta': 'Olvido'
        },
        'homogeneas': {
            'titulo': 'ED Homogéneas', 
            'desc': 'Proyección de Nivelación: Compara el puntaje del alumno con el promedio grupal para estimar el tiempo de regularización.', 
            'meta': 'Nivelación'
        },
        'exactas': {
            'titulo': 'ED Exactas', 
            'desc': 'Consistencia de Esfuerzo: Analiza si el flujo de aprendizaje es constante o si hay fugas de atención durante el examen.', 
            'meta': 'Esfuerzo'
        },
        'factor': {
            'titulo': 'Factor Integrante', 
            'desc': 'Factores Externos: Mide cómo variables como el estrés o el ruido afectan la curva de retención de datos.', 
            'meta': 'Impacto'
        },
        'lineales': {
            'titulo': 'ED Lineales', 
            'desc': 'Crecimiento Acumulativo: Modela el incremento directo del conocimiento base por cada módulo de estudio completado.', 
            'meta': 'Crecimiento'
        },
        'variacion': {
            'titulo': 'Variación de Parámetros', 
            'desc': 'Respuesta a Estímulos: Evalúa la reacción del alumno ante cambios en la dificultad de las preguntas (estímulos de examen).', 
            'meta': 'Respuesta'
        },
        'bernoulli': {
            'titulo': 'Bernoulli', 
            'desc': 'Saturación Cognitiva: Identifica el punto donde el alumno deja de aprender eficientemente debido al cansancio mental.', 
            'meta': 'Saturación'
        },
        'laplace': {
            'titulo': 'Laplace', 
            'desc': 'Análisis de Impulso: Mide el impacto inmediato de eventos discretos, como un curso propedéutico intensivo.', 
            'meta': 'Impulso'
        },
    }
    return render(request, 'analytics/dashboard.html', {'ed_models': ed_models})

def graficar_view(request, modelo):
    # --- DATOS PARA FILTROS (Se mantiene igual) ---
    years = Stage.objects.dates('application_date', 'year').distinct()
    stages = Stage.objects.values_list('stage', flat=True).distinct().order_by('stage')
    careers = Career.objects.all()

    selected_year = request.GET.get('year')
    selected_stage = request.GET.get('stage')
    selected_career = request.GET.get('career')

    etapas_obj = Stage.objects.all().order_by('stage')
    if selected_stage:
        etapas_obj = etapas_obj.filter(stage=selected_stage)

    chart_labels = [f"Etapa {e.stage}" for e in etapas_obj]
    datasets = []
    colores = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF']

    carreras_to_plot = careers
    if selected_career:
        carreras_to_plot = careers.filter(id=selected_career)

    for i, career in enumerate(carreras_to_plot):
        data_puntos = []
        for stage in etapas_obj:
            examenes = Exam.objects.filter(career=career, stage=stage)
            if selected_year:
                examenes = examenes.filter(created__year=selected_year)
            promedio = examenes.aggregate(Avg('score'))['score__avg'] or 0
            data_puntos.append(round(float(promedio), 2))
        
        datasets.append({
            'label': career.name,
            'data': data_puntos,
            'backgroundColor': colores[i % len(colores)],
            'borderWidth': 1,
            'type': 'bar'
        })

    # --- LÓGICA DE PREDICCIÓN SEGÚN LA DESCRIPCIÓN DE LA ED ---
# --- LÓGICA DE PREDICCIÓN SEGÚN LA DESCRIPCIÓN DE LA ED ---
    # Obtenemos un promedio inicial real basado en los datos existentes
    promedio_gral = Exam.objects.all().aggregate(Avg('score'))['score__avg'] or 5
    y0 = float(promedio_gral)
    t = np.arange(len(chart_labels))
    
    # Mapeo de fórmulas matemáticas a las descripciones del sistema SEANI
    if modelo == 'separables':
        # Ley del Olvido (Decaimiento Exponencial): y = y0 * e^-kt
        # Representa la pérdida de información por falta de repaso
        y_teorico = y0 * np.exp(-0.15 * t)
        desc_grafica = "Predicción: Pérdida de retención por falta de repaso"
        
    elif modelo == 'homogeneas':
        # Nivelación Académica (Crecimiento hacia el límite):
        # Compara el puntaje del alumno para estimar tiempo de regularización
        y_teorico = y0 + (8.5 - y0) * (1 - np.exp(-0.5 * t))
        desc_grafica = "Predicción: Tiempo estimado para alcanzar nivel óptimo"

    elif modelo == 'exactas':
        # Consistencia de Esfuerzo (ED Exactas):
        # Analiza si el flujo de aprendizaje es constante (oscilación mínima de control)
        y_teorico = [y0 + (0.2 if i % 2 == 0 else -0.2) for i in t]
        desc_grafica = "Análisis: Estabilidad del flujo de aprendizaje (Consistencia)"

    elif modelo == 'factor':
        # Factores Externos (Impacto):
        # Mide cómo el ruido o estrés afectan la retención (perturbación de la curva)
        y_teorico = y0 - (1.2 * np.sin(t)) 
        desc_grafica = "Impacto: Sensibilidad a factores de estrés y ruido"

    elif modelo == 'lineales':
        # Crecimiento Acumulativo: Incremento directo por módulo completado
        # Modelo lineal y = mt + b
        y_teorico = y0 + (0.5 * t)
        desc_grafica = "Crecimiento: Incremento de conocimiento base acumulado"

    elif modelo == 'variacion':
        # Respuesta a Estímulos: Reacción ante cambios en dificultad
        # Representado por picos de ajuste en la curva
        y_teorico = [y0 + (1.0 if i % 3 == 0 else -0.5) for i in t]
        desc_grafica = "Respuesta: Reacción ante la dificultad de los reactivos"

    elif modelo == 'bernoulli':
        # Saturación Cognitiva: Sigmoide que identifica el estancamiento por cansancio
        L = 9.0  # Techo cognitivo
        y_teorico = L / (1 + ((L - y0) / y0) * np.exp(-0.7 * t))
        desc_grafica = "Saturación: Límite de aprendizaje por cansancio mental"

    elif modelo == 'laplace':
        # Análisis de Impulso (Función Escalón):
        # Mide el impacto inmediato de un evento discreto como un curso intensivo
        y_teorico = [y0 if val < 2 else min(y0 + 2.5, 10) for val in t]
        desc_grafica = "Impulso: Efecto de curso propedéutico intensivo"

    else:
        y_teorico = [y0] * len(t)
        desc_grafica = "Modelo de Referencia Estándar"

 # ... (todo el código anterior de las fórmulas se mantiene igual)

    # Asegurar que los valores no salgan del rango 0-10
    y_teorico = [max(0, min(10, round(float(v), 2))) for v in y_teorico]

    datasets.append({
        'label': desc_grafica,
        'data': y_teorico,
        'borderColor': '#198754', 
        'type': 'line',
        'fill': False,
        'borderDash': [5, 5], 
        'borderWidth': 4,
        'tension': 0.4,        # <--- Esencial para la curva
        'lineTension': 0.4,    # <--- Agrega esto también por compatibilidad con versiones viejas
        'pointRadius': 5,
    })

    context = {
        'modelo': modelo.upper(),
        'years': years,
        'stages': stages,
        'careers': careers,
        'selected_year': selected_year,
        'selected_stage': selected_stage,
        'selected_career': selected_career,
        'chart_labels': chart_labels,
        'chart_data': datasets,
    }
    return render(request, 'analytics/grafica_detalle.html', context)