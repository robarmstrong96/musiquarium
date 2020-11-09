import os, sys, psycopg2, logging, _thread, threading, json, pathlib, asyncio, time
from queue import Queue
from ratelimiter import RateLimiter
from threading import Thread, Lock
from django import forms
from django.db import connection
from django.http import JsonResponse
from library.models import Song
from library.file_detection import directory_scan # relative import
from library.detection_music import Detection, Database, musiq_match_song, musiq_retrieve_song
from django.views.generic import ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import RegistrationForm, DiscogzAPIForm, ImageUploadForm, BulkInitilization
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect, HttpResponse


logger = logging.getLogger("mylogger")

# registered application
user_agent = 'musiquarium/0.1'

# --------------------------------- template view files -----------------------#
"""
        These are the template functions (i.e. html requests)
"""

@login_required(login_url='/library/login_user')
def index(request):
    """View function for home page of site."""

    # Checks to see if user has any detected media already. If so, user is
    # prompted to start the initial bulk library import process.
    song_count = Song.objects.filter(profile=request.user.profile).count()
    if song_count <= 0:
        init_import = True
    else:
        init_import = False

    # dict used for initial bulk library creation
    init_bulk_detect = {
        'match': None,
        'metadata': None,
        'file_dir': None,
    }

    # checks for post items for initial library creation
    if request.method == 'POST' and 'match' in request.POST:
        init_bulk_detect['match'] = request.POST['match']
    if request.method == 'POST' and 'metadata' in request.POST:
        init_bulk_detect['metadata'] = request.POST['metadata']
    if request.method == 'POST' and 'file' in request.POST:
        init_bulk_detect['file_dir'] = request.POST['file']

    # starts bulk user music library initialization
    if request.method == 'POST' and 'match' in request.POST and 'metadata' in request.POST and 'file' in request.POST:
        import_daemon = BulkImport(request.user, init_bulk_detect)
        import_daemon.daemon = True
        import_daemon.start()

    return render(request, 'index.html', {'profile': request.user.profile,
    'init_import': init_import, 'song_count': song_count})

@login_required(login_url='/library/login_user')
def profile(request):
    """ profile html request """

    # avatar image filename
    avatar_file = (f"{request.user.first_name}_{request.user.last_name}_{request.user.email}")

    # updates profile information (i.e. email, password)
    if request.method == 'POST' and 'email' in request.POST:
        update_user_profile(request)

    # updates (specifically discogs) api information(maybe? might not need)
    if request.method == 'POST' and 'discogz' in request.POST:
        form = update_profile(request) # Updates profile model, returns form with updated data
    else:
        form = DiscogzAPIForm()

    # deletes library information associated with user profile
    if request.method == "POST" and 'delete' in request.POST:
        logger.info(f"Deleting all entries for profile {request.user.profile}")
        Song.objects.filter(profile=request.user.profile).delete()

    # sets profile avatar image
    if request.method == 'POST':
       upload_form = ImageUploadForm(request.POST, request.FILES)
       if upload_form.is_valid():
           if 'avatar' in request.FILES:
                image = request.FILES.get('avatar')
                request.user.profile.set_image_path(image.__str__())
                request.user.profile.save()
           upload_form.save()
           logger.info(f"success in file upload: {upload_form}")
       else:
           logger.error(f"error: {upload_form.errors}")
    else:
        upload_form = ImageUploadForm()

    # generate client api key
    # if request.method == 'POST' and 'authenticate' in request.POST:
        #client = discogz_get_client() # 1) get discogz client instance
        #request_token, request_secret, url = client.get_authorize_url() # 2) get request information
        #discogz_client_authorization(client, request.user.profile)
        #return HttpResponseRedirect(url)

    return render(request, 'profile.html', {'form': form,
    'upload_form': upload_form, 'profile': request.user.profile})

