from django.shortcuts import render
from django.db.models import Avg
from exam.models import Exam, Stage
from career.models import Career
import numpy as np
from .logic import SEANIEngine

# Metadatos de cada modelo (para el dashboard y la vista de detalle)
ED_MODELS = {
    'separables': {
        'titulo':     'Variables Separables',
        'desc':       'Ley del Olvido: Predice la pérdida de información del aspirante '
                      'conforme pasa el tiempo sin repaso. (dy/dt = -k·y)',
        'meta':       'Olvido',
        'color':      'azul',
        'params_def': {'k': 0.15},
        'params_info': [
            {'name': 'k', 'label': 'Tasa de olvido (k)', 'min': 0.01, 'max': 1.0,
             'step': 0.01, 'default': 0.15, 'help': 'Velocidad de pérdida de conocimiento'},
        ],
    },
    'homogeneas': {
        'titulo':     'ED Homogéneas',
        'desc':       'Nivelación Académica: Proyecta cuántas etapas tarda un aspirante '
                      'en converger al promedio grupal. (dy/dt = y/t + c)',
        'meta':       'Nivelación',
        'color':      'amarillo',
        'params_def': {'c': 0.5},
        'params_info': [
            {'name': 'c', 'label': 'Constante de convergencia (c)', 'min': 0.1, 'max': 2.0,
             'step': 0.1, 'default': 0.5, 'help': 'Velocidad de acercamiento al promedio'},
        ],
    },
    'exactas': {
        'titulo':     'ED Exactas',
        'desc':       'Consistencia de Esfuerzo: Analiza si el flujo de aprendizaje es '
                      'estable o hay fugas de atención. (y·dy + α·t·dt = 0)',
        'meta':       'Esfuerzo',
        'color':      'rojo',
        'params_def': {'alpha': 0.2},
        'params_info': [
            {'name': 'alpha', 'label': 'Factor de desgaste (α)', 'min': 0.01, 'max': 1.0,
             'step': 0.01, 'default': 0.2, 'help': 'Cuánto decae el esfuerzo con el tiempo'},
        ],
    },
    'factor': {
        'titulo':     'Factor Integrante',
        'desc':       'Factores Externos: Mide cómo el estrés o el ruido afectan la '
                      'curva de retención. (dy/dt + p·y = q)',
        'meta':       'Impacto',
        'color':      'morado',
        'params_def': {'p': 0.3, 'q': 1.5},
        'params_info': [
            {'name': 'p', 'label': 'Amortiguamiento (p)', 'min': 0.1, 'max': 2.0,
             'step': 0.1, 'default': 0.3, 'help': 'Intensidad del factor externo negativo'},
            {'name': 'q', 'label': 'Fuerza estabilizadora (q)', 'min': 0.1, 'max': 5.0,
             'step': 0.1, 'default': 1.5, 'help': 'Capacidad de recuperación del alumno'},
        ],
    },
    'lineales': {
        'titulo':     'ED Lineales',
        'desc':       'Crecimiento Acumulativo: Modela el incremento directo del '
                      'conocimiento base por cada módulo. (dy/dt = a·y + b)',
        'meta':       'Crecimiento',
        'color':      'naranja',
        'params_def': {'a': 0.3, 'b': 0.5},
        'params_info': [
            {'name': 'a', 'label': 'Tasa de crecimiento (a)', 'min': 0.01, 'max': 1.0,
             'step': 0.01, 'default': 0.3, 'help': 'Proporción de conocimiento que retroalimenta'},
            {'name': 'b', 'label': 'Incremento base (b)', 'min': 0.0, 'max': 3.0,
             'step': 0.1, 'default': 0.5, 'help': 'Ganancia fija por módulo completado'},
        ],
    },
    'variacion': {
        'titulo':     'Variación de Parámetros',
        'desc':       'Respuesta a Estímulos: Evalúa la reacción del alumno ante cambios '
                      'en la dificultad. (dy/dt = -ω·sin(t))',
        'meta':       'Respuesta',
        'color':      'verde',
        'params_def': {'omega': 0.8},
        'params_info': [
            {'name': 'omega', 'label': 'Amplitud oscilatoria (ω)', 'min': 0.1, 'max': 3.0,
             'step': 0.1, 'default': 0.8, 'help': 'Intensidad del cambio de dificultad'},
        ],
    },
    'bernoulli': {
        'titulo':     'Bernoulli',
        'desc':       'Saturación Cognitiva: Identifica el punto donde el alumno deja '
                      'de aprender eficientemente. (dy/dt = r·y·(1-y/K))',
        'meta':       'Saturación',
        'color':      'rosa',
        'params_def': {'r': 0.5, 'K': 10.0},
        'params_info': [
            {'name': 'r', 'label': 'Tasa de aprendizaje (r)', 'min': 0.1, 'max': 2.0,
             'step': 0.1, 'default': 0.5, 'help': 'Velocidad de aprendizaje inicial'},
            {'name': 'K', 'label': 'Capacidad máxima (K)', 'min': 5.0, 'max': 10.0,
             'step': 0.5, 'default': 10.0, 'help': 'Techo cognitivo del alumno (máx 10)'},
        ],
    },
    'laplace': {
        'titulo':     'Laplace',
        'desc':       'Análisis de Impulso: Respuesta al escalón de un sistema de 2do '
                      'orden. Modela el impacto de un curso propedéutico.',
        'meta':       'Impulso',
        'color':      'cian',
        'params_def': {'zeta': 0.3, 'omega_n': 1.0},
        'params_info': [
            {'name': 'zeta', 'label': 'Factor de amortiguamiento (ζ)', 'min': 0.05, 'max': 0.99,
             'step': 0.05, 'default': 0.3, 'help': 'ζ < 1: subamortiguado (oscila)'},
            {'name': 'omega_n', 'label': 'Frecuencia natural (ωn)', 'min': 0.5, 'max': 3.0,
             'step': 0.5, 'default': 1.0, 'help': 'Velocidad de respuesta del sistema'},
        ],
    },
}


