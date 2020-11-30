import os
import sys
import psycopg2
import logging
import _thread
import threading
import json
import pathlib
import asyncio
import time
import discogs_client
from queue import Queue
from ratelimiter import RateLimiter
from threading import Thread, Lock
from django import forms
from django.db import connection
from django.http import JsonResponse
from library.models import Song
from library.file_detection import directory_scan  # relative import
from library.detection_music import Detection, Database, musiq_match_song, musiq_retrieve_song, discogs_create_new_client
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
from django.core import serializers
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django import template
from messages_extends import constants as constants_messages
from django.contrib.messages import get_messages

register = template.Library()

logger = logging.getLogger("mylogger")

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
    # logger.info(request.POST)
    if request.method == 'POST' and 'match' in request.POST:
        init_bulk_detect['match'] = request.POST['match']
    if request.method == 'POST' and 'metadata' in request.POST:
        init_bulk_detect['metadata'] = request.POST['metadata']
    if request.method == 'POST' and 'file' in request.POST:
        init_bulk_detect['file_dir'] = request.POST['file']

    # starts bulk user music library initialization
    if request.method == 'POST' and 'match' in request.POST and 'metadata' in request.POST and 'file' in request.POST:
        #import_daemon = BulkImport(request, request.user, init_bulk_detect)
        #import_daemon.daemon = True
        #import_daemon.start()
        _bulk_import(request, init_bulk_detect, request.user)
        match = init_bulk_detect['match']
        metadata = init_bulk_detect['metadata']
        message = f'The bulk import using detection method {match} and the {metadata} database has started.'
        messages.add_message(request, constants_messages.INFO_PERSISTENT, message)

    return render(request, 'index.html', {'profile': request.user.profile,
                                          'init_import': init_import, 'song_count': song_count})


@login_required(login_url='/library/login_user')
def profile(request):
    """ profile html request """

    # avatar image filename
    avatar_file = (
        f"{request.user.first_name}_{request.user.last_name}_{request.user.email}")

    # updates profile information (i.e. email, password)
    if request.method == 'POST' and 'email' in request.POST:
        update_user_profile(request)

    # updates (specifically discogs) api information(maybe? might not need)
    if request.method == 'POST' and 'discogz' in request.POST:
        # Updates profile model, returns form with updated data
        form = update_profile(request)
    else:
        form = DiscogzAPIForm()

    # deletes library information associated with user profile
    if request.method == "POST" and 'delete' in request.POST:
        # logger.info(f"Deleting all entries for profile {request.user.profile}")
        Song.objects.filter(profile=request.user.profile).delete()
        messages.add_message(request, constants_messages.SUCCESS_PERSISTENT, "Musiquarium library information successfully deleted.")

    # sets profile avatar image
    if request.method == 'POST':
        upload_form = ImageUploadForm(request.POST, request.FILES)
        if upload_form.is_valid():
            if 'avatar' in request.FILES:
                image = request.FILES.get('avatar')
                request.user.profile.set_image_path(image.__str__())
                request.user.profile.save()
            upload_form.save()
            # logger.info(f"success in file upload: {upload_form}")
        else:
            logger.error(f"error: {upload_form.errors}")
    else:
        upload_form = ImageUploadForm()

    # logger.info(request.POST)

    # configure discogs
    if request.method == 'POST' and 'configure' in request.POST:
        token, secret, url = request.user.profile.discogs_client.get_authorize_url()
        return redirect(url)
    elif request.method == 'POST' and 'verify' in request.POST and 'configure' not in request.POST:
        try:
            token, secret = request.user.profile.discogs_client.get_access_token(
                request.POST['verifier'])
            request.user.profile.discogs_access_secret = secret
            request.user.profile.discogs_access_token = token
            request.user.profile.save()
            request.user.save()
            messages.add_message(request, messages.INFO, "Discogs has been configured.")
        except HTTPError:
            print('Unable to authenticate')
            sys.exit(1)

    return render(request, 'profile.html', {'form': form,
                                            'upload_form': upload_form, 'profile': request.user.profile})


@login_required(login_url='/library/login_user')
def table(request):
    logger.info(request)
    storage = get_messages(request)
    #for message in storage:
    #    message.delete()
    #    logger.info(message)
    """ table html request """
    song_list = Song.objects.filter(profile=request.user.profile)

    return render(request, 'table.html', {'page_obj': song_list,
                                          'size': song_list.count(), 'profile': request.user.profile})


