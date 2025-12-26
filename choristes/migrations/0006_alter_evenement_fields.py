# Generated migration

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('choristes', '0005_choirrole_alter_choriste_options_choriste_active_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='evenement',
            name='end_hour',
        ),
        migrations.RemoveField(
            model_name='evenement',
            name='start_hour',
        ),
        migrations.AlterField(
            model_name='evenement',
            name='start_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='evenement',
            name='end_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
