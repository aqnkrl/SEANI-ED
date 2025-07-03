from django.shortcuts import render, redirect
from django.http import HttpResponse

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .models import Exam, Stage
from career.models import Career

from .forms import CandidateForm, LoadCSVForm


### Views for Aspirantes
@login_required
def home(request):
    if request.user.is_superuser:
        return redirect('admin:index')
    exam = request.user.exam
    modules = exam.exammodule_set.all()
    # return render(request, 'exam/home3.html')  # Después del Examen
    # return render(request, 'exam/home2.html')  # Antes del Examen
    return render(request, 'exam/home.html', {'modules': modules} ) # Durante el examen

@login_required
def question(request, module_id, question_id = 1):
    exam = request.user.exam

    modules = exam.exammodule_set.filter(module_id = module_id)

    if modules.count() == 0 or question_id <= 0:
        return redirect('exam:home')
    if exam.exammodule_set.get(module_id = module_id).active == False:
        return redirect('exam:home')
    if request.method == 'GET':
        try:
            # exam = request.user.exam
            questions = exam.breakdown_set.filter(question__module_id = module_id)
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
        
    if request.method == 'POST':
        # exam = request.user.exam
        questions = exam.breakdown_set.filter(question__module_id = module_id)
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
    return redirect('exam:home')

@login_required
def save_exam(request):
    if request.method == 'POST':
        exam = request.user.exam
        exam.compute_score()
        return redirect('exam:home')
    return redirect('exam:home')


#### Views for Admin
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
                    username = username, 
                    password = password, 
                    email = email)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            exam = Exam.objects.create(user = user, stage = stage, career = career)
            exam.set_modules()
            exam.set_questions()
            form = CandidateForm()
            return render(request, 'admin/exam/create.html', {'message': "Aspirante Registrado!", "form": form})
    
    form = CandidateForm()
    return render(request, 'admin/exam/create.html', { "form": form })

def load_csv(request):
    if request.method == 'POST':
        form = LoadCSVForm(request.POST, request.FILES)
        
        if form.is_valid():
            
            file_csv = form.cleaned_data['file']
            stage = form.cleaned_data['stage']
            data_csv = file_csv.read().decode('utf-8').split('\n')

            data = []
            for index, line_ in enumerate(data_csv):
                if index != 0:
                    line = line_.split(',')
                    data.append({
                        "first_name": line[0].strip(), 
                        "last_name": line[1].strip(),
                        "email": line[2].strip(),
                        "password": line[3].strip(),
                        "career": line[4].strip()
                        })
                    
            for item in data:
                user = User.objects.create_user(
                        username = item['email'],
                        password = item['password'],
                        email = item['email'])
                user.first_name = item['first_name']
                user.last_name = item['last_name']
                user.save()

                career = Career.objects.get(short_name = item['career'])

                exam = Exam.objects.create(user = user, career = career, stage = stage )
                exam.set_modules()
                exam.set_questions()
            
            return render(request, 'admin/exam/load_csv.html', {'message': "Carga de datos exitosa!"})

    form = LoadCSVForm()
    return render(request, 'admin/exam/load_csv.html', {"form": form})

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
    else:
        return redirect('home')