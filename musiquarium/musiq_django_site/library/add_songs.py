#from models import Song, Artist, Album, Genre
#import psycopg2
import sys, pathlib
sys.path.append(pathlib.Path(__file__).resolve())
from musiq_django_site import settings
from django.core.management import setup_environ
setup_environ(settings)

def add_songs_to_database(songs):
    for song in songs:
        artist = "N/A"
        print(f'{song[2]} {song[3]}')
        if(Artist.objects.filter(artist = song[3]).exists() == False):
            artist = Artist(artist = song[3])
            artist.save()
        if(Song.objects.filter(title = song[2], album__album__contains=song[3]).exists() == False):
            temp = Song.objects.create(title = song[2], file_size = 0, duration = 1, artist = artist, album = "N/A")
            temp.save()