@login_required(login_url='/library/login_user')
def table(request):
    """ table html request """
    song_list = Song.objects.filter(profile=request.user.profile)

    for song in song_list:
        logger.info(song.file_location.__str__())

    #if request.method == "POST" and 'organize' in request.POST:
        #detect = BulkImport(request.user)
        #detect.daemon = True
        #detect.start()
        #BASE_DIR = pathlib.Path(__file__).resolve()
        #PATHS = os.path.join(BASE_DIR.parents[1].__str__(), 'media/')
        #logger.info(PATHS)
        #list = file_detection(Detection.MUSICBRAINZS, Database.MUSICBRAINZ, PATHS)
        #logger.info("created list...")
        #musicbrainz_retrieval(list, Detection.MUSICBRAINZS, request.user)

    return render(request, 'table.html', {'page_obj': song_list,
    'size': song_list.count(), 'profile': request.user.profile})

def login_user(request):
    """ login html request """
    logger.info(request.method)

    if request.user.is_authenticated:
        logger.info("spaghetti!")
        logout(request)

    if request.method == "POST":
        logger.info(request.method)
        user = authenticate(username=request.POST.get('email'),
        password=request.POST.get('password'))
        if user is not None:
            login(request, user)

            song_count = Song.objects.filter(profile=user.profile).count()
            if song_count <= 0:
                init_import = True
            else:
                init_import = False

            return render(request, 'index.html', {'profile': user.profile,
            'init_import': init_import, 'song_count': song_count})
    return render(request, 'login_user.html', )

def register(request):
    """ register html request """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # load the profile instance created by the signal
            user.save()
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('index')
    else:
        form = RegistrationForm()

    # returns profile
    return render(request, 'register.html', {'form': form})


# --------------------------------- non template view files -------------------#
"""
        These are the non-template functions (i.e. update functions, upload
        functions, etc...)
"""

def _bulk_import(init_dict, user):
    match_limiter = RateLimiter(max_calls=1, period=3)
    database_limiter = RateLimiter(max_calls=1, period=3)
    matched_songs = [] # songs that have been matched

    #try:
    # rate limiter used for limiting api calls to the matcher api
    if (init_dict['match'] == Detection.MUSICBRAINZS):
        match_limiter = RateLimiter(max_calls=1, period=1)

    # rate limiter used for limiting api calls to the database api
    if (init_dict['metadata'] == Database.MUSICBRAINZ):
        database_limiter = RateLimiter(max_calls=1, period=1)

    # 1) obtains files and enum values based on given media directory and
    # given sting values representing matching methods/databases.
    matching, database, files = directory_scan(init_dict['match'],
    init_dict['metadata'], init_dict['file_dir'])

    # 2) matches the detected songs with preffered matching methodology
    logger.info("Matching songs...")
    for file in files:
        with match_limiter:
            matched_songs.append(musiq_match_song(matching, file))

    # 3) retrieves song metadata from specified database
    logger.info("Retrieving metadata...")
    for match in matched_songs:
        with database_limiter:
            musiq_retrieve_song(match, database, matching, user)

    #except Exception as e:
    #    logger.error(f"Error during bulk import in def: {e}")

def logout(request):
    auth.logout(request)
    return redirect('login_user')

class BulkImport(Thread):
    '''
        Thread for bulk matching and detecting functionality.
    '''

    def __init__(self, user, dict_metadata):
        Thread.__init__(self)
        self.user = user
        self.metadata = dict_metadata

    def run(self):
        while True:
            try:
                logger.info("Starting bulk import...")
                _bulk_import(self.metadata, self.user)
            except Exception as e:
                logger.error(f"Error during bulk import in thread: {e}")
            finally:
                logger.info("Finished bulk import!")
                return

def update_profile(request):
    '''
        Function for adding discogs user information.
    '''
    profile = request.user.profile
    form = DiscogzAPIForm(request.POST or None)
    if form.is_valid():
        profile.discogz = request.POST['discogz']
        profile.save()
    request.user.save()

    return form

def update_user_profile(request):
    profile = request.user.profile
    if 'email' in request.POST:
        logger.info('email' in request.POST)
        request.user.email = request.POST['email']
    if 'first_name' in request.POST:
        logger.info('first_name' in request.POST)
        request.user.first_name = request.POST['first_name']
    if 'last_name' in request.POST:
        logger.info('last_name' in request.POST)
        request.user.last_name = request.POST['last_name']
    request.user.profile.save()
    request.user.save()
