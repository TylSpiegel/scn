import django.core.validators
import django.db.models.deletion
import modelcluster.fields
import taggit.managers
import wagtail.fields
from django.db import migrations, models


def clear_music_data(apps, schema_editor):
    RepertoireItem = apps.get_model('music', 'RepertoireItem')
    Piece = apps.get_model('music', 'Piece')
    RepertoireItem.objects.all().delete()
    Piece.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0004_remove_piece_tags_repertoireitem_tags_and_more'),
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
        ('wagtailcore', '0096_referenceindex_referenceindex_source_object_and_more'),
        ('wagtaildocs', '0014_alter_document_file_size'),
    ]

    operations = [
        migrations.RunPython(clear_music_data, migrations.RunPython.noop),

        migrations.DeleteModel(name='RepertoireItem'),
        migrations.DeleteModel(name='Piece'),

        migrations.CreateModel(
            name='PieceIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(
                    auto_created=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    serialize=False,
                    to='wagtailcore.page',
                )),
                ('introduction', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Index des morceaux',
                'verbose_name_plural': 'Index des morceaux',
            },
            bases=('wagtailcore.page',),
        ),

        migrations.CreateModel(
            name='Piece',
            fields=[
                ('page_ptr', models.OneToOneField(
                    auto_created=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    serialize=False,
                    to='wagtailcore.page',
                )),
                ('compositeur', models.CharField(max_length=250)),
                ('descr', wagtail.fields.RichTextField(blank=True)),
                ('traduction', wagtail.fields.RichTextField(blank=True)),
                ('interpretation', wagtail.fields.RichTextField(blank=True)),
                ('activer_timecodes', models.BooleanField(
                    default=False,
                    help_text='Cochez pour activer la fonctionnalité de timecodes',
                    verbose_name='Activer les timecodes',
                )),
                ('timecodes', wagtail.fields.StreamField(
                    [('timecode', 2)],
                    blank=True,
                    block_lookup={
                        0: ('wagtail.blocks.CharBlock', (), {
                            'help_text': 'Format mm:ss, ex: 02:45',
                            'label': 'Timecode',
                            'validators': [django.core.validators.RegexValidator(
                                message='Le format doit être mm:ss (ex: 02:45)',
                                regex='^([0-5][0-9]):([0-5][0-9])$',
                            )],
                        }),
                        1: ('wagtail.blocks.TextBlock', (), {'label': 'Texte associé'}),
                        2: ('wagtail.blocks.StructBlock', [[('timecode', 0), ('texte', 1)]], {}),
                    },
                    null=True,
                    use_json_field=True,
                    verbose_name='Timecodes avec annotations',
                )),
                ('pdf', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='+',
                    to='wagtaildocs.document',
                )),
                ('audios', wagtail.fields.StreamField(
                    [('audios', 4)],
                    blank=True,
                    block_lookup={
                        0: ('wagtail.blocks.ChoiceBlock', [], {'choices': [
                            ('Tutti', 'Tutti'), ('Soprano', 'Soprano'),
                            ('Alto', 'Alto'), ('Ténor', 'Ténor'), ('Basse', 'Basse'),
                        ], 'required': False}),
                        1: ('wagtail.blocks.CharBlock', (), {
                            'help_text': 'Entrer une valeur ici annule le champ ci-dessus.',
                            'max_length': 30, 'required': False,
                        }),
                        2: ('wagtail.documents.blocks.DocumentChooserBlock', (), {
                            'help_text': 'Sélectionnez un fichier audio', 'required': False,
                        }),
                        3: ('wagtail.blocks.CharBlock', (), {
                            'help_text': 'Un petit mot ?', 'max_length': 255, 'required': False,
                        }),
                        4: ('wagtail.blocks.StructBlock', [[
                            ('pupitre', 0), ('custom_pupitre', 1), ('audio', 2), ('comment', 3),
                        ]], {}),
                    },
                    null=True,
                    use_json_field=True,
                )),
                ('additional_files', wagtail.fields.StreamField(
                    [('section', 9)],
                    blank=True,
                    block_lookup={
                        0: ('wagtail.blocks.CharBlock', (), {'required': True}),
                        1: ('wagtail.blocks.ChoiceBlock', [], {'choices': [
                            ('Tutti', 'Tutti'), ('Soprano', 'Soprano'),
                            ('Alto', 'Alto'), ('Ténor', 'Ténor'), ('Basse', 'Basse'),
                        ], 'required': False}),
                        2: ('wagtail.blocks.CharBlock', (), {
                            'help_text': 'Entrer une valeur ici annule le champ ci-dessus.',
                            'max_length': 30, 'required': False,
                        }),
                        3: ('wagtail.documents.blocks.DocumentChooserBlock', (), {
                            'help_text': 'Sélectionnez un fichier audio', 'required': False,
                        }),
                        4: ('wagtail.blocks.CharBlock', (), {
                            'help_text': 'Un petit mot ?', 'max_length': 255, 'required': False,
                        }),
                        5: ('wagtail.blocks.StructBlock', [[
                            ('pupitre', 1), ('custom_pupitre', 2), ('audio', 3), ('comment', 4),
                        ]], {'required': False}),
                        6: ('wagtail.blocks.ListBlock', (5,), {}),
                        7: ('wagtail.documents.blocks.DocumentChooserBlock', (), {'required': False}),
                        8: ('wagtail.blocks.ListBlock', (7,), {}),
                        9: ('wagtail.blocks.StructBlock', [[
                            ('title', 0), ('audios', 6), ('files', 8),
                        ]], {}),
                    },
                    null=True,
                    use_json_field=True,
                )),
            ],
            options={
                'verbose_name': 'Morceau',
                'verbose_name_plural': 'Morceaux',
            },
            bases=('wagtailcore.page',),
        ),

        migrations.CreateModel(
            name='RepertoireItem',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True, primary_key=True, serialize=False, verbose_name='ID',
                )),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('comment', models.TextField(blank=True, verbose_name='Commentaire')),
                ('piece', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='repertoire_items',
                    to='music.piece',
                    verbose_name='Morceau',
                )),
                ('repertoire', modelcluster.fields.ParentalKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='items',
                    to='music.repertoirepage',
                )),
                ('tags', taggit.managers.TaggableManager(
                    blank=True,
                    help_text='A comma-separated list of tags.',
                    through='taggit.TaggedItem',
                    to='taggit.Tag',
                    verbose_name='Tags',
                )),
            ],
            options={
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]
