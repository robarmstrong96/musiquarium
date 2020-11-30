import os, sys, stat, subprocess, logging, time, pathlib, queue
from library.detection_music import Detection, Database # relative import
from ratelimiter import RateLimiter
from queue import Queue

logger = logging.getLogger("mylogger")

file_extensions = [".mp3",
                    ".aif",
                    ".m4a",
                    ".flac",
                    ".ogg",
                    ".wav",
                    ".aac"]

def directory_scan(detection, database, file_dir):
    # scans media for media files
    song_paths = []

    # Detects files in given directory
    #logger.info(f"\'{os.path.abspath(file_dir)}\'")
    for subdir, dirs, files in os.walk(os.path.abspath(file_dir)):
         for file in files:
            for extension in file_extensions:
                if ( extension in (os.path.join(subdir, file)).__str__() ):
                    logger.info(f"{file} exists!")
                    song_paths.append(os.path.join(subdir, file))

    # returns enum values using 'detection' and 'database' function parameters
    enum_detect, enum_database = _get_enum_values(detection, database)

    # function return
    #logger.info("Done!")
    return enum_detect, enum_database, song_paths

def _get_enum_values(detection, database):
    enum_detect = ""
    enum_database = ""

    if detection == "Musicbrainz":
        enum_detect = Detection.MUSICBRAINZS
    elif detection == "ARCloud":
        enum_detect = Detection.ACRCLOUD
    elif detection == "Metadata":
        enum_detect = Detection.METADATA

    if database == "Musicbrainz":
        enum_database = Database.MUSICBRAINZ
    elif database == "Discogs":
        enum_database = Database.DISCOGS

    #logger.info(f"{enum_detect} and {enum_database}")
    return enum_detect, enum_database
