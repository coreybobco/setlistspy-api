import datetime
from hashlib import sha1
from random import randint
from uuid import uuid4
from django.utils import timezone
from django.contrib.auth.models import User
import factory.fuzzy
from faker import Faker


class DJFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'app.DJ'
        django_get_or_create = ('url',)

    name = factory.Faker('name')
    url = factory.Faker('url')
    xml_md5 = factory.fuzzy.FuzzyAttribute(lambda: uuid4().hex)
    last_check_time = factory.fuzzy.FuzzyAttribute(lambda: timezone.now())


class SetlistFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'app.setlist'

    dj = factory.SubFactory(DJFactory)
    title = factory.LazyAttribute(lambda obj: f'{obj.dj.name} @ {Faker().city()} ' +
                                              f'({(timezone.now() - datetime.timedelta(days=randint(1,1000))).date()})')
    mixesdb_id = factory.fuzzy.FuzzyInteger(1, 99999)
    mixesdb_mod_time = factory.fuzzy.FuzzyAttribute(lambda: timezone.now())
    xml_sha1 = factory.fuzzy.FuzzyAttribute(lambda: sha1(f'{randint(0,100000)}'
                                                         .encode('utf-8')).hexdigest()[:31])


class ArtistFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'app.Artist'
        django_get_or_create = ('name',)

    name = factory.Faker('name')


class LabelFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'app.Label'
        django_get_or_create = ('name',)

    name = factory.LazyAttribute(lambda obj: f'{Faker().company()} Records')
    discogs_id = factory.fuzzy.FuzzyInteger(1, 99999)


class TrackFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'app.Track'

    artist = factory.SubFactory(ArtistFactory)
    title = factory.LazyAttribute(lambda obj: " ".join(Faker().words()).title())

    @factory.post_generation
    def setlists(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for setlist in extracted:
                TrackPlayFactory(track=self, setlist=setlist)


class TrackPlayFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = 'app.TrackPlay'

    track = factory.SubFactory(TrackFactory)
    setlist = factory.SubFactory(SetlistFactory)
    set_order = factory.fuzzy.FuzzyInteger(1, 50)
    label = factory.SubFactory(LabelFactory)


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User

    username = factory.lazy_attribute(lambda obj: uuid4().hex)
    password = factory.PostGenerationMethodCall('set_password', Faker().word())
    is_active = True