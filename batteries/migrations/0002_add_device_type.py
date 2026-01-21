# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('batteries', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='batterysubmission',
            name='device_type',
            field=models.CharField(
                choices=[('battery', 'Батарейки'), ('lamp', 'Лампы'), ('powerbank', 'Power Banks')],
                default='battery',
                max_length=20,
                verbose_name='Тип устройства'
            ),
        ),
        migrations.AlterModelOptions(
            name='batterysubmission',
            options={'ordering': ['-date_submitted'], 'verbose_name': 'Сдача устройств', 'verbose_name_plural': 'Сдачи устройств'},
        ),
    ]
