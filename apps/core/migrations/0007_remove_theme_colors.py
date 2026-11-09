from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_palettes"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="themesettings",
            name="background_color",
        ),
        migrations.RemoveField(
            model_name="themesettings",
            name="navbar_bg",
        ),
        migrations.RemoveField(
            model_name="themesettings",
            name="navbar_follows_primary",
        ),
        migrations.RemoveField(
            model_name="themesettings",
            name="navbar_hover_bg",
        ),
        migrations.RemoveField(
            model_name="themesettings",
            name="navbar_text",
        ),
        migrations.RemoveField(
            model_name="themesettings",
            name="primary_color",
        ),
        migrations.RemoveField(
            model_name="themesettings",
            name="secondary_color",
        ),
        migrations.RemoveField(
            model_name="themesettings",
            name="tertiary_color",
        ),
        migrations.RemoveField(
            model_name="themesettings",
            name="text_color",
        ),
        migrations.RemoveField(
            model_name="themesettings",
            name="text_muted_color",
        ),
    ]
