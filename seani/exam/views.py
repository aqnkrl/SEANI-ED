from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import openpyxl
from django.views.decorators.csrf import csrf_protect
import csv
import io
import json
import random

from django.db.models import Avg, Count
from collections import defaultdict
from .models import Exam, Stage, HomeScreenSetting,Career, Module
from career.models import Career
from .forms import CandidateForm, LoadCSVForm, StageForm, AddStageForm


# ----------------------------------------------------
# Vistas del aspirante

@login_required
def home(request):
    if request.user.is_superuser:
        return redirect('admin:index')

    screen_setting = HomeScreenSetting.objects.filter(is_active=True).first()

    if screen_setting:
        if screen_setting.screen_name == 'home2':
            return home2(request)
        elif screen_setting.screen_name == 'home3':
            return home3(request)

    exam = request.user.exam
    modules = exam.exammodule_set.all()
    return render(request, 'exam/home.html', {'modules': modules})

@login_required
def home2(request):
    if request.user.is_superuser:
        return redirect('admin:index')

    settings = HomeScreenSetting.objects.filter(screen_name='home2').first()
    return render(request, 'exam/home2.html', {'settings': settings})

@login_required
def home3(request):
    if request.user.is_superuser:
        return redirect('admin:index')
    return render(request, 'exam/home3.html')

@login_required
def question(request, module_id, question_id=1):
    exam = request.user.exam
    modules = exam.exammodule_set.filter(module_id=module_id)

    if modules.count() == 0 or question_id <= 0:
        return redirect('exam:home')
    if not exam.exammodule_set.get(module_id=module_id).active:
        return redirect('exam:home')

    questions = exam.breakdown_set.filter(question__module_id=module_id)

    if request.method == 'GET':
        try:
            question_breakdown = questions[question_id - 1]
            question = question_breakdown.question
            answer = question_breakdown.answer
            return render(request, 'exam/question.html', {
                'question': question,
                'module_id': module_id,
                'question_id': question_id,
                'answer': answer,
            })
        except IndexError:
            exam.compute_score_by_module(module_id)
            exam.compute_score()
            return redirect('exam:home')

    elif request.method == 'POST':
        question_breakdown = questions[question_id - 1]
        answer = request.POST['answer']
        if question_breakdown.answer != answer:
            question_breakdown.answer = answer
            question_breakdown.save()
        return redirect('exam:question', module_id, question_id + 1)

@login_required
def save_module(request, module_id):
    if request.method == 'POST':
        exam = request.user.exam
        exam.compute_score_by_module(module_id)
    return redirect('exam:home')

@login_required
def save_exam(request):
    if request.method == 'POST':
        exam = request.user.exam
        exam.compute_score()
    return redirect('exam:home')

# ----------------------------------------------------
# Vistas del administrador

def create(request):
    if request.method == 'POST':
        form = CandidateForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            stage = form.cleaned_data['stage']
            career = form.cleaned_data['career']

            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name
            )

            exam = Exam.objects.create(user=user, stage=stage, career=career)
            exam.set_modules()
            exam.set_questions()

            return render(request, 'admin/exam/create.html', {
                'message': "Aspirante Registrado!",
                'form': CandidateForm()
            })

    return render(request, 'admin/exam/create.html', { "form": CandidateForm() })

def load_csv(request):
    if request.method == 'POST':
        form = LoadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            file_csv = form.cleaned_data['file']
            stage = form.cleaned_data['stage']

            decoded = file_csv.read().decode('utf-8-sig')
            reader = csv.reader(io.StringIO(decoded))
            next(reader, None)

            duplicados = []
            registrados = 0

            for row in reader:
                if len(row) < 6 or not any(cell.strip() for cell in row):
                    continue

                first_name = row[0].strip().title()
                last_name = row[1].strip().title()
                email = row[2].strip().lower()
                password = row[3].strip()
                career_short = row[4].strip().upper()

                career, _ = Career.objects.get_or_create(
                    short_name=career_short,
                    defaults={"name": career_short.title()}
                )

                if not User.objects.filter(username=email).exists():
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                    )

                    exam = Exam.objects.create(user=user, career=career, stage=stage)
                    exam.set_modules()
                    exam.set_questions()
                    registrados += 1
                else:
                    duplicados.append(email)

            mensaje = "Aspirante(s) registrado(s)!"
            if duplicados:
                mensaje += f" Correos duplicados: {', '.join(duplicados)}"

            return render(request, 'admin/exam/load_csv.html', {
                'message': mensaje,
                'duplicados': duplicados
            })

    return render(request, 'admin/exam/load_csv.html', { "form": LoadCSVForm() })

