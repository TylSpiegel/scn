import factory
from factory.django import DjangoModelFactory
from faker import Faker
from datetime import datetime, timedelta
import random

from apps.community.models import Choriste, Event, Role

fake = Faker('fr_FR')


class RoleFactory(DjangoModelFactory):
    class Meta:
        model = Role

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


class EventFactory(DjangoModelFactory):
    class Meta:
        model = Event

    name = factory.Faker('sentence', nb_words=3)
    start_date = factory.LazyAttribute(
        lambda x: datetime.now() + timedelta(days=random.randint(1, 90))
    )
    end_date = factory.LazyAttribute(
        lambda obj: obj.start_date + timedelta(hours=2)
    )
    is_repetition = factory.Faker('boolean')
    pupitre = factory.Iterator(['Tutti', 'Soprano', 'Alto', 'Ténor', 'Basse'])
