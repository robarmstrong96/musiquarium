import sys, logging, musicbrainzngs, json
from library.models import Song
from django.db import models
#from django.contrib import messages

# logger for logging debug information
logger = logging.getLogger("mylogger")

def add_songs_to_database(songs):
    for song in songs:
        if (not song[2] and not song[3]):
            if(Song.objects.filter(title = song[2], artist = song[3]).exists() == False):
                temp = Song(title = song[2], file_size = 0, duration = 1, artist = song[3])
                logger.info(temp)
                temp.save()

def add_song_musicbrainz(song_metadata, user):
    """
        Creates or updates song with given information for specific user.
        If song exists, created value is false. Otherwise, the song exists and created is true.
    """
    # If song already exists, update all information
    try:
        album, release_date, image_path = _determine_first_release(song_metadata['song']['albums'])
        new, created = Song.objects.update_or_create(
                title = song_metadata['song']['title'],
                artist = song_metadata['song']['artists']['artist'],
                defaults={
                    "title": song_metadata['song']['title'],
                    "album": album,
                    "artist": song_metadata['song']['artists']['artist'],
                    "profile": user.profile,
                    "release_date": release_date,
                    "detection_method": "Musicbrains",
                    "album_artwork": image_path,
                    'json_item': json.dumps(song_metadata)})
        if (created):
            new.save()
            #messages.success(request, f"Song \'{song_metadata['song']['title']}\' updated")
            #logger.info("Old song, updating...")
        else:
            new.save()
            #messages.success(request, f"Song \'{song_metadata['song']['title']}\' added")
            #logger.info("New song, creating...")
        #logger.info("Done.")

    except Exception as e:
        logger.error(f"Error while adding \'{song_metadata['song']['title']}\' musicbrainz song instance to database: {e}")

def _determine_first_release(albums):
    releases = []
    for album in albums.values():
        for item in album:
            image = __musicbrainz_album_cover_grab(item['album'], item['album_musicbrains_id'])
            return item['album'], item['release_date'], image

def __musicbrainz_album_cover_grab(release, id):
    musicbrainzngs.set_useragent('musiquarium', '0.1', 'robert.armstrong.18@cnu.edu')
    try:
        # download release image in binary data and write to file
        release_cover_binary = musicbrainzngs.get_image_front(id)
        with open(f"./assets/img/album_artwork/{release} - {id}.png", "wb")  as image:
            image.write(release_cover_binary)  # Write binary data to release id file
            return f"../assets/img/album_artwork/{release} - {id}.png"
    except Exception as e:
        logger.error(f"\t[Unable to get cover art for {release}!: {e}]")
        return "../assets/img/default/null.png"
