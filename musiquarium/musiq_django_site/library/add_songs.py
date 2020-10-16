import sys, logging
from library.models import Song

#django.setup()

sys.path.append("../")

# logger for logging debug information
logger = logging.getLogger("mylogger")

def add_songs_to_database(songs):
    #for song in songs:
    #    print(f'{song[2]} {song[3]}')
    for song in songs:
        if (not song[2] and not song[3]):
            if(Song.objects.filter(title = song[2], artist = song[3]).exists() == False):
                temp = Song(title = song[2], file_size = 0, duration = 1, artist = song[3])
                logger.info(temp)
                temp.save()
