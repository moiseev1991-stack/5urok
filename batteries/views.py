from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import BatterySubmission
from .forms import UserRegistrationForm, BatterySubmissionForm


def home(request):
    """Главная страница с общей статистикой"""
    total_batteries = BatterySubmission.get_total_count()
    total_users = BatterySubmission.objects.values('user').distinct().count()
    
    context = {
        'total_batteries': total_batteries,
        'total_users': total_users,
    }
    return render(request, 'batteries/home.html', context)


def register(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт создан для {username}!')
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'batteries/register.html', {'form': form})


def user_login(request):
    """Вход пользователя"""
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')
    return render(request, 'batteries/login.html')


@login_required
def submit_batteries(request):
    """Страница для ввода информации о сданных батарейках"""
    if request.method == 'POST':
        form = BatterySubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.save()
            messages.success(
                request, 
                f'Спасибо! Вы добавили {submission.quantity} батареек. Всего сдано: {BatterySubmission.get_total_count()}'
            )
            return redirect('submit_batteries')
    else:
        form = BatterySubmissionForm()
    
    # Получаем статистику пользователя
    user_submissions = BatterySubmission.objects.filter(user=request.user)
    user_total = user_submissions.aggregate(total=Sum('quantity'))['total'] or 0
    user_count = user_submissions.count()
    
    context = {
        'form': form,
        'user_total': user_total,
        'user_count': user_count,
        'recent_submissions': user_submissions[:5],
    }
    return render(request, 'batteries/submit_batteries.html', context)


@login_required
def profile(request):
    """Профиль пользователя с историей сдач"""
    user_submissions = BatterySubmission.objects.filter(user=request.user)
    user_total = user_submissions.aggregate(total=Sum('quantity'))['total'] or 0
    
    context = {
        'user_submissions': user_submissions,
        'user_total': user_total,
        'submission_count': user_submissions.count(),
    }
    return render(request, 'batteries/profile.html', context)
