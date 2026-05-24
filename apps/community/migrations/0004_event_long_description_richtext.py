from django.db import migrations
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('community', '0003_event_descriptions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='long_description',
            field=wagtail.fields.RichTextField(
                blank=True,
                verbose_name='Description longue',
                help_text="Détails affichés dans la fenêtre d'expansion (facultatif)",
            ),
        ),
    ]
