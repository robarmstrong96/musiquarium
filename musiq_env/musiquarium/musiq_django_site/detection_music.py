import acoustid, chromaprint, os, sys
from enum import Enum, unique

class Detection(Enum):
    AUDIO_FINGERPRINT = 1
    METADATA = 2 # Not implementing yet

class Database(Enum):
    MUSICBRAINZ = 1 # Picard
    DISCOGZ = 2

def musiq_detect_song(detection, database, file_dir, API_KEY="UZKCzQ6AAg"):
    '''
        This function will be a wrapper for the various detection functions
        i.e. this function passes a type which represents the detection method which will be used:
            * determine detection method (pyacoustid)
            * database(s) which will be used to gather song information

        param : detection
            Detection method which will determine the detection method (audio fingerprinting (and metadata?) )
        param : database
            Type which determines the database to choose from a given set of databases.
    '''

    if (detection == Detection.AUDIO_FINGERPRINT):
        if (database == Database.MUSICBRAINZ):
            return _musicbrainz_detect(file_dir, API_KEY)
        if (database == Database.DISCOGZ):
            return _discogz_detect(file_dir)

def _musicbrainz_detect(file_dir, API_KEY): # Uses chromaprint and pyacousid to detect song and return song information
    song_data = []
    for score, recording_id, title, artist in acoustid.match(API_KEY, file_dir):
        song_data.append([score, recording_id, title, artist])
    return song_data

def _discogz_detect(file_dir): # Temporary function
    return false
