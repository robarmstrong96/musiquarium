import os, sys, psycopg2, logging, _thread, json
from threading import Thread, Lock
from django import forms
from django.db import connection
from django.http import JsonResponse
from library.models import Song
from library.test_run import testrun # relative import
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
from library.detection_music import discogz_personal_client, discogz_data_retrieval, musicbrainz_retrieval, discogz_client_authorization, discogz_get_client, Detection, Database

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
    if Song.objects.filter(profile=request.user.profile).count() <= 0:
        init_import = True
        logger.info(request.POST)
    else:
        init_import = False

    return render(request, 'index.html', {'profile': request.user.profile,
    'init_import': init_import})

@login_required(login_url='/library/login_user')
def profile(request):
    """ profile html request """

    # avatar image filename
    avatar_file = (f"{request.user.first_name}_{request.user.last_name}_{request.user.email}")

    # updates profile information (i.e. email, password)
    if request.method == 'POST' and 'username' in request.POST:
        update_user_profile(request)

    # updates api information(maybe? might not need)
    if request.method == 'POST' and 'discogz' in request.POST:
        form = update_profile(request) # Updates profile model, returns form with updated data
    else:
        form = DiscogzAPIForm()

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

    logger.info(request.user.profile.avatar)

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
    if request.method == "POST" and 'organize' in request.POST:
        detect = BulkImport(request.user)
        detect.daemon = True
        detect.start()
        #list = testrun()
        #logger.info("Starting data retrieval..")
        #musicbrainz_retrieval(list, Detection.MUSICBRAINZS, request.user)

    return render(request, 'table.html', {'page_obj': song_list,
    'size': song_list.count(), 'profile': request.user.profile})

def login_user(request):
    """ login html request """
    logger.info(request.method)
    if request.method == "POST":
        logger.info(request.method)
        user = authenticate(username=request.POST.get('email'),
        password=request.POST.get('password'))
        if user is not None:
            login(request, user)
            return render(request, 'index.html')
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

def logout(request):
    auth.logout(request)
    return redirect('login_user')

class BulkImport(Thread):
    '''
        Thread for bulk matching and detecting functionality.
    '''

    def __init__(self, user):
        Thread.__init__(self)
        self.user = user

    def run(self):
        user = self.user
        while True:
            try:
                #client = discogz_personal_client()
                list = testrun()
                logger.info("created list...")
                musicbrainz_retrieval(list, Detection.MUSICBRAINZS, user)
                #discogz_data_retrieval(list, client)
            except:
                logger.error(sys.exc_info()[0])
            finally:
                logger.info("Finished thread!")
                return True

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
