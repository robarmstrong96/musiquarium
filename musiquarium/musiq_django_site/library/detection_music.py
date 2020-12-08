import chromaprint
import os
import sys
import environ
import logging
import discogs_client
import json
import oauth2 as oauth
import music_tag
import musicbrainzngs
import acoustid
from ratelimiter import RateLimiter
from discogs_client.exceptions import HTTPError
from enum import Enum, unique
from library.add_songs import add_song_musicbrainz, add_song_discogs
from acrcloud.recognizer import ACRCloudRecognizer
from django.utils.text import slugify

''' Global variables '''

# adds parent folder to python path
sys.path.append("../")

discogs_limiter = RateLimiter(max_calls=30, period=60)

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
_pt = _env("PERSONAL_TOKEN")

# registered application name represented as a string
user_agent = 'musiquarium/0.1'

# enums for different media detection methods


class Detection(Enum):
    MUSICBRAINZS = 1
    ACRCLOUD = 2
    METADATA = 3  # Not implementing yet

# enums for different databases to gather song information from
# (using above enum 'Detection' for initial song recognition)


class Database(Enum):
    MUSICBRAINZ = 1
    DISCOGS = 2


''' Wrapper functions '''


def musiq_match_song(detection, file_path):
    '''
        This function will be a wrapper function for the various matching functions
        i.e. this function passes a type which represents the detection method which will be used:
            * determine detection method (pyacoustid)

        param : detection
            Detection method which will determine the detection method (audio fingerprinting (and metadata?) )
        param : file_path
            File path to music file(s)
    '''

    if (detection == Detection.MUSICBRAINZS):
        return _musicbrainz_match(file_path, _env('MUSICBRAINZ_API_KEY'))
    elif (detection == Detection.ACRCLOUD):
        return _acrcloud_match(file_path)
    elif (detection == Detection.METADATA):
        return metadata_grab(file_path)


def musiq_retrieve_song(song_metadata, database, match, user):
    '''
        This function will be a wrapper function for the various metadata retrieval functions
        i.e. this function passes a type which represents the metadata source:
            * database(s) which will be used to gather song information

        param : database
            Type which determines the database to choose from a given set of databases.
        param : file_path
            File path to music file(s)
    '''

    if (database == Database.MUSICBRAINZ):
        return _musicbrainz_retrieval(song_metadata, match, user)
    elif (database == Database.DISCOGS):
        return _discogs_retrieval(song_metadata, match, user)


''' Matching and detection functionality '''


def metadata_grab(file_dir):
    song_metadata = []
    try:
        # logger.info(f"File: {file_dir} and type {type(file_dir)}")
        grab = music_tag.load_file(file_dir)
        list = [('title', str(grab['title'])), ('artists', dict([('artist', str(grab['artist'])),
                ('artist', str(grab['albumartist']))])), ('albums', dict([('album', str(grab['album'])),
                ('album_musicbrains_id', "N/A"), ('release_date', str(grab['year']))])),
                ('file_path', file_dir), ('track_number', str(grab['track_number'])),
                ('json_data', None), ('genres', dict([('genre',  str(grab['genre']))]))]
        song_metadata.append(('song', dict(list)))
    except:
        logger.error(f"Error with {file_dir}: {e}")
        list = [('score', "N/A"), ('recording_id', "N/A"), ('title', "N/A"),
            ('artists', dict([('artist', "N/A")])), ('albums', dict(
                [('album', 'Unknown'), ('album_musicbrains_id', "N/A"), ('release_date', "Unknown")])),
            ('file_path', file_dir), ('track_number', "N/A"), ('json_data', None),
            ('genres', dict([('genre', 'Unknown Genre')]))]
        song_metadata.append(('song', dict(list)))
    finally:
        return dict(song_metadata)


def _musicbrainz_match(file_dir, API_KEY):
    """
        Function which deals with audio fingerprinting given songs and
        returning musicbrainz matched metadata in json format.
    """
    song_metadata = []
    try:
        for score, recording_id, title, artist in acoustid.match(API_KEY, file_dir):
            list = [('score', score), ('recording_id', recording_id), ('title', title),
                    ('artists', dict([('artist', artist)])), ('albums', dict(
                        [('album', 'Unknown'), ('album_musicbrains_id', "N/A"), ('release_date', "Unknown")])),
                    ('file_path', file_dir), ('track_number', 0), ('json_data', None),
                    ('genres', dict([('genre', 'Unknown Genre')]))]
            song_metadata.append(('song', dict(list)))
    except Exception as e:
        logger.error(f"Error with {file_dir}: {e}")
        list = [('score', "N/A"), ('recording_id', "N/A"), ('title', "N/A"),
                ('artists', dict([('artist', "N/A")])), ('albums', dict(
                    [('album', 'Unknown'), ('album_musicbrains_id', "N/A"), ('release_date', "Unknown")])),
                ('file_path', file_dir), ('track_number', "N/A"), ('json_data', None),
                ('genres', dict([('genre', 'Unknown Genre')]))]
        song_metadata.append(('song', dict(list)))
    finally:
        return dict(song_metadata)


