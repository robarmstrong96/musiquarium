#import django
#django.setup()
import os, sys, stat, subprocess
import pathlib
from library.detection_music import Detection, Database, musiq_detect_song # relative import
from library.add_songs import add_songs_to_database # relative import

sys.path.append("../")

BASE_DIR = pathlib.Path(__file__).resolve()
PATHS = os.path.join(BASE_DIR.parents[2].__str__(), 'media/')

file_extensions = [".mp3",
                    ".aif",
                    ".m4a"]

def testrun():
    songs = []
    for subdir, dirs, files in os.walk('../media'):
         for file in files:
             for extension in file_extensions:
                 if ( (os.path.join(subdir, file)).__str__().find(extension) != -1 ):
                      songs.append(os.path.join(subdir, file))

    for file_path in songs:
        if (os.path.isfile(file_path)):
            song_data = musiq_detect_song(Detection.AUDIO_FINGERPRINT, Database.DISCOGS, file_path)
            #add_songs_to_database(song_data)
