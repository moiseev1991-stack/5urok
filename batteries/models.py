from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class BatterySubmission(models.Model):
    """Модель для хранения информации о сданных батарейках"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='battery_submissions')
    quantity = models.PositiveIntegerField(verbose_name='Количество батареек')
    date_submitted = models.DateTimeField(default=timezone.now, verbose_name='Дата сдачи')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания записи')
    
    class Meta:
        verbose_name = 'Сдача батареек'
        verbose_name_plural = 'Сдачи батареек'
        ordering = ['-date_submitted']
    
    def __str__(self):
        return f'{self.user.username} - {self.quantity} батареек ({self.date_submitted.date()})'
    
    @classmethod
    def get_total_count(cls):
        """Возвращает общее количество сданных батареек"""
        return cls.objects.aggregate(total=models.Sum('quantity'))['total'] or 0
