import factory
from factory.django import DjangoModelFactory
from faker import Faker
from datetime import datetime, timedelta
import random

# Importer depuis le module choristes
from choristes.models import Choriste, Evenement, ChoirRole

fake = Faker('fr_FR')

class ChoirRoleFactory(DjangoModelFactory):
    class Meta:
        model = ChoirRole
    
    name = factory.Iterator(['Chef de chœur', 'Président', 'Trésorier', 'Secrétaire'])

class ChoristeFactory(DjangoModelFactory):
    class Meta:
        model = Choriste
    
    name = factory.LazyAttribute(lambda x: fake.name())
    pupitre = factory.Iterator(['Soprano', 'Alto', 'Ténor', 'Basse'])
    mail = factory.LazyAttribute(lambda x: fake.email())
    phone = factory.LazyAttribute(lambda x: fake.phone_number())
    birthdate = factory.LazyAttribute(lambda x: fake.date_of_birth(minimum_age=18, maximum_age=80))
    active = True
    
    @factory.post_generation
    def choir_functions(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for role in extracted:
                self.choir_functions.add(role)

class EvenementFactory(DjangoModelFactory):
    class Meta:
        model = Evenement
    
    name = factory.Faker('sentence', nb_words=3)
    start_date = factory.LazyAttribute(
        lambda x: datetime.now() + timedelta(days=random.randint(1, 90))
    )
    end_date = factory.LazyAttribute(
        lambda obj: obj.start_date + timedelta(hours=2)
    )
    is_repetition = factory.Faker('boolean')
    pupitre = factory.Iterator(['Tous', 'Soprano', 'Alto', 'Ténor', 'Basse'])
