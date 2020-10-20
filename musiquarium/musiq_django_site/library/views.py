import os, sys, psycopg2, logging, _thread
from threading import Thread, Lock
from django import forms
from django.db import connection
from library.models import Song
from library.test_run import testrun # relative import
from django.views.generic import ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import RegistrationForm, DiscogzAPIForm
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect, HttpResponse
from library.detection_music import discogz_personal_client, discogz_data_retrieval, musicbrainz_detect, discogz_client_authorization, discogz_get_client

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
    logger.info(f" Type = {request.method}")
    return render(request, 'index.html')

@login_required(login_url='/library/login_user')
def profile(request):
    """ profile html request """

    # returns profile
    if request.method == 'POST':
        form = update_profile(request) # Updates profile model, returns form with updated data
    else:
        form = DiscogzAPIForm()

    # generate client api key
    # if request.method == 'POST' and 'authenticate' in request.POST:
        #client = discogz_get_client() # 1) get discogz client instance
        #request_token, request_secret, url = client.get_authorize_url() # 2) get request information
        #discogz_client_authorization(client, request.user.profile)
        #return HttpResponseRedirect(url)

    return render(request, 'profile.html', {'form': form, 'profile': request.user.profile})

@login_required(login_url='/library/login_user')
def table(request):
    """ table html request """
    #testrun()
    song_list = Song.objects.all()
    page_number = request.GET.get('page', 1) # parses url GET for page
    paginator = Paginator(song_list, 10)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    if request.method == "POST" and 'organize' in request.POST:
        detect = PopulateThreading(request.user)
        detect.daemon = True
        detect.start()
        #list = testrun()
        #logger.info("Starting data retrieval..")
        #musicbrainz_detect(list, request.user)

    return render(request, 'table.html', {'page_obj': page_obj, 'size': song_list.count(), 'profile': request.user.profile})

def login_user(request):
    """ login html request """
    # returns profile if unsucessful

    logger.info(request.method)
    if request.method == "POST":
        logger.info(request.method)
        user = authenticate(username=request.POST.get('email'), password=request.POST.get('password'))
        if user is not None:
            login(request, user)
            return render(request, 'index.html')
    return render(request, 'login_user.html', )

def register(request):
    """ register html request """
    logger.info(f'request: {request.method}')
    if request.method == 'POST':
        logger.info(" Successful, it was get! ")
        form = RegistrationForm(request.POST)
        logger.info(f"\'{form}\' form info ")
        logger.info(f"{form.is_valid()} form info\n")
        if form.is_valid():
            logger.info(" Successful, form is valid! ")
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
    return render(request, 'login_user.html')

class PopulateThreading(Thread):

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
                logger.info(f"List size: {list} Starting data retrieval..")
                musicbrainz_detect(list, user)
                #discogz_data_retrieval(list, client)
            except:
                logger.error(sys.exc_info()[0])
            finally:
                logger.info("Finished thread!")
                return True

def drop_table():
    cursor = connection.cursor()
    table_name = Album._meta.db_table
    psql = "DROP TABLE %s CASCADE;" % (table_name, )
    cursor.execute(psql)

    # # returns profile
    # return render(request, 'table.html', {'songs': Song.objects.all()})

def update_profile(request):
    profile = request.user.profile
    form = DiscogzAPIForm(request.POST or None)
    if form.is_valid():
        profile.discogz = request.POST['discogz']
        profile.save()
    request.user.save()

    return form

def upload_image(request):
    from django.core.files.storage import FileSystemStorage
    if request.method == 'POST' and request.FILES['avatar']:
        myfile = request.FILES['avatar']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_image_url = fs.url(filename)
        return render(request, 'profile.html', {
            'uploaded_image_url': uploaded_image_url
        })
    return render(request, 'profile.html')
