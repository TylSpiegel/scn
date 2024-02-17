
"""
class CalendrierPage(Page):
	introduction = models.TextField(help_text="Text to describe the page", blank=True)
	image = models.ForeignKey(
		'wagtailimages.Image',
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name='+'
	)
	content_panels = Page.content_panels + [
		FieldPanel("introduction"),
		FieldPanel('image'),
	]
	subpage_types = ["CalendrierEventPage", "CalendrierPublicEventPage"]
	parent_page_types = ["ChoristesIndexPage"]
	max_count = 1

	def children(self):
		return self.get_children().specific().live()

	def get_events_json(self):
		events = CalendrierEventPage.objects.live()
		public_events = CalendrierPublicEventPage.objects.live()
		formatted_events = []
		for event in events:
			current_event = {
				'title': event.title,
				'start': event.date.isoformat()
				if isinstance(event.date, date)
				else event.date
			}
			formatted_events.append(current_event)
		for public_event in public_events:
			current_event = {
				'title': public_event.title,
				'start': public_event.date.isoformat()
				if isinstance(public_event.date, date)
				else public_event.date
			}
			formatted_events.append(current_event)
		return json.dumps(formatted_events)

	def get_context(self, request):
		context = super().get_context(request)
		context['events_json'] = self.get_events_json()
		return context


class CalendrierEventPage(Page):
	date = models.DateField("Post date")
	intro = models.CharField(max_length=250)
	body = RichTextField(blank=True)

	content_panels = Page.content_panels + [
		FieldPanel('date'),
		FieldPanel('intro'),
		FieldPanel('body'),
	]
	parent_page_types = ["CalendrierPage"]
	subpage_types = []


class CalendrierPublicEventPage(Page):
	date = models.DateField("Post date")
	intro = models.CharField(max_length=250)
	body = RichTextField(blank=True)
	content_panels = Page.content_panels + [
		FieldPanel('date'),
		FieldPanel('intro'),
		FieldPanel('body'),
	]
	parent_page_types = ["CalendrierPage"]
	subpage_types = []
"""
