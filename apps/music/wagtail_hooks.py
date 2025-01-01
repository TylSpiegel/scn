from wagtail.contrib.modeladmin.options import (
    ModelAdmin, 
    modeladmin_register
)
from .models.entities.section import Section

class SectionAdmin(ModelAdmin):
    """Admin interface for managing choir sections."""
    
    model = Section
    menu_label = 'Pupitres'  
    menu_icon = 'group'  
    menu_order = 200  
    add_to_settings_menu = True  # Will appear in the Settings sub-menu
    exclude_from_explorer = False # Appears in Wagtail's explorer view
    
    # List display configuration
    list_display = ('name', 'color_display', 'description')
    list_filter = ('name',)
    search_fields = ('name', 'description')
    ordering = ['name']
    
    # Custom methods for display
    def color_display(self, obj):
        """Display color as a colored square in the admin."""
        return format_html(
            '<div style="background-color: {}; width: 20px; height: 20px; border-radius: 4px; border: 1px solid #ccc;"></div>',
            obj.color
        )
    color_display.short_description = 'Couleur'
    
    # Panels configuration for edit view
    panels = [
        FieldPanel('name'),
        NativeColorPanel('color'),
        FieldPanel('description'),
    ]
    
    # Additional configuration for export functionality
    list_export = ('name', 'color', 'description')
    export_filename = 'sections-export'

# Register the admin interface
modeladmin_register(SectionAdmin)