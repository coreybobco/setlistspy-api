from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from setlistspy.app.factories import *


class SetSpyApiTestCase(APITestCase):

    def setUp(self, *args, **kwargs):
        self.user = UserFactory()
        self.client = APIClient()
        self.client.credentials(
            HTTP_AUTHORIZATION='Token ' + self.user.auth_token.key
        )
        super().setUp(*args, **kwargs)


class ArtistsApiTestCase(SetSpyApiTestCase):
    list_url = reverse('artist-list')

    def test_list(self):
        for i in range(3):
            ArtistFactory()
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK, msg=res.data)
        self.assertEqual(res.data['count'], 3)

    def test_retrieve(self):
        artist = ArtistFactory()
        url = reverse('artist-detail', kwargs={'pk': artist.pk.hex})
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK, msg=res.data)

    def test_filters(self):
        artist1 = ArtistFactory(name='Aphex Twin')
        artist2 = ArtistFactory(name='AFX')

        # By name
        res = self.client.get(self.list_url, {'name': artist1.name}, format='json')
        self.assertEqual(res.data['count'], 1)

        ArtistFactory(name='Basic Channel')
        res = self.client.get(self.list_url, {'name__in': f'{artist1.name},{artist2.name}'}, format='json')
        self.assertEqual(res.data['count'], 2)


class DJsApiTestCase(SetSpyApiTestCase):
    list_url = reverse('dj-list')

    def test_list(self):
        for i in range(3):
            DJFactory()
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK, msg=res.data)
        self.assertEqual(res.data['count'], 3)

    def test_retrieve(self):
        dj = DJFactory()
        url = reverse('dj-detail', kwargs={'pk': dj.pk.hex})
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK, msg=res.data)

    def test_filters(self):
        dj1 = DJFactory(name='Jeff Mills')
        dj2 = DJFactory(name='Surgeon')
        dj3 = DJFactory(name='Bill Converse')
        TrackPlayFactory(setlist__dj=dj1)
        TrackPlayFactory(setlist__dj=dj2)

        # By name
        res = self.client.get(self.list_url, {'name': dj1.name}, format='json')
        self.assertEqual(res.data['count'], 1)
        res = self.client.get(self.list_url, {'name__in': f'{dj1.name},{dj2.name}'}, format='json')
        self.assertEqual(res.data['count'], 2)

        # By labels they play
        dj_filter = {'setlists__track_plays__label__name': dj1.setlists.first().track_plays.first().label.name}
        res = self.client.get(self.list_url, dj_filter, format='json')
        self.assertEqual(res.data['count'], 1)
        # Use complex filter to support value with commas in it
        condition1 = f'(setlists__track_plays__label__name={dj1.setlists.first().track_plays.first().label.name})'
        condition2 = f'(setlists__track_plays__label__name={dj2.setlists.first().track_plays.first().label.name})'
        dj_filter = {'filters': f'{condition1}|{condition2}'}
        res = self.client.get(self.list_url, dj_filter, format='json')
        self.assertEqual(res.data['count'], 2)


class LabelsApiTestCase(SetSpyApiTestCase):
    list_url = reverse('label-list')

    def test_list(self):
        for i in range(3):
            LabelFactory()
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK, msg=res.data)
        self.assertEqual(res.data['count'], 3)

    def test_retrieve(self):
        label = LabelFactory()
        url = reverse('label-detail', kwargs={'pk': label.pk.hex})
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK, msg=res.data)

    def test_filters(self):
        label1 = LabelFactory(name='Warp Records')
        label2 = LabelFactory(name='PAN Records')
        TrackPlayFactory(label=label1)
        TrackPlayFactory(label=label2)
        LabelFactory(name='L.I.E.S. Records')

        # By name
        res = self.client.get(self.list_url, {'name': label1.name}, format='json')
        self.assertEqual(res.data['count'], 1)
        res = self.client.get(self.list_url, {'name__in': f'{label1.name},{label2.name}'}, format='json')
        self.assertEqual(res.data['count'], 2)

        # By DJ name
        res = self.client.get(self.list_url,
                              {'track_plays__setlist__dj__name': label1.track_plays.first().setlist.dj.name},
                              format='json')
        self.assertEqual(res.data['count'], 1)
        label_filter = {'filters': f'(track_plays__setlist__dj__name={label1.track_plays.first().setlist.dj.name})|' +
                                   f'(track_plays__setlist__dj__name={label2.track_plays.first().setlist.dj.name})'}
        res = self.client.get(self.list_url, label_filter, format='json')
        self.assertEqual(res.data['count'], 2)


