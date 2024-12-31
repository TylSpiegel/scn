from django.db import models
from django.db.models import TextField
from django.forms import CharField
from wagtail.admin.panels import FieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

PUPITRES_CHOICES = (
    ('Tutti', 'Tutti'),
    ('Soprano', 'Soprano'),
    ('Alto', 'Alto'),
    ('Ténor', 'Ténor'),
    ('Basse', 'Basse'),
    ('Autre', 'Autre'),
)

PUPITRES_COLORS = {
    'Tutti': '#007BFF',
    'Soprano': '#DC3545',
    'Alto': '#FFC107',
    'Ténor': '#28A745',
    'Basse': '#17A2B8',
    'Autre': '#6C757D',
}

"""
TODO: Create model for sections
"""