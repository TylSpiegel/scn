from django.db import migrations


class Migration(migrations.Migration):
    """
    Vide la colonne `music_piece.timecodes` pour les lignes importées avant
    le passage de StreamField à TextField. L'ancien JSON est incompatible avec
    le nouveau format « paroles + [mm:ss] » et serait affiché tel quel dans
    l'admin / le player.
    """

    dependencies = [
        ("music", "0002_repertoirepage_ordre_important_alter_piece_timecodes"),
    ]

    operations = [
        migrations.RunSQL(
            sql="UPDATE music_piece SET timecodes = '';",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