class TracksApiTestCase(SetSpyApiTestCase):
    list_url = reverse('track-list')

    def test_list(self):
        for i in range(3):
            TrackFactory()
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK, msg=res.data)
        self.assertEqual(res.data['count'], 3)

    def test_retrieve(self):
        track = TrackFactory()
        url = reverse('track-detail', kwargs={'pk': track.pk.hex})
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK, msg=res.data)

    def test_filters(self):
        track1 = TrackFactory(artist__name='Aphex Twin')
        track2 = TrackFactory(artist__name='AFX')
        TrackPlayFactory(track=track1, set_order=1,
                         label__name="Comma, Semicolon, and Period Records")
        TrackPlayFactory(track=track2, set_order=2)
        track3 = TrackFactory(artist__name='Basic Channel')  # extra track which shouldn't return in results
        TrackPlayFactory(track=track3, set_order=3)

        # By title
        res = self.client.get(self.list_url, {'title': track1.title}, format='json')
        self.assertEqual(res.data['count'], 1)
        res = self.client.get(self.list_url, {'title__in': f'{track1.title},{track2.title}'}, format='json')
        self.assertEqual(res.data['count'], 2)

        # By artist name
        res = self.client.get(self.list_url, {'artist__name': track1.artist.name}, format='json')
        self.assertEqual(res.data['count'], 1)
        res = self.client.get(self.list_url, {'artist__name__in': f'{track1.artist.name},{track2.artist.name}'},
                              format='json')
        self.assertEqual(res.data['count'], 2)

        # By setlist title
        res = self.client.get(self.list_url, {'setlists__title': track1.setlists.first().title}, format='json')
        self.assertEqual(res.data['count'], 1)
        track_filter = f'{track1.setlists.first().title},{track2.setlists.first().title}'
        res = self.client.get(self.list_url, {'setlists__title__in': track_filter}, format='json')
        self.assertEqual(res.data['count'], 2)

        # By setlist dj name
        res = self.client.get(self.list_url, {'setlists__dj__name': track1.setlists.first().dj.name}, format='json')
        self.assertEqual(res.data['count'], 1)
        track_filter = {'setlists__dj__name__in': f'{track1.setlists.first().dj.name},' +
                                                  f'{track2.setlists.first().dj.name}'}
        res = self.client.get(self.list_url, track_filter, format='json')
        self.assertEqual(res.data['count'], 2)

        # By label name
        res = self.client.get(self.list_url, {'plays__label__name': track1.plays.first().label.name}, format='json')
        self.assertEqual(res.data['count'], 1)
        # Use complex filter to support value with commas in it
        track_filter = {'filters': f'(plays__label__name={track1.plays.first().label.name})|' + \
                                   f'(plays__label__name={track2.plays.first().label.name})'}
        res = self.client.get(self.list_url, track_filter, format='json')
        self.assertEqual(res.data['count'], 2)

        # By set order
        res = self.client.get(self.list_url, {'plays__set_order': track1.plays.first().set_order}, format='json')
        self.assertEqual(res.data['count'], 1)
        track_filter = {'plays__set_order__in': f'{track1.plays.first().set_order},{track2.plays.first().set_order}'}
        res = self.client.get(self.list_url, track_filter, format='json')
        self.assertEqual(res.data['count'], 2)

    def test_stats(self):
        url = reverse('track-stats')

        tracks = []
        for i in range(10):
            tracks.append(TrackFactory())

        for i in range(3):
            setlist = SetlistFactory()
            for i in range(10):
                TrackPlayFactory(track=tracks[i], setlist=setlist, set_order=i)

        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for i in range(10):
            self.assertEqual(len(res.data[i]['setlists']), 3)

        url = reverse('track-stats', kwargs={'pk': tracks[0].pk.hex})
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['setlists']), 3)

