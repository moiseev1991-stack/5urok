from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum, Count
from datetime import datetime, timedelta


class BatterySubmission(models.Model):
    """Модель для хранения информации о сданных устройствах"""
    
    DEVICE_TYPE_CHOICES = [
        ('battery', 'Батарейки'),
        ('lamp', 'Лампы'),
        ('powerbank', 'Power Banks'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='battery_submissions')
    device_type = models.CharField(
        max_length=20,
        choices=DEVICE_TYPE_CHOICES,
        default='battery',
        verbose_name='Тип устройства'
    )
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    date_submitted = models.DateTimeField(default=timezone.now, verbose_name='Дата сдачи')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания записи')
    
    class Meta:
        verbose_name = 'Сдача устройств'
        verbose_name_plural = 'Сдачи устройств'
        ordering = ['-date_submitted']
    
    def __str__(self):
        device_name = dict(self.DEVICE_TYPE_CHOICES).get(self.device_type, self.device_type)
        return f'{self.user.username} - {self.quantity} {device_name.lower()} ({self.date_submitted.date()})'
    
    @classmethod
    def get_total_count(cls):
        """Возвращает общее количество всех сданных устройств"""
        return cls.objects.aggregate(total=models.Sum('quantity'))['total'] or 0
    
    @classmethod
    def get_stats_by_type(cls):
        """Возвращает статистику по типам устройств"""
        stats = cls.objects.values('device_type').annotate(
            total=Sum('quantity'),
            count=Count('id')
        )
        result = {}
        for stat in stats:
            device_name = dict(cls.DEVICE_TYPE_CHOICES).get(stat['device_type'], stat['device_type'])
            result[stat['device_type']] = {
                'name': device_name,
                'total': stat['total'] or 0,
                'count': stat['count']
            }
        return result
    
    @classmethod
    def get_stats_by_period(cls, days=30):
        """Возвращает статистику за определенный период"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        stats = cls.objects.filter(
            date_submitted__gte=start_date,
            date_submitted__lte=end_date
        ).values('device_type').annotate(
            total=Sum('quantity')
        )
        
        result = {}
        for stat in stats:
            device_name = dict(cls.DEVICE_TYPE_CHOICES).get(stat['device_type'], stat['device_type'])
            result[stat['device_type']] = {
                'name': device_name,
                'total': stat['total'] or 0
            }
        return result