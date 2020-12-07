import sys, logging, musicbrainzngs, json
from library.models import Song
from django.db import models

# logger for logging debug information
logger = logging.getLogger("mylogger")

default_image = "./assets/img/default/note.png"

""" Musicbrainz metadata retrieval | Database updating """

def add_song_musicbrainz(song_metadata, user):
    """
        Creates or updates song with given information for specific user.
        If song exists, created value is false. Otherwise, the song exists and created is true.
    """
    # If song already exists, update all information
    try:
        album, release_date, image_path = _determine_first_release(song_metadata['song']['albums'])
        albums = get_possible_albums(song_metadata['song']['albums'])
        new, created = Song.objects.update_or_create(
                title = song_metadata['song']['title'],
                artist = song_metadata['song']['artists']['artist'],
                file_location = song_metadata['song']['file_path'], # primary key
                defaults={
                    "title": song_metadata['song']['title'],
                    "album": albums,
                    "artist": song_metadata['song']['artists']['artist'],
                    "profile": user.profile,
                    "release_date": release_date,
                    "detection_method": "Musicbrains",
                    "album_artwork": image_path,
                    "json_item": json.dumps(song_metadata),
                    "file_location": song_metadata['song']['file_path']})
        if (created):
            new.save()
            #logger.info("New song, creating...")
        else:
            new.save()
                #logger.info("Old song, updating...")
            #logger.info("Done.")
    except Exception as e:
       logger.error(f"Error while adding musicbrainz song instance to database: {e}")

def _determine_first_release(albums):
    releases = []
    #logger.info(albums)
    album = None
    release_date = None
    for album in albums.values():
        for item in album:
            if (album == None and release_date == None):
                album = item['album']
                release_date = item['album_musicbrains_id']
            image = __musicbrainz_album_cover_grab(item['album'], item['album_musicbrains_id'])
            if not image == default_image:
                return item['album'], item['release_date'], image
    return album, release_date, image

def get_possible_albums(albums_all):
    albums = []
    for item in albums_all.values():
        for album in item:
            if album['album'] not in albums:
                albums.append(album['album'])
    return ", ".join(album for album in albums)


def __musicbrainz_album_cover_grab(release, id):
    musicbrainzngs.set_useragent('musiquarium', '0.1', 'robert.armstrong.18@cnu.edu')
    try:
        # download release image in binary data and write to file
        logger.info(id)
        release_cover_binary = musicbrainzngs.get_image_front(id)
        with open(f"../assets/img/album_artwork/{release} - {id}.png", "wb")  as image:
            image.write(release_cover_binary)  # Write binary data to release id file
            return f"../assets/img/album_artwork/{release} - {id}.png"
    except Exception as e:
        logger.error(f"\t[Unable to get cover art for {release}!: {e}]")
        return default_image

""" Discogs metadata retrieval | Database updating """

def add_song_discogs(song_metadata, user, image_path):
    """
        Creates or updates song with given information for specific user.
        If song exists, created value is false. Otherwise, the song exists and created is true.
    """
    # If song already exists, update all information
    try:
        album, id, release_date, label = __get_discogs_release(song_metadata['song']['albums'])
        albums = get_possible_albums(song_metadata['song']['albums'])
        new, created = Song.objects.update_or_create(
                title = song_metadata['song']['title'],
                artist = song_metadata['song']['artists']['artist'],
                file_location = song_metadata['song']['file_path'],
                defaults={
                    "title": song_metadata['song']['title'],
                    "genre": song_metadata['song']['genres']['genre'],
                    "album": albums,
                    "artist": song_metadata['song']['artists']['artist'],
                    "profile": user.profile,
                    "release_date": release_date,
                    "detection_method": "Discogs",
                    "album_artwork": image_path,
                    "json_item": json.dumps(song_metadata),
                    "file_location": song_metadata['song']['file_path']})
        if (created):
            new.save()
            # logger.info("New song, creating...")
        else:
            new.save()
            # logger.info("Old song, updating...")

    except Exception as e:
        logger.error(f"Error while adding \'{song_metadata['song']['title']}\' discogs song instance to database: {e}")

def __get_discogs_release(albums):
    for item in albums.values():
        for album in item:
            return album['album'], album['discogs_id'], album['release_date'], album['release_label']
