# models.py
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel

class CalendarPage(Page):
   name = models.CharField("Titre", max_length=100)
   description = RichTextField("Description", blank=True)
   
   content = StreamField([
       ('rich_text', blocks.RichTextBlock()),
       ('events_list', EventsListBlock()),
       ('calendar', CalendarBlock()),
   ], use_json_field=True)

   content_panels = Page.content_panels + [
       MultiFieldPanel([
           FieldPanel('name'),
           FieldPanel('description'),
       ], heading="En-tête"),
       FieldPanel('content'),
   ]