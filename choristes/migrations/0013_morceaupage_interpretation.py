# Generated by Django 4.2.7 on 2023-12-07 16:21

from django.db import migrations
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('choristes', '0012_rename__title_morceaupage_titre'),
    ]

    operations = [
        migrations.AddField(
            model_name='morceaupage',
            name='interpretation',
            field=wagtail.fields.RichTextField(blank=True),
        ),
    ]