from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0002_remove_event_is_repetition_remove_event_pupitre_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='description',
            new_name='long_description',
        ),
        migrations.AddField(
            model_name='event',
            name='short_description',
            field=models.CharField(
                blank=True,
                max_length=255,
                verbose_name='Description courte',
                help_text='Résumé affiché dans la liste (facultatif)',
            ),
        ),
    ]
