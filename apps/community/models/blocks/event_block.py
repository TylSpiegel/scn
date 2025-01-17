


class EventBlock(blocks.StructBlock):
   event = blocks.SnippetChooserBlock('Event')
   display_style = blocks.ChoiceBlock(
       choices=[
           ('mini', 'Version courte'),
           ('normal', 'Version normale'), 
           ('full', 'Version complète'),
       ],
       default='normal',
       label="Style d'affichage"
   )
   show_comments = blocks.BooleanBlock(
       required=False, 
       default=False,
       label="Afficher les commentaires"
   )

   class Meta:
       template = "components/event_%(display_style)s.html"
       icon = "date"