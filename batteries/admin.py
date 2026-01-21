from django.contrib import admin
from .models import BatterySubmission


@admin.register(BatterySubmission)
class BatterySubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'quantity', 'date_submitted', 'created_at')
    list_filter = ('date_submitted', 'created_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at',)