def _musicbrainz_retrieval(song_metadata, match_method, user):
    '''
        Retrieves metadata for specified song, with the retrieval methodology
        depending on the matching method used (i.e. Picard(musicbrainz audio
        fingerprinting service) vs. ARCloud)

        param : song_detected_information
            Dict of information pertaining to a matched song.
        param : match_method
            Enum value representing the matching methodology used to detect the
            specified song.
        param : user
            Django user.
    '''
    # Set the User-Agent to be used for requests to the MusicBrainz webservice. This must be set before requests are made.
    musicbrainzngs.set_useragent(
        'musiquarium', '0.1', 'robert.armstrong.18@cnu.edu')

    # if the specified song was matched with the musicbrains audio fingerprinting service
    try:
        if match_method == Detection.MUSICBRAINZS:
            recording_search_result = musicbrainzngs.get_recording_by_id(
                song_metadata['song']['recording_id'],
                includes=["tags", "releases", "discids"])
            release_list = []

            # with open(f"json_temp/{song_metadata['song']['title']}.json", "w") as json_file:
            #    json_file.write(json.dumps(recording_search_result, indent=4))

            # iterate through albums/releases
            for recording in recording_search_result["recording"]["release-list"]:
                release_string = "N/A"
                id_string = "N/A"
                date_string = "N/A"

                ''' checks if existing data exists in json/meta data,
                sets data if exists '''
                if ("title" in recording):
                    # if musicbrainz album/release title is in json data...
                    release_string = recording["title"]
                if ("id" in recording):
                    # if musicbrainz id of album is in given json data...
                    id_string = recording["id"]
                if ("date" in recording):
                    # if release date of album is in given json data...
                    date_string = recording["date"]

                # appends album information in dict format to list
                release_list.append(dict([('album', release_string),
                                          ('album_musicbrains_id', id_string),
                                          ('release_date', date_string)]))

            # modifies dict entry 'albums' information
            song_metadata['song']['albums'] = dict([('albums', release_list)])

            # modifies/creates 'Song' django model instance with
            # given information
            add_song_musicbrainz(song_metadata, user)

        # if the specified song was matched with the ARCloud audio fingerprinting service
        elif match_method == Detection.ACRCLOUD or match_method == Detection.METADATA:
            # searches musicbrainz database with ARCloud data, grabs first search
            # result
            recording_search_result = musicbrainzngs.search_recordings(strict=False,
                                                                       limit=1, query=song_metadata['song']['title'],
                                                                       artist=song_metadata['song']['artists']['artist'],
                                                                       recording=song_metadata['song']['title'],
                                                                       release=song_metadata['song']['albums'].values(
                                                                       ),
                                                                       country='US')

            release_list = []

            # with open(f"json_temp/{song_metadata['song']['title']}.json", "w") as json_file:
            #    json_file.write(json.dumps(next(iter(recording_search_result['recording-list'])), indent=4))

            # iterate through albums/releases
            for recording in recording_search_result['recording-list']:
                for release in dict(recording)['release-list']:
                    release_string = "N/A"
                    id_string = "N/A"
                    date_string = "N/A"

                    ''' checks if existing data exists in json/meta data,
                            sets data if exists '''
                    if ("title" in release):
                       # if musicbrainz album/release title is in json data...
                        release_string = release['title']
                    if ("id" in release):
                       # if musicbrainz id of album is in given json data...
                        id_string = release['id']
                    if ("date" in release):
                       # if release date of album is in given json data...
                        date_string = release['date']

                    # appends album information in dict format to list
                    release_list.append(dict([('album', release_string),
                                              ('album_musicbrains_id', id_string),
                                              ('release_date', date_string)]))

            # modifies dict entry 'albums' information
            song_metadata['song']['albums'] = dict([('albums', release_list)])

            # modifies/creates 'Song' django model instance with
            # given information
            add_song_musicbrainz(song_metadata, user)

    except Exception as e:
        add_song_musicbrainz(song_metadata, user)
        logger.error(f"Error while grabbing musicbrainz information: {e}")


