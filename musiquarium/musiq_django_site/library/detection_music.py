#import django
#django.setup()

import acoustid, chromaprint, os, sys, environ, logging, discogs_client
import oauth2 as oauth
from discogs_client.exceptions import HTTPError
from urllib import request
from urllib.parse import parse_qsl
from urllib.parse import urlparse
from enum import Enum, unique

# adds parent folder to python path
sys.path.append("../")

# logger for logging debug information
logger = logging.getLogger("mylogger")

# grabs .env information
environ.Env.read_env()
_env = environ.Env()
_ck = _env('CONSUMER_KEY')
_cs = _env('CONSUMER_SECRET')
_rtu = _env('REQUEST_TOKEN_URL')
_au = _env('AUTHORIZE_URL')
_atu = _env('ACCESS_TOKEN_URL')

# enum for different media detection methods
class Detection(Enum):
    AUDIO_FINGERPRINT = 1
    METADATA = 2 # Not implementing yet

# enum for different databases to gather song information from (using above detection methods for initial song recognition)
class Database(Enum):
    MUSICBRAINZ = 1 # Picard (setup but not really implemented)
    DISCOGS = 2

def musiq_detect_song(detection, database, file_dir):
    '''
        This function will be a wrapper for the various detection functions
        i.e. this function passes a type which represents the detection method which will be used:
            * determine detection method (pyacoustid)
            * database(s) which will be used to gather song information

        param : detection
            Detection method which will determine the detection method (audio fingerprinting (and metadata?) )
        param : database
            Type which determines the database to choose from a given set of databases.
        param : file_dir
            File path to music directory
    '''

    if (detection == Detection.AUDIO_FINGERPRINT):
        if (database == Database.MUSICBRAINZ):
            return _musicbrainz_detect(file_dir, _env('MUSICBRAINZ_API_KEY'))
        if (database == Database.DISCOGS):
            return _discogz_detect(file_dir)

def _musicbrainz_detect(file_dir, API_KEY): # Uses chromaprint and pyacousid to detect song and return song information
    song_data = []
    for score, recording_id, title, artist in acoustid.match(API_KEY, file_dir):
        #print(score, recording_id, title, artist)
        song_data.append([score, recording_id, title, artist])
    return song_data

def _discogz_detect(file_dir): # Temporary function
    _discogz_authorization()

def _discogz_authorization():
    # registered application
    user_agent = 'musiquarium/0.1'

    # logging information, ensuring env variables loaded correctly
    logger.info(f'\nConsumer Key and Secret:\n{_ck} + {_cs}\n')

    # creating oauth Consumer and Client objects...
    client = discogs_client.Client(user_agent)
    client.set_consumer_key(_ck, _cs)

    # Passes in our consumer key and secret to the token request URL. Discogs returns
    # an ouath_request_token as well as an oauth request_token secret.
    token, secret, url = client.get_authorize_url()
    logger.info(f'\n\'{token}\' \n\n\'{url}\'')

    logger.info(' == Request Token == ')
    logger.info(f'* oauth_token = {token}')
    logger.info(f'* oauth_token_secret = {secret}')

    logger.info(f'Please browse to the following URL {url}')

    accepted = 'n'
    while accepted.lower() == 'n':
        print
        accepted = input(f'Have you authorized me at {url} [y/n] :')

    oauth_verifier = input('Verification code : ')