class TrackPlaysApiTestCase(SetSpyApiTestCase):
    list_url = reverse('trackplay-list')

    def test_list(self):
        for i in range(3):
            TrackPlayFactory()
        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK, msg=res.data)
        self.assertEqual(res.data['count'], 3)

    def test_retrieve(self):
        play = TrackPlayFactory()
        url = reverse('trackplay-detail', kwargs={'pk': play.pk.hex})
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK, msg=res.data)

    def test_filters(self):
        setlist = SetlistFactory()
        play1 = TrackPlayFactory(set_order=1, label__name="Comma, Semicolon, and Period Records")
        play2 = TrackPlayFactory(set_order=2)
        TrackPlayFactory(set_order=7)  # extra track which shouldn't return in results

        # By label name
        res = self.client.get(self.list_url, {'label__name': play1.label.name}, format='json')
        self.assertEqual(res.data['count'], 1)
        # Use complex filter to support value with commas in it
        play_filter = {'filters': f'(label__name={play1.label.name})|(label__name={play2.label.name})'}
        res = self.client.get(self.list_url, play_filter, format='json')
        self.assertEqual(res.data['count'], 2)

        # By track title
        res = self.client.get(self.list_url, {'track__title': play1.track.title}, format='json')
        self.assertEqual(res.data['count'], 1)
        res = self.client.get(self.list_url, {'track__title__in': f'{play1.track.title},{play2.track.title}'},
                              format='json')
        self.assertEqual(res.data['count'], 2)

        # By track artist name
        res = self.client.get(self.list_url, {'track__artist__name': play1.track.artist.name}, format='json')
        self.assertEqual(res.data['count'], 1)
        play_filter = {'track__artist__name__in': f'{play1.track.artist.name},{play2.track.artist.name}'}
        res = self.client.get(self.list_url, play_filter, format='json')
        self.assertEqual(res.data['count'], 2)

        # By setlist title
        res = self.client.get(self.list_url, {'setlist__title': play1.setlist.title}, format='json')
        self.assertEqual(res.data['count'], 1)
        track_filter = {'setlist__title__in': f'{play1.setlist.title},{play2.setlist.title}'}
        res = self.client.get(self.list_url, track_filter, format='json')
        self.assertEqual(res.data['count'], 2)

        # By setlist dj name
        res = self.client.get(self.list_url, {'setlist__dj__name': play1.setlist.dj.name}, format='json')
        self.assertEqual(res.data['count'], 1)
        track_filter = {'setlist__dj__name__in': f'{play1.setlist.dj.name},{play2.setlist.dj.name}'}
        res = self.client.get(self.list_url, track_filter, format='json')
        self.assertEqual(res.data['count'], 2)

        # By set order
        res = self.client.get(self.list_url, {'set_order': play1.set_order}, format='json')
        self.assertEqual(res.data['count'], 1)
        track_filter = {'set_order__in': f'{play1.set_order},{play2.set_order}'}
        res = self.client.get(self.list_url, track_filter, format='json')
        self.assertEqual(res.data['count'], 2)


class SetlistsApiTestCase(SetSpyApiTestCase):
    list_url = reverse('setlist-list')

    def test_list(self):
        # Create 3 setlists
        for i in range(3):
            setlist = SetlistFactory()

        res = self.client.get(self.list_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK, msg=res.data)
        self.assertEqual(res.data['count'], 3)

    def test_retrieve(self):
        setlist = SetlistFactory()
        for i in range(5):
            track = TrackFactory()
            TrackPlayFactory(track=track, setlist=setlist, set_order=i)

        url = reverse('setlist-detail', kwargs={'pk': setlist.pk.hex})
        res = self.client.get(url, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK, msg=res.data)

    def test_filters(self):
        setlist1 = SetlistFactory(b2b=False)
        setlist2 = SetlistFactory(b2b=False)
        setlist3 = SetlistFactory(b2b=True)
        for i in range(3):
            TrackPlayFactory(setlist=setlist1)

        # By title
        res = self.client.get(self.list_url, {'title': setlist1.title}, format='json')
        self.assertEqual(res.data['count'], 1)
        res = self.client.get(self.list_url, {'title__in': f'{setlist1.title},{setlist2.title}'}, format='json')
        self.assertEqual(res.data['count'], 2)

        # By dj name
        res = self.client.get(self.list_url, {'dj__name': setlist1.dj.name}, format='json')
        self.assertEqual(res.data['count'], 1)
        setlist_filter = {'dj__name__in': f'{setlist1.dj.name},{setlist2.dj.name}'}
        res = self.client.get(self.list_url, setlist_filter, format='json')
        self.assertEqual(res.data['count'], 2)

        # By mixesdb id
        res = self.client.get(self.list_url, {'mixesdb_id': setlist1.mixesdb_id}, format='json')
        self.assertEqual(res.data['count'], 1)
        setlist_filter = {'mixesdb_id__in': f'{setlist1.mixesdb_id},{setlist2.mixesdb_id}'}
        res = self.client.get(self.list_url, setlist_filter, format='json')
        self.assertEqual(res.data['count'], 2)

        # By B2B
        res = self.client.get(self.list_url, {'b2b': True}, format='json')
        self.assertEqual(res.data['count'], 1)
        res = self.client.get(self.list_url, {'b2b': False}, format='json')
        self.assertEqual(res.data['count'], 2)

        # By empty
        res = self.client.get(self.list_url, {'empty': True}, format='json')
        self.assertEqual(res.data['count'], 2)
        res = self.client.get(self.list_url, {'empty': False}, format='json')
        self.assertEqual(res.data['count'], 1)

