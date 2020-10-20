#import django
#django.setup()

import acoustid, chromaprint, os, sys, environ, logging, discogs_client, _thread, threading, musicbrainzngs, json
import oauth2 as oauth
from discogs_client.exceptions import HTTPError
from urllib import request
from urllib.parse import parse_qsl
from urllib.parse import urlparse
from enum import Enum, unique
from ratelimiter import RateLimiter
from library.add_songs import add_song_musicbrainz

# adds parent folder to python path
sys.path.append("../")

# logger for logging debug information
logger = logging.getLogger("mylogger")

#logging.basicConfig(level=logging.DEBUG)
# optionally restrict musicbrainzngs output to INFO messages
#logging.getLogger("musicbrainzngs")

# grabs .env information
environ.Env.read_env()
_env = environ.Env()
_ck = _env('CONSUMER_KEY')
_cs = _env('CONSUMER_SECRET')
_rtu = _env('REQUEST_TOKEN_URL')
_au = _env('AUTHORIZE_URL')
_atu = _env('ACCESS_TOKEN_URL')
_pt = _env("PERSONAL_TOKEN")

rate_limiter = RateLimiter(max_calls=3, period=60) # helps with limiting api calls to specified web service
temp_rate_limiter = RateLimiter(max_calls=1, period=3)

# registered application
user_agent = 'musiquarium/0.1'

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
        return _musicbrainz_match(file_dir, _env('MUSICBRAINZ_API_KEY')) # initial file recognition with musicbrains audio fingerprinting library
        #if (database == Database.MUSICBRAINZ):
        #    _musicbrainz_detect(file_dir, song_list, _env('MUSICBRAINZ_API_KEY'))
        #if (database == Database.DISCOGS):
        #    return _discogz_detect(file_dir)

def _musicbrainz_match(file_dir, API_KEY): # Uses chromaprint and pyacousid to detect song and return detected song information
    song_data = []
    for score, recording_id, title, artist in acoustid.match(API_KEY, file_dir, parse=True):
        song_data.append([score, recording_id, title, artist])
        logger.info(" Detection Successful! ")

    return song_data

def musicbrainz_detect(song_detected_information, user):
    # Set the User-Agent to be used for requests to the MusicBrainz webservice. This must be set before requests are made.
    musicbrainzngs.set_useragent('musiquarium', '0.1', 'robert.armstrong.18@cnu.edu')

    for song_info in song_detected_information:
        with temp_rate_limiter:

            song_title = song_info[0][2]
            release_list = []
            selected_release =""
            selected_release_id=""
            selected_release_date=""
            artist_title = song_info[0][3]
            track_number = 1
            file_location = song_info[1]

            #logger.info(f"At Data retrieval step, using id: {song_info[0][1]}")
            try:
                recording_search_result = musicbrainzngs.get_recording_by_id( song_info[0][1], includes=["tags", "releases", "discids"] )

                # iterate through albums/releases
                for recording in recording_search_result["recording"]["release-list"]:
                    release_string = ""
                    id_string = ""
                    date_string = ""

                    logger.info("getting release information")

                    if ("title" in recording):
                        for release in recording["title"]:
                            release_string += release
                    else:
                        release_string = "N/A"
                    if ("id" in recording):  # if musicbrainz id of album is in given json data
                        for id in recording["id"]:
                            id_string += id
                    else:
                        id_string = "N/A"
                    if ("date" in recording):  # if date of album is in given json data
                        for date in recording["date"]:
                            date_string += date
                    else:
                        date_string = "N/A"

                    logger.info("got release information")

                    release_list.append([release_string, id_string, date_string]) # adds all album/release information to tuple

                # picks first album release (sorted by date)
                selected_release = release_list[0][0]
                selected_release_id = release_list[0][1]
                selected_release_date = release_list[0][2]

                # retrieve covert art for select album release
                #image_data = musicbrainzngs.get_cover_art_list( selected_release_id )
                #musicbrainzngs.get_cover_art_list("46a48e90-819b-4bed-81fa-5ca8aa33fbf3")
                #musicbrainzngs.get_image(mbid=song_info[0][1], coverid=front)
                #logger.info("Successfully retrieved image data!")

                #for image in image_data["images"]:
                #    if "Front" in image["types"] and image["approved"]:
                #        logger.info("%s is an approved front image!" % image["thumbnails"]["large"])
                #        break

                add_song_musicbrainz(song_title, selected_release, selected_release_id, selected_release_date, artist_title, file_location, user)
                logger.info("Added item")

            except:
                logger.error(f"Error while grabbing {song.info} musicbrainz information")


######### unimplemented due to issues with discogs user authorization #########

def _discogz_detect(file_dir): # Temporary function
    return None

def discogz_get_client():
    return discogs_client.Client(user_agent, _ck, _cs)

def discogz_personal_client():
    return discogs_client.Client(user_agent, user_token=_pt)

def discogz_client_authorization(client, profile):
    try:
        token, secret = client.get_access_token(profile.discogz)
    except HTTPError:
        print('Unable to authenticate.')
        sys.exit(1)

    return url

def discogz_client_verification(token, profile):
    # this token is generated by the current user and tied to a this user
    oauth_verifier = token
    temp_client = discogs_client.Client(user_agent, _ck, _cs, profile.discogz_token, profile.discogz_secret, profile.discogz)

    # fetch the identity object for the current logged in user.
    # return discogsclient.identity()

def discogz_data_retrieval(song_information, client):
    search_results = []
    for info in song_information:
        logger.info(f'{info[0][2]} - {info[0][3]} - {info[1]} ')
        with rate_limiter:
            data = client.search(info[0][2], track=info[0][2], artist=info[0][3], format='album')

        search_results.append(data)

    for search in search_results:
        for release in search:
            with temp_rate_limiter:
                logger.info(release)
                #logger.info(f'\n\t== discogs-id {release.id} ==')
                #logger.info(f'\tArtist\t: {", ".join(artist.name for artist in release.artists)}')
                # logger.info(f'\tFormats\t: {", ".join(release.get("format", ["Unknown"]))}')
                #logger.info(f'\tTitle\t: {release.title}')
                #logger.info(f'\tYear\t: {release.year}')
                #logger.info(f'\tLabels\t: {", ".join(label.name for label in release.labels)}')