def _acrcloud_match(file_path):
    '''
        Matching function used to fingerprint a locally recognized and
        supported (i.e. mp3, wav, flac, etc...) audio file using the
        ACRcloud audio fingerprinting service.

        param : file_path
            Absolute file path of a recognized audio file
    '''

    config = {  # dict used for configuring ACRCloudRecognizer
        'host': 'identify-us-west-2.acrcloud.com',
        'access_key': 'ce28963d9965bbd732c17487e9b698dd',
        'access_secret': 'dYqdPQ8N1bEhnnLr2WjlGYmvyA2Gh3JuLVe5dTZv',
        'timeout': 10  # in seconds
    }

    # sets ACRCloudRecognizer client
    matcher = ACRCloudRecognizer(config)

    # reads given json formatted metadata into python dict
    metadata = json.loads(matcher.recognize_by_file(file_path, 0))
    # logger.info(metadata)

    song_metadata = []

    try:
        #logger.info(f"matching {metadata}")
        for info in metadata['metadata']['music']:
            temp_song_info = []

            # getting song title
            if ('title' in info):
                temp_song_info.append(('title', info['title']))
            else:
                temp_song_info.append(('title', "Unknown"))
            # getting album name
            if ('album' in info):
                temp_song_info.append(
                    ('albums', dict([('album', info['album']['name'])])))
            else:
                temp_song_info.append(('album', "Unknown"))
            # getting list of artists
            if ('artists' in info):
                artist_list = []
                for artist in info['artists']:
                    artist_list.append(('artist', artist['name']))
                temp_song_info.append(('artists', dict(artist_list)))
            else:
                temp_song_info.append(('artists', "Unknown"))
            # getting list of genres
            if ('genres' in info):
                genres_list = []
                for genres in info['genres']:
                    genres_list.append(('genre', genres['name']))
                temp_song_info.append(('genres', dict(genres_list)))
            else:
                temp_song_info.append(('genres', "Unknown"))
            # getting release date information
            if ('release_date' in info):
                temp_song_info.append(('release_date', info['release_date']))
            else:
                temp_song_info.append(('release_date', "Unknown"))
            temp_song_info.append(('file_path', file_path))

            song_metadata.append(('song', dict(temp_song_info)))

        # returns a dict of collected song data in a python dictionary
        return dict([next(iter(song_metadata))])
    except:
        return dict([next(iter(song_metadata))])


def _discogs_retrieval(song_metadata, match, user):
    """
        Grabs discogs metadata for given user.
    """
    # Configures client
    client = discogs_create_new_client(user)
    # logger.info(f"Account: {client.identity()}")

    # Retrieval based by matching methodology
    try:
        if (match == Detection.MUSICBRAINZS or match == Detection.ACRCLOUD or match == Detection.METADATA):
            # logger.info(song_metadata)
            image_path = "../assets/img/default/note.png"
            search_results = client.search(song_metadata['song']['title'], type='release',
                                           artist=song_metadata['song']['artists']['artist'])

            release_list = []

            if (len(search_results) > 0):  # successfully obtained results
                genres = []

                for release in search_results:

                    release_list.append(dict([('album', release.title),
                                              ('discogs_id', release.id),
                                              ('release_date', release.year),
                                              ('release_label', ", ".join(label.name for label in release.labels))]))

                    image_binary = release.images[0]['uri']

                    with discogs_limiter:
                        content, resp = client._fetcher.fetch(None, 'GET', image_binary,
                                      headers={'User-agent': client.user_agent})

                    file_title = slugify(release.title + "-" + str(release.id))
                    with open(f"./assets/img/album_artwork/{file_title}.png", "wb") as image:
                        image_path = f"./assets/img/album_artwork/{file_title}.png"
                        image.write(content)

                # modifies dict entry 'albums' information
                song_metadata['song']['albums'] = dict([('albums', release_list)])
                # modifies dict entry 'artists'
                song_metadata['song']['artists']['artist'] = ", ".join(
                    artist.name for artist in release.artists)
                # modifies dict entry 'genres'
                try:
                    for style in release.style:
                        if not style in genres:
                            genres.append(style)
                    for genre in release.genre:
                        if not genre in genres:
                            genres.append(genre)
                except:
                    if not "Unknown Genre" in genres:
                        genres.append("Unknown Genre")

                song_metadata['song']['genres']['genre'].join(genre for genre in genres)

                add_song_discogs(song_metadata, user, image_path)
            else:  # no search results, keeping matched data
                release_list.append(dict([('album', 'Unknown'),
                                          ('discogs_id', 'Unknown'),
                                          ('release_date', 'Unknown'),
                                          ('release_label', 'Unknown')]))
                # modifies dict entry 'albums' information
                song_metadata['song']['albums'] = dict([('albums', release_list)])
                # attempts to add song metadata to musiquarium database
                add_song_discogs(song_metadata, user, image_path)
    except Exception as e:
        logger.error(f"Error obtaining discogs information: {e}")


def discogs_create_new_client(user):
    """
        Creates and returns a new discogs client if the user has configured
        musiquarium with discogs through the profile page.

        param : user
            Musiquarium user which the discogs client will be configured with.
    """
    token, secret = user.profile.get_discogs_info()
    #logger.info(f"token: {token} and secret: {secret}")
    client = discogs_client.Client(user_agent, consumer_key=_ck,
                                   consumer_secret=_cs, token=token, secret=secret)
    return client
