import sys, logging
from library.models import Song
from django.db import models

# logger for logging debug information
logger = logging.getLogger("mylogger")

def add_songs_to_database(songs):
    for song in songs:
        if (not song[2] and not song[3]):
            if(Song.objects.filter(title = song[2], artist = song[3]).exists() == False):
                temp = Song(title = song[2], file_size = 0, duration = 1, artist = song[3])
                logger.info(temp)
                temp.save()

def add_song_musicbrainz(song, release, release_id, release_date, artist, file_location, user):
    """
        Creates or updates song with given information for specific user.  If song exists, created value is false. Otherwise, the song exists and created is true.
    """
    # If song already exists, update all information
    logger.info(f"Attempting to save song for {user}")
    new, created = Song.objects.update_or_create(
            title = song,
            artist = artist,
            defaults={
                "title": song,
                "album": release,
                "artist": artist,
                "profile": user.profile})
    if (created):
        new.save()
        logger.info("Old song, updating...")
    else:
        new.save()
        logger.info("New song, creating...")
    logger.info("Done.")
