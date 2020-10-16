import os, sys, psycopg2, logging
from django import forms
from django.db import connection
from library.models import Song
from library.test_run import testrun # relative import
from django.views.generic import ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import RegistrationForm
from django.contrib.auth import login, authenticate

sys.path.append("./musiq_detection")

logger = logging.getLogger("mylogger")

# Create your views here.

@login_required(login_url='/library/login')
def index(request):
    """View function for home page of site."""
    return render(request, 'index.html')

@login_required(login_url='/library/login')
def profile(request):
    """ profile html request """
    # returns profile
    return render(request, 'profile.html')

def update_profile(request, user_id):
    user = User.objects.get(pk=user_id)
    user.save()

@login_required(login_url='/library/login')
def table(request):
    """ profile html request """
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
    return render(request, 'table.html', {'page_obj': page_obj, 'size': song_list.count()})

def drop_table():
    cursor = connection.cursor()
    table_name = Album._meta.db_table
    psql = "DROP TABLE %s CASCADE;" % (table_name, )
    cursor.execute(psql)

    # # returns profile
    # return render(request, 'table.html', {'songs': Song.objects.all()})

def login(request):
    """ profile html request """

    # returns profile if unsucessful
    return render(request, 'login.html', )

def logout(request):
    auth.logout(request)
    return render(request,'login')


def register(request):
    """ profile html request """
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
            auth.login(request, user)
            return redirect('index')
    else:
        form = RegistrationForm()

    # returns profile
    return render(request, 'register.html', {'form': form})
