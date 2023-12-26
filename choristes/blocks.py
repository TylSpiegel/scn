from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel


class AudioDocumentBlock(blocks.StructBlock):
	CHOICES = (
		('Tutti', 'Tutti'),
		('Soprano', 'Soprano'),
		('Alto', 'Alto'),
		('Ténor', 'Ténor'),
		('Basse', 'Basse'),
	)
	pupitre = blocks.ChoiceBlock(
		choices=CHOICES,
		default='Tutti',
		required=False
	)
	custom_pupitre = blocks.CharBlock(
		max_length=30,
		required=False,
		help_text="Entrer une valeur ici annule le champ ci-dessus.",
	)
	audio = DocumentChooserBlock(required=False, help_text="Sélectionnez un fichier audio")
	comment = blocks.CharBlock(required=False, max_length=255, help_text="Un petit mot ?")

	def clean(self, value):
		cleaned_data = super().clean(value)
		pupitre = cleaned_data.get('pupitre')
		custom = cleaned_data.get('custom_pupitre')

		if custom:
			cleaned_data['pupitre'] = custom
		elif not pupitre:
			raise ValidationError('Vous devez sélectionner une option ou fournir une valeur personnalisée.')

		return cleaned_data

	class Meta:
		icon = "media"
		template = "blocks/audio_file.html"
		form_classname = "struct-block"

		edit_handler = MultiFieldPanel([
			FieldRowPanel([
				FieldPanel('pupitre', classname="col4"),
				FieldPanel('custom_pupitre', classname="col8"),
			]),
			FieldPanel('audio'),
			FieldPanel('comment'),
		], heading="Détails de l'Audio Document")


class AdditionalFilesBlock(blocks.StructBlock):
	title = blocks.CharBlock(required=True)
	audios = blocks.ListBlock(
		AudioDocumentBlock(required=False)
	)
	files = blocks.ListBlock(
		DocumentChooserBlock(required=False)
	)


class MorceauBlock(blocks.StructBlock):
	titre = blocks.CharBlock(required=True, max_length=255, help_text="Entrez le titre")
	texte = blocks.TextBlock(required=True, help_text="Entrez le texte principal")
	document_pdf = DocumentChooserBlock(required=True, help_text="Sélectionnez un document PDF")

	documents_audio = blocks.ListBlock(
		AudioDocumentBlock(),
		min_num=0,
		max_num=4,
		help_text="Ajoutez entre 1 et 4 fichiers audio"
	)

	champs_texte_supplementaires = blocks.StreamBlock(
		[('texte_supplementaire', blocks.TextBlock())],
		help_text="Ajoutez un nombre indéterminé de champs texte",
		required=False
	)

	class Meta:
		icon = "form"
		template = "blocks/morceau.html"
