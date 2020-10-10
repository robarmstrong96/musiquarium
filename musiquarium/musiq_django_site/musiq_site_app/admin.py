from django.contrib import admin
from musiq_site_app.models import Song # Imports the Song Model/class from the models.py file in our app directory

# Register your models here.

class SongAdmin(admin.ModelAdmin): # Testing admin model importing/registration
    pass
admin.site.register(Song, SongAdmin)
