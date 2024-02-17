from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register
from .models import Choriste, Evenement

class ChoristesModelAdmin(ModelAdmin):
    model = Choriste
    menu_label = 'Choriste'
    menu_icon = 'placeholder'
    menu_order = 290
    add_to_settings_menu = True
    exclude_from_explorer = False
    list_display = ('name')
    search_fields = ('name')

class EventModelAdmin(ModelAdmin):
    model = Evenement
    menu_label = 'Evénement'
    menu_icon = 'placeholder'
    menu_order = 291
    add_to_settings_menu = True
    exclude_from_explorer = False
    list_display = ('name', 'description', 'pupitre', 'start_date')
    search_fields = ('name', 'start_date')


modeladmin_register(ChoristesModelAdmin)
modeladmin_register(EventModelAdmin)