def analitica_view(request):
    return render(request, 'analytics/dashboard.html', {'ed_models': ED_MODELS})


def graficar_view(request, modelo):
    if modelo not in ED_MODELS:
        modelo = 'separables'

    info = ED_MODELS[modelo]
    engine = SEANIEngine()

    # --- DATOS REALES DE SEANI ---
    years   = Stage.objects.dates('application_date', 'year').distinct()
    stages  = Stage.objects.values_list('stage', flat=True).distinct().order_by('stage')
    careers = Career.objects.all()

    selected_year   = request.GET.get('year')
    selected_stage  = request.GET.get('stage')
    selected_career = request.GET.get('career')

    etapas_obj = Stage.objects.all().order_by('stage')
    if selected_stage:
        etapas_obj = etapas_obj.filter(stage=selected_stage)

    chart_labels = [f"Etapa {e.stage}" for e in etapas_obj]
    n_puntos = max(len(chart_labels), 4)

    datasets_reales = []
    colores = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF']

    carreras_to_plot = careers.filter(id=selected_career) if selected_career else careers

    for i, career in enumerate(carreras_to_plot):
        data_puntos = []
        for stage in etapas_obj:
            examenes = Exam.objects.filter(career=career, stage=stage)
            if selected_year:
                examenes = examenes.filter(created__year=selected_year)
            promedio = examenes.aggregate(Avg('score'))['score__avg'] or 0
            data_puntos.append(round(float(promedio), 2))

        datasets_reales.append({
            'label': career.name,
            'data': data_puntos,
            'borderColor': colores[i % len(colores)],
            'backgroundColor': colores[i % len(colores)] + '33',
            'type': 'line',
            'fill': False,
            'borderWidth': 2,
            'borderDash': [],
            'tension': 0.3,
            'pointRadius': 4,
        })

    # --- PARÁMETROS CONFIGURABLES DESDE EL FORMULARIO ---
    params = {}
    for p in info['params_info']:
        raw = request.GET.get(p['name'])
        try:
            params[p['name']] = float(raw)
        except (TypeError, ValueError):
            params[p['name']] = p['default']

    # Condición inicial: promedio real o 5
    promedio_gral = Exam.objects.all().aggregate(Avg('score'))['score__avg'] or 5.0
    y0 = float(promedio_gral)

    # --- RESOLVER MODELO MATEMÁTICO ---
    resultado = engine.resolver_modelo(modelo, y0, n_puntos=n_puntos, params=params)
    errores   = engine.calcular_errores(
        resultado['analitica'],
        resultado['euler'],
        resultado['euler_mejorado'],
        resultado['rk4'],
    )

    # Etiquetas para el eje X del modelo matemático
    labels_modelo = [f"t={i}" for i in range(1, n_puntos + 1)]

    # Datasets del modelo matemático (4 curvas)
    datasets_modelo = [
        {
            'label': f'Analítica: {resultado["etiqueta"]}',
            'data': resultado['analitica'],
            'borderColor': '#198754',
            'backgroundColor': '#19875422',
            'type': 'line', 'fill': False,
            'borderWidth': 3, 'borderDash': [],
            'tension': 0.4, 'pointRadius': 5,
            'yAxisID': 'y',
        },
        {
            'label': f'Euler  (MAE={errores["euler"]})',
            'data': resultado['euler'],
            'borderColor': '#dc3545',
            'backgroundColor': '#dc354522',
            'type': 'line', 'fill': False,
            'borderWidth': 2, 'borderDash': [6, 3],
            'tension': 0.0, 'pointRadius': 4,
            'yAxisID': 'y',
        },
        {
            'label': f'Euler Mejorado (MAE={errores["euler_mejorado"]})',
            'data': resultado['euler_mejorado'],
            'borderColor': '#fd7e14',
            'backgroundColor': '#fd7e1422',
            'type': 'line', 'fill': False,
            'borderWidth': 2, 'borderDash': [4, 2],
            'tension': 0.0, 'pointRadius': 4,
            'yAxisID': 'y',
        },
        
    ]

    context = {
        'modelo':           modelo.upper(),
        'modelo_key':       modelo,
        'info':             info,
        'years':            years,
        'stages':           stages,
        'careers':          careers,
        'selected_year':    selected_year,
        'selected_stage':   selected_stage,
        'selected_career':  selected_career,
        # Gráfica datos reales
        'chart_labels':     chart_labels,
        'chart_data':       datasets_reales,
        # Gráfica modelo matemático
        'labels_modelo':    labels_modelo,
        'datasets_modelo':  datasets_modelo,
        # Info del modelo
        'desc_ed':          resultado['desc_ed'],
        'desc_app':         resultado['desc_app'],
        'errores':          errores,
        'y0':               round(y0, 2),
        'params':           params,
        'params_info':      info['params_info'],
    }
    return render(request, 'analytics/grafica_detalle.html', context)