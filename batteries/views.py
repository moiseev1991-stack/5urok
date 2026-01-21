from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import BatterySubmission
from .forms import UserRegistrationForm, BatterySubmissionForm


def home(request):
    """Главная страница с общей статистикой"""
    total_devices = BatterySubmission.get_total_count()
    total_users = BatterySubmission.objects.values('user').distinct().count()
    
    # Статистика по типам устройств
    stats_by_type = BatterySubmission.get_stats_by_type()
    
    # Статистика за разные периоды
    stats_7_days = BatterySubmission.get_stats_by_period(7)
    stats_30_days = BatterySubmission.get_stats_by_period(30)
    stats_90_days = BatterySubmission.get_stats_by_period(90)
    
    # Общее количество за периоды
    end_date = timezone.now()
    total_7_days = BatterySubmission.objects.filter(
        date_submitted__gte=end_date - timedelta(days=7)
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    total_30_days = BatterySubmission.objects.filter(
        date_submitted__gte=end_date - timedelta(days=30)
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    total_90_days = BatterySubmission.objects.filter(
        date_submitted__gte=end_date - timedelta(days=90)
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    context = {
        'total_devices': total_devices,
        'total_users': total_users,
        'stats_by_type': stats_by_type,
        'stats_7_days': stats_7_days,
        'stats_30_days': stats_30_days,
        'stats_90_days': stats_90_days,
        'total_7_days': total_7_days,
        'total_30_days': total_30_days,
        'total_90_days': total_90_days,
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
    """Страница для ввода информации о сданных устройствах"""
    if request.method == 'POST':
        form = BatterySubmissionForm(request.POST)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.user = request.user
            submission.save()
            device_name = dict(BatterySubmission.DEVICE_TYPE_CHOICES).get(
                submission.device_type, submission.device_type
            )
            messages.success(
                request, 
                f'Спасибо! Вы добавили {submission.quantity} {device_name.lower()}. Всего сдано: {BatterySubmission.get_total_count()}'
            )
            return redirect('submit_batteries')
    else:
        form = BatterySubmissionForm()
    
    # Получаем статистику пользователя
    user_submissions = BatterySubmission.objects.filter(user=request.user)
    user_total = user_submissions.aggregate(total=Sum('quantity'))['total'] or 0
    user_count = user_submissions.count()
    
    # Статистика по типам для пользователя
    user_stats_by_type = user_submissions.values('device_type').annotate(
        total=Sum('quantity'),
        count=Count('id')
    )
    
    context = {
        'form': form,
        'user_total': user_total,
        'user_count': user_count,
        'recent_submissions': user_submissions[:5],
        'user_stats_by_type': user_stats_by_type,
    }
    return render(request, 'batteries/submit_batteries.html', context)


@login_required
def profile(request):
    """Профиль пользователя с историей сдач"""
    user_submissions = BatterySubmission.objects.filter(user=request.user)
    user_total = user_submissions.aggregate(total=Sum('quantity'))['total'] or 0
    
    # Статистика по типам для пользователя
    user_stats_by_type = user_submissions.values('device_type').annotate(
        total=Sum('quantity'),
        count=Count('id')
    )
    
    context = {
        'user_submissions': user_submissions,
        'user_total': user_total,
        'submission_count': user_submissions.count(),
        'user_stats_by_type': user_stats_by_type,
    }
    return render(request, 'batteries/profile.html', context)
