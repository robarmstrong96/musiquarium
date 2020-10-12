from django.shortcuts import render
from django.db import connection
from library.models import Song, Artist, Album, Genre

import psycopg2

# Create your views here.

def index(request):
    """View function for home page of site."""

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html')

def profile(request):
    """ profile html request """

    # returns profile
    return render(request, 'profile.html')

def table(request):
    """ profile html request """

    #drop_table()
    if(Artist.objects.filter(artist = "Limp Bizkit").exists() == False):
        artist = Artist(artist = "Limp Bizkit")
        artist.save()
    if(Album.objects.filter(album = "Sam's Greatest Hits").exists() == False):
        album = Album.objects.create(artist = artist, album = "Sam's Greatest Hits")
    if(Genre.objects.filter(genre="music to fuck to").exists() == False):
        genre = Genre(genre="music to fuck to")
        genre.save()
        album.genre.add(genre)
        album.save()
    if(Song.objects.filter(title = "Toxic", album__album__contains="Sam's Greatest Hits").exists() == False):
        temp = Song.objects.create(title = "Toxic", file_size = 0, duration = 1, artist = artist, album = album)
        temp.save()
    return render(request, 'table.html', {'songs': Song.objects.all()})

def drop_table():
    cursor = connection.cursor()
    table_name = Album._meta.db_table
    psql = "DROP TABLE %s CASCADE;" % (table_name, )
    cursor.execute(psql)

    # returns profile
    # return render(request, 'table.html', {'songs': Song.objects.all()})

def login(request):
    """ profile html request """

    # returns profile
    return render(request, 'login.html')

def register(request):
    """ profile html request """

    # returns profile
    return render(request, 'register.html')
