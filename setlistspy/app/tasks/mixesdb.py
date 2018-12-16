import hashlib

import urllib.parse
import re
from collections import defaultdict

from django.utils import timezone
import xmltodict
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from .base import shared_task
from setlistspy.app.models import Artist, DJ, Label, Setlist, Track, TrackPlay


class UnchangedData(Exception):
    pass

def check_xml_md5(dj, response_xml):
    """Check if XML md5 has changed since last time this script ran"""
    if response_xml:
        response_xml_md5 = hashlib.md5(response_xml.encode('utf-8')).hexdigest()
        if not dj.xml_md5 == response_xml_md5:
            # Setlists and related model instances require checking for updates
            dj.xml_md5 = response_xml_md5
    dj.last_check_time = timezone.now()
    dj.save()

def extract_setlist_features(raw_setlist_datum, dj):
    if not(raw_setlist_datum.get('title', None) and raw_setlist_datum['title'][0:5] != "File:"):
        # Link to a mix and not a setlist
        return None

    # Extract and divide all the text from the li's in the "Tracklist" section of the wiki page for the setlist
    tracklist_lines = raw_setlist_datum['revision']['text']['#text'].split("\n")
    tracklist_lines = list(map(lambda line: line.strip(), tracklist_lines))

    setlist_features = {
        'mixesdb_id': int(raw_setlist_datum['id']),
        'title': raw_setlist_datum['title'],
        'mixesdb_mod_time': raw_setlist_datum['revision']['timestamp'],
        'xml_sha1': raw_setlist_datum['revision']['sha1'],
        'b2b': True if "[[Category:Various]]" in tracklist_lines else False
    }

    if setlist_features['b2b']:
        try:
            # Try to only get the tracks under this DJ's header if it's a B2B set.
            tracklist_lines = tracklist_lines[(1 + tracklist_lines.index(";" + dj.name)):]
        except ValueError:
            # Imperfect data -- not possible to tell which of two DJs played the track
            pass

    tracklist_data = []
    for tracklist_line in tracklist_lines:
        track_features = extract_track_features(setlist_features, tracklist_line)
        if track_features:
            tracklist_data.append(track_features)
    setlist_features['tracklist_data'] = tracklist_data
    return setlist_features

def extract_track_features(setlist_features, tracklist_line):
    """Determine if a line contains a track and, if it is, extract and clean the artist, title, and label data"""
    try:
        tracklist_line = tracklist_line.decode('utf-8')
    except AttributeError:
        # Doesn't need decoding
        pass
    track_features = {}
    # Pattern generally supports {Artist} - {title} [{Label}]
    pattern = re.compile('(?:\[[\d:\?]*\])?[\s]?(?!\?)([^\[]*) - ([^\[]*)(\[.*])?$')

    if setlist_features['b2b'] and (len(tracklist_line) == 0 or tracklist_line[0] in ["[", ";"]):
        return None
    match = pattern.match(tracklist_line.strip("# ").strip(''))
    if match:
        artist_name = match.group(1).title()
        if " - " in artist_name:
            # Fringe case
            text_components = artist_name.split(" - ")
            track_features['artist_name'] = text_components[0].strip().title()[:255]
            track_features['title'] = text_components[1].strip().title()[:255]
            try:
                track_features['label_name'] = match.group(2).strip("[( )]").split("-")[0].strip().title()[:255]
            except AttributeError:
                track_features['label_name'] = None
        else:
            track_features['artist_name'] = artist_name[:255]
            track_features['title'] = match.group(2).strip()[:255]
            try:
                track_features['label_name'] = match.group(3).strip("[( )]").split("-")[0].strip().title()[:255]
            except AttributeError:
                track_features['label_name'] = None
    else:
        if " - " in tracklist_line and len(tracklist_line) > 7 and tracklist_line[0] not in ["[", "{", "|", "="] \
                and "file details" not in tracklist_line.lower():
            print("irregular line:")
            try:
                print(tracklist_line.encode('utf-8', 'replace'))
            except AttributeError:
                # Doesn't need decoding
                print(tracklist_line)
                pass
        return None
    return track_features

def save_setlists(raw_setlist_data, dj):
    """Save setlists to database"""
    # If there are 0-1 setlists, convert to list for iteration
    raw_setlist_data = [raw_setlist_data] if not isinstance(raw_setlist_data, list) else raw_setlist_data
    unchanged_data = UnchangedData()
    for raw_setlist_datum in raw_setlist_data:
        setlist_features = extract_setlist_features(raw_setlist_datum, dj)
        if setlist_features:
            try:
                setlist = Setlist.objects.get(dj=dj, mixesdb_id=setlist_features['mixesdb_id'])
                if setlist.xml_sha1 != setlist_features['xml_sha1']:
                    setlist.title = setlist_features['title']
                    setlist.mixesdb_mod_time = setlist_features['mixesdb_mod_time']
                    setlist.xml_sha1 = setlist_features['xml_sha1']
                    setlist.b2b = setlist_features['b2b']
                    setlist.save()
                else:
                    raise unchanged_data
            except Setlist.DoesNotExist:
                setlist = Setlist.objects.create(
                    dj=dj,
                    mixesdb_id=setlist_features['mixesdb_id'],
                    title=setlist_features['title'],
                    mixesdb_mod_time=setlist_features['mixesdb_mod_time'],
                    xml_sha1=setlist_features['xml_sha1'],
                    b2b=setlist_features['b2b']
                )
            except UnchangedData:
                continue
            save_tracks.delay(setlist_features['tracklist_data'], setlist.pk)


@shared_task
def save_tracks(tracklist_data, setlist_id):
    """Save tracks, artists, labels, and trackplays to database"""
    setlist = Setlist.objects.get(pk=setlist_id)
    set_order = 1
    for track_features in tracklist_data:
        artist, created = Artist.objects.get_or_create(name=track_features['artist_name'])
        track, created = Track.objects.get_or_create(artist=artist, title=track_features['title'])
        if track_features.get('label_name', None):
            label, created = Label.objects.get_or_create(name=track_features['label_name'])
        else:
            label = None
        try:
            trackplay = TrackPlay.objects.get(track=track, setlist=setlist)
            trackplay.set_order = set_order
            trackplay.label = label
            trackplay.save()
        except TrackPlay.DoesNotExist:
            TrackPlay.objects.create(
                track=track,
                setlist=setlist,
                set_order=set_order,
                label=label
            )
        set_order += 1

@shared_task
def process_setlists_xml(response_xml, dj_id):
    dj = DJ.objects.get(id=dj_id)
    check_xml_md5(dj, response_xml)
    setlists_xml_dict = xmltodict.parse(response_xml) \
        .get('mediawiki', defaultdict(lambda: None)).get('page')
    if setlists_xml_dict:
        save_setlists(setlists_xml_dict, dj)