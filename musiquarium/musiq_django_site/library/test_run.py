#import django
#django.setup()
import os, sys, stat, subprocess, logging, time, pathlib
from library.detection_music import Detection, Database, musiq_detect_song # relative import
from library.add_songs import add_songs_to_database # relative import
from ratelimiter import RateLimiter

BASE_DIR = pathlib.Path(__file__).resolve()
PATHS = os.path.join(BASE_DIR.parents[1].__str__(), 'media/')

logger = logging.getLogger("mylogger")
logger.info(PATHS)

file_extensions = [".mp3",
                    ".aif",
                    ".m4a"]

rate_limiter = RateLimiter(max_calls=3, period=1) # helps with limiting api calls to specified web service

def testrun():
    # scans media for media files
    songs = []
    song_data = []
    for subdir, dirs, files in os.walk(PATHS):
         for file in files:
            for extension in file_extensions:
                logger.info(f"{file}...?")
                if ( extension in (os.path.join(subdir, file)).__str__() ):
                    logger.info(f"{file} exists!")
                    songs.append(os.path.join(subdir, file))

    # calls specified recognition method and specifies database
    for file_path in songs:
        if (os.path.isfile(file_path)):
            with rate_limiter:
                data = musiq_detect_song(Detection.AUDIO_FINGERPRINT, Database.MUSICBRAINZ, file_path)
                for info in data:
                    if (info[2] is not None and info[3] is not None):
                        song_data.append([info, file_path])
                        break

    return song_data
