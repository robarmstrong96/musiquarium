from django.shortcuts import render

# Create your views here.

from library.models import Song, Artist, Album, Genre

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

    artist = Artist(artist = "Limp Bizkit")
    artist.save()
    album = Album.objects.create(artist = artist, album = "Sam's Greatest Hits")
    genre = Genre(genre="music to fuck to")
    genre.save()
    album.genre.add(genre)
    album.save()
    temp = Song.objects.create(title = "Toxic", file_size = 0, duration = 1, artist = artist, album = album)
    temp.save()


    # returns profile
    return render(request, 'table.html', {'songs': Song.objects.all()})

def login(request):
    """ profile html request """

    # returns profile
    return render(request, 'login.html')

def register(request):
    """ profile html request """

    # returns profile
    return render(request, 'register.html')