def login_user(request):
    """ login html request """

    if request.user.is_authenticated:
        # logger.info(f"\'{request.user}\' is currently logged in, logging out")
        logout(request)

    if request.method == "POST":
        user = authenticate(username=request.POST.get('email'),
                            password=request.POST.get('password'))
        if user is not None:
            # logger.info(f"logging in {user}")
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
            user = authenticate(username=user.email, password=raw_password)
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

def delete_message(request):
    logger.info(request)
    storage = get_messages(request)
    for message in storage:
        logger.info(message)
        message.delete()
    return render(requets, 'table.html')


def _bulk_import(request, init_dict, user):
    match_limiter = RateLimiter(max_calls=1, period=3)
    database_limiter = RateLimiter(max_calls=1, period=3)
    matched_songs = []  # songs that have been matched

    # try:
    # rate limiter used for limiting api calls to the matcher api
    if (init_dict['match'] == Detection.MUSICBRAINZS):
        match_limiter = RateLimiter(max_calls=1, period=1)

    # rate limiter used for limiting api calls to the database api
    if (init_dict['metadata'] == Database.MUSICBRAINZ):
        database_limiter = RateLimiter(max_calls=1, period=1)

    if (init_dict['metadata'] == Database.DISCOGS):
        database_limiter = RateLimiter(max_calls=60, period=60)

    # 1) obtains files and enum values based on given media directory and
    # given sting values representing matching methods/databases.
    matching, database, files = directory_scan(init_dict['match'],
                                               init_dict['metadata'], init_dict['file_dir'])

    # 2) matches the detected songs with preffered matching methodology
    # logger.info("Matching songs...")
    messages.add_message(request, messages.INFO, "Starting to match data using selected matching methodology...")
    for file in files:
        with match_limiter:
            matched_songs.append(musiq_match_song(matching, file))
    messages.add_message(request, messages.INFO, "Finished matching data using selected matching methodology.")

    # 3) retrieves song metadata from specified database
    # logger.info("Retrieving metadata...")
    messages.add_message(request, messages.INFO, "Starting to grab metadata from selected database...")
    for match in matched_songs:
        with database_limiter:
            musiq_retrieve_song(match, database, matching, user)
    messages.add_message(request, messages.INFO, "Finished grabbing metadata from selected database.")

    # except Exception as e:
    #    logger.error(f"Error during main bulk import: {e}")


def logout(request):
    auth.logout(request)
    return redirect('login_user')


class BulkImport(Thread):
    '''
        Thread for bulk matching and detecting functionality.
    '''

    def __init__(self, request, user, dict_metadata):
        Thread.__init__(self)
        self.user = user
        self.metadata = dict_metadata
        self.request = request

    def run(self):
        while True:
            try:
                # logger.info("Starting bulk import...")
                _bulk_import(self.request, self.metadata, self.user)
            except Exception as e:
                messages.add_message(self.request, messages.ERROR, "Error during bulk import...")
                logger.error(f"Error during bulk import in a thread: {e}")
            finally:
                # logger.info("Finished bulk import!")
                messages.add_message(self.request, messages.SUCCESS, "Bulk import has finished!")
                return


def update_user_profile(request):
    profile = request.user.profile
    if 'email' in request.POST:
        # logger.info('email' in request.POST)
        request.user.email = request.POST['email']
    if 'first_name' in request.POST:
        # logger.info('first_name' in request.POST)
        request.user.first_name = request.POST['first_name']
    if 'last_name' in request.POST:
        # logger.info('last_name' in request.POST)
        request.user.last_name = request.POST['last_name']
    # request.user.profile.save()
    request.user.save()


@csrf_exempt
def save_song(request):
    file_location = request.POST['id']
    type = request.POST['type']
    value = request.POST['value']
    # logger.info(file_location)
    song = Song.objects.get(file_location=file_location)

    if type == 'artist':
        song.artist = value

    if type == 'album':
        song.album = value

    if type == 'title':
        song.title = value

    if type == 'release_date':
        song.release_date = value

    if type == 'genre':
        song.genre = value

    song.save()
    return JsonResponse({"success": "Updated"})
