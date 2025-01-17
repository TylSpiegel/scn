


class EventsListBlock(blocks.StructBlock):
   """
	EventsListBlock - A StreamField block to display filtered event lists

	Features:
	- Configurable max events display
	- Date range filtering
	- Event type filtering
	- Display style options (mini/normal/full)
	- Past events toggle
	- Custom title and description

	Usage:
	content = StreamField([
	('events_list', EventsListBlock()),
	], use_json_field=True)
	"""

   name = blocks.CharBlock(required=True, label="Titre")
   description = blocks.RichTextBlock(required=False, label="Description")
   max_events = blocks.IntegerBlock(
       default=5, 
       min_value=1, 
       required=True, 
       label="Nombre d'événements maximum"
   )
   date_start = blocks.DateBlock(required=False, label="Date de début")
   date_end = blocks.DateBlock(required=False, label="Date de fin")
   event_types = blocks.ListBlock(
       blocks.ChoiceBlock(
           choices=lambda: [(et.id, et.name) for et in EventType.objects.all()]
       ),
       required=False,
       label="Types d'événements"
   )
   display_style = blocks.ChoiceBlock(
       choices=[
           ('mini', 'Version courte'),
           ('normal', 'Version normale'),
           ('full', 'Version complète'),
       ],
       default='normal',
       label="Style d'affichage"
   )
   show_past = blocks.BooleanBlock(
       default=False, 
       required=False, 
       label="Afficher les événements passés"
   )

   def get_context(self, value, parent_context=None):
       context = super().get_context(value, parent_context)
       events = Event.objects.all()
       
       if value['date_start']:
           events = events.filter(start_date__gte=value['date_start'])
       if value['date_end']:
           events = events.filter(start_date__lte=value['date_end'])
       if value['event_types']:
           events = events.filter(event_type_id__in=value['event_types'])
       if not value['show_past']:
           events = events.filter(start_date__gte=timezone.now().date())
           
       context['events'] = events[:value['max_events']]
       return context

   class Meta:
       template = "blocks/events_list.html"
       icon = "date"