@login_required
def get_scores_with_modules(request):
    if request.user.is_superuser:
        results = []
        exams = Exam.objects.filter(stage_id=4)
        for e in exams:
            scores = e.exammodule_set.all()
            results.append({
                'user': e.full_name(),
                'email': e.user.email,
                'career': e.career,
                'mod_1': round(scores[0].score, 2),
                'mod_2': round(scores[1].score, 2),
                'mod_3': round(scores[2].score, 2),
                'mod_4': round(scores[3].score, 2),
                'final': round(e.score, 2)
            })
        return render(request, 'home/results.html', { 'results': results })
    return redirect('home')

@login_required
def home_results(request):
    if not request.user.is_superuser:
        return redirect('home')

    form = StageForm(request.GET or None)
    exams = []

    if form.is_valid():
        selected_stage = form.cleaned_data['stage']
        selected_career = form.cleaned_data.get('career')

        exams = Exam.objects.filter(stage=selected_stage)
        if selected_career:
            exams = exams.filter(career=selected_career)

        exams = exams.select_related('user', 'career')

    return render(request, 'home/results.html', {
        'form': form,
        'exams': exams
    })

@login_required
def export_filtered_results_excel(request):
    if not request.user.is_superuser:
        return redirect('home')

    form = StageForm(request.GET or None)
    if form.is_valid():
        selected_stage = form.cleaned_data['stage']
        selected_career = form.cleaned_data.get('career')

        exams = Exam.objects.filter(stage=selected_stage)
        if selected_career:
            exams = exams.filter(career=selected_career)

        exams = exams.select_related('user', 'career')

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Resultados Filtrados"

        sheet.append([
            "Nombre completo", "Correo", "Carrera",
            "Comprensión Lectora", "Estructura de la Lengua",
            "Pensamiento Matemático", "Pensamiento Analítico", "Promedio"
        ])

        for exam in exams:
            modules = exam.exammodule_set.all()
            if modules.count() < 4:
                continue

            sheet.append([
                exam.full_name(),
                exam.user.email,
                exam.career.name,
                round(modules[0].score, 2),
                round(modules[1].score, 2),
                round(modules[2].score, 2),
                round(modules[3].score, 2),
                round(exam.score, 2),
            ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename=resultados_filtrados.xlsx'
        workbook.save(response)
        return response

    return HttpResponse("Parámetros inválidos para exportar.", status=400)

@login_required
def export_scores_excel(request):
    if not request.user.is_superuser:
        return redirect('home')

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Resultados por Módulo"

    sheet.append([
        "Nombre completo", "Correo", "Carrera",
        "Módulo 1", "Módulo 2", "Módulo 3", "Módulo 4", "Puntaje Final"
    ])

    exams = Exam.objects.filter(stage_id=4).select_related('user', 'career')
    for exam in exams:
        modules = exam.exammodule_set.all()
        if modules.count() < 4:
            continue

        sheet.append([
            exam.full_name(),
            exam.user.email,
            exam.career.name,
            round(modules[0].score, 2),
            round(modules[1].score, 2),
            round(modules[2].score, 2),
            round(modules[3].score, 2),
            round(exam.score, 2),
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=resultados_modulos.xlsx'
    workbook.save(response)
    return response

# ----------------------------------------------------
# CRUD de Etapas 

@login_required
def stage_add(request):
    if not request.user.is_superuser:
        return redirect('home')

    if request.method == 'POST':
        form = AddStageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('exam:stage_list')
    else:
        form = AddStageForm()

    return render(request, 'admin/stage_add.html', { 'form': form })

@login_required
def stage_list(request):
    if not request.user.is_superuser:
        return redirect('home')
    stages = Stage.objects.all().order_by('stage')
    return render(request, 'admin/stage_list.html', { 'stages': stages })

@login_required
def stage_edit(request, pk):
    if not request.user.is_superuser:
        return redirect('home')

    stage = get_object_or_404(Stage, pk=pk)
    if request.method == 'POST':
        form = AddStageForm(request.POST, instance=stage)
        if form.is_valid():
            form.save()
            return redirect('exam:stage_list')
    else:
        form = AddStageForm(instance=stage)
    return render(request, 'admin/stage_edit.html', { 'form': form, 'edit': True })

@login_required
def stage_delete(request, pk):
    if not request.user.is_superuser:
        return redirect('home')

    stage = get_object_or_404(Stage, pk=pk)
    if request.method == 'POST':
        stage.delete()
        return redirect('exam:stage_list')
    return render(request, 'admin/stage_confirm_delete.html', {'stage': stage})
 
# ------------------------------------------------------------------------------------
# HomeScreenSetting
@csrf_protect
def home_screen_table(request):
    screens = HomeScreenSetting.objects.all().order_by('screen_name')

    if request.method == 'POST':
        screen_id = request.POST.get('screen_id')
        action = request.POST.get('action')

        screen = get_object_or_404(HomeScreenSetting, id=screen_id)

        if action == 'activate':
            # Desactivar todas
            HomeScreenSetting.objects.update(is_active=False)
            screen.is_active = True

            if screen.screen_name == 'home2':
                # Guardar fecha y hora si vienen en el POST
                screen.display_date = request.POST.get('display_date') or None
                screen.display_time = request.POST.get('display_time') or None

            screen.save()

        return redirect('exam:home_screen_table')

    return render(request, 'admin/home_screen_table.html', {'screens': screens})


# ------------------------------------------------------------------------------------
# ESTO TODAVIA NO ESTÁ IMPLEMENTADO(NO FUNCIONA)
"""
@login_required
def admin_home(request):
    if not request.user.is_superuser:
        return redirect('home')

    exams = Exam.objects.select_related('stage')

    grouped_general = defaultdict(list)    # (year, stage) -> [scores]
    grouped_modules = {i: defaultdict(list) for i in range(1,5)}  # módulos 1 a 4

    for exam in exams:
        if exam.stage and exam.stage.application_date:
            year = exam.stage.application_date.year
        else:
            continue
        stage_num = exam.stage.stage
        grouped_general[(year, stage_num)].append(exam.score)

        modules = exam.exammodule_set.all()
        for mod in modules:
            if mod.module.id in range(1,5):
                grouped_modules[mod.module.id][(year, stage_num)].append(mod.score)

    all_stages = sorted({stage for (_, stage) in grouped_general})
    all_years = sorted({year for (year, _) in grouped_general})

    chart_data = {}
    for year in all_years:
        chart_data[year] = []
        for stage in all_stages:
            scores = grouped_general.get((year, stage), [])
            avg = round(sum(scores) / len(scores), 2) if scores else 0
            chart_data[year].append(avg)

    def avg_scores_for_module(mod_id):
        result = []
        for stage in all_stages:
            scores = []
            for year in all_years:
                scores += grouped_modules[mod_id].get((year, stage), [])
            avg = round(sum(scores) / len(scores), 2) if scores else 0
            result.append(avg)
        return result

    context = {
        'chart_labels': json.dumps([f"Etapa {s}" for s in all_stages]),
        'chart_data': json.dumps(chart_data),
        'mod1_scores': json.dumps(avg_scores_for_module(1)),
        'mod2_scores': json.dumps(avg_scores_for_module(2)),
        'mod3_scores': json.dumps(avg_scores_for_module(3)),
        'mod4_scores': json.dumps(avg_scores_for_module(4)),
    }

    return render(request, 'admin/home.html', context)
"""


# ---------------------------------------------------
# Vista para detalle por módulo con filtros y gráfica
# ------------------------------------------------------------------------------------
@login_required
def detalle_por_modulo(request):
    if not request.user.is_superuser:
        return redirect('home')

    selected_stage = request.GET.get('stage')
    selected_career = request.GET.get('career')
    selected_year = request.GET.get('year')
    module_id = request.GET.get('module_id')

    exams = Exam.objects.select_related('stage', 'career').prefetch_related('exammodule_set__module').all()

    if selected_stage:
        exams = exams.filter(stage__stage=selected_stage)
    if selected_career:
        exams = exams.filter(career__id=selected_career)
    if selected_year:
        exams = exams.filter(stage__application_date__year=selected_year)

    if module_id:
        try:
            module_id = int(module_id)
            if module_id not in [1, 2, 3, 4]:
                module_id = None
        except ValueError:
            module_id = None

    # Agrupar por etapa y carrera
    grouped = defaultdict(lambda: defaultdict(list))

    for exam in exams:
        if not exam.stage or not exam.stage.application_date or not exam.career:
            continue
        stage_num = exam.stage.stage
        year = exam.stage.application_date.year
        career_name = exam.career.name
        modules = exam.exammodule_set.all()
        mod_score = None
        if module_id:
            for mod in modules:
                if mod.module.id == module_id:
                    mod_score = mod.score
                    break
        else:
            mod_score = exam.score

        if mod_score is not None:
            label = f"Etapa {stage_num} - {year}"
            grouped[label][career_name].append(mod_score)

    all_labels = sorted(grouped.keys())
    all_careers = sorted({c for label in grouped.values() for c in label.keys()})

    vibrant_colors = [
        '#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231',
        '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe',
        '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000',
        '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080'
    ]

    chart_labels = all_labels
    chart_data = []

    for career in all_careers:
        data = []
        for label in all_labels:
            scores = grouped[label].get(career, [])
            avg = round(sum(scores) / len(scores), 2) if scores else 0
            data.append(avg)
        color_index = all_careers.index(career) % len(vibrant_colors)
        chart_data.append({
            'label': career,
            'data': data,
            'backgroundColor': vibrant_colors[color_index]
        })

    # Promedios por módulo agrupados por etapa + año
    modulos = Module.objects.filter(id__in=[1, 2, 3, 4])
    modulo_chart_labels = sorted(set(
        f"Etapa {exam.stage.stage} - {exam.stage.application_date.year}"
        for exam in exams if exam.stage and exam.stage.application_date
    ))

    modulo_chart_data = []

    modulo_colors = {
        1: '#3b82f6',  # Comprensión Lectora
        2: '#facc15',  # Estructura de la Lengua
        3: '#ef4444',  # Pensamiento Matemático
        4: '#8b5cf6',  # Pensamiento Analítico
    }

    for mod in modulos:
        data = []
        for label in modulo_chart_labels:
            etapa_num, year = label.replace("Etapa ", "").split(" - ")
            etapa_num = int(etapa_num)
            year = int(year)
            scores = []
            for exam in exams:
                if exam.stage and exam.stage.stage == etapa_num and exam.stage.application_date.year == year:
                    for ex_mod in exam.exammodule_set.all():
                        if ex_mod.module.id == mod.id and ex_mod.score is not None:
                            scores.append(ex_mod.score)
            avg = round(sum(scores) / len(scores), 2) if scores else 0
            data.append(avg)

        modulo_chart_data.append({
            'label': mod.name,
            'data': data,
            'backgroundColor': modulo_colors.get(mod.id, '#999999')
        })

    if module_id:
        try:
            module_obj = Module.objects.get(id=module_id)
            module_name = module_obj.name
        except Module.DoesNotExist:
            module_name = f"Módulo {module_id}"
    else:
        module_name = "General"

    stages = Stage.objects.values_list('stage', flat=True).distinct().order_by('stage')
    years = Stage.objects.dates('application_date', 'year').distinct()
    careers = Career.objects.all()

    context = {
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'modulo_chart_labels': modulo_chart_labels,
        'modulo_chart_data': modulo_chart_data,
        'years': years,
        'stages': stages,
        'careers': careers,
        'selected_year': selected_year,
        'selected_stage': selected_stage,
        'selected_career': selected_career,
        'selected_module': module_id,
        'module_name': module_name,
    }

    return render(request, 'admin/detalle_por_modulo.html', context)


@login_required
def debug_exam_data(request):
    exams = Exam.objects.select_related('stage').prefetch_related('exammodule_set__module').all()[:10]
    data = []
    for exam in exams:
        modules = [{
            'module_id': em.module.id,
            'module_name': em.module.name,
            'score': em.score
        } for em in exam.exammodule_set.all()]
        data.append({
            'exam_id': exam.id,
            'stage': exam.stage.stage,
            'stage_date': exam.stage.application_date,
            'modules': modules
        })
    return render(request, 'admin/debug_exam_data.html', {'exams': data})


# ----------------------------------------------------
# CRUD de Aspirantes

@login_required
def aspirante_list(request):
    if not request.user.is_superuser:
        return redirect('home')

    aspirantes = Exam.objects.select_related('user', 'stage', 'career').order_by('user__last_name')
    return render(request, 'admin/aspirante_list.html', { 'aspirantes': aspirantes })

@login_required
def aspirante_add(request):
    if not request.user.is_superuser:
        return redirect('home')

    if request.method == 'POST':
        form = CandidateForm(request.POST)
        if form.is_valid():
            # Guardar nuevo aspirante
            return redirect('exam:aspirante_add')  
    else:
        form = CandidateForm()

    # Obtener aspirantes para la tabla
    aspirantes = Exam.objects.select_related('user', 'stage', 'career').order_by('user__last_name')

    return render(request, 'admin/aspirante_add.html', {
        'form': form,
        'aspirantes': aspirantes,
    })

@login_required
def aspirante_delete(request, pk):
    if not request.user.is_superuser:
        return redirect('home')

    exam = get_object_or_404(Exam, pk=pk)

    if request.method == 'POST':
        exam.user.delete()  
        return redirect('exam:aspirante_list')

    return render(request, 'admin/aspirante_confirm_delete.html', { 'aspirante': exam })

@login_required
def aspirante_edit(request, pk):
    if not request.user.is_superuser:
        return redirect('home')

    exam = get_object_or_404(Exam, pk=pk)
    user = exam.user

    if request.method == 'POST':
        form = CandidateForm(request.POST)  
        if form.is_valid():
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.username = form.cleaned_data['username']

            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])

            user.save()

            stage_changed = exam.stage != form.cleaned_data['stage']
            career_changed = exam.career != form.cleaned_data['career']

            exam.stage = form.cleaned_data['stage']
            exam.career = form.cleaned_data['career']
            exam.save()

            if stage_changed or career_changed:
                exam.set_modules()
                exam.set_questions()

            return redirect('exam:aspirante_list')
    else:
        form = CandidateForm(initial={
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'username': user.username,
            'stage': exam.stage,
            'career': exam.career,
        })

    return render(request, 'admin/aspirante_edit.html', {'form': form, 'edit': True})

@login_required
def admin_home(request):
    if not request.user.is_superuser:
        return redirect('home')

    # Obtener aspirantes (exámenes con usuario relacionado)
    aspirantes = Exam.objects.select_related('user', 'stage', 'career').all().order_by('user__last_name')

    # Obtener módulos para el div graf-container (como ya haces)
    modulos = Module.objects.all()

    return render(request, 'admin/home.html', {
        'modulos': modulos,
        'aspirantes': aspirantes,
    })
