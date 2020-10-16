import sys, os
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.contrib.auth.forms import UserCreationForm
from django.dispatch import receiver

class Song(models.Model):
    # Stored File Information
    # file = models.FileField(_('File'),  blank=True, null=True)
    file_size = models.IntegerField(_('File size'),editable=False)
    duration = models.IntegerField(_('Song duration in seconds'),editable=False,default=0)

    # Song DB variables
    # play_count = models.IntegerField(_('Play count'), default=0, blank=True, null=True)
    title = models.CharField(_('Title'), max_length=100)
    track_number = models.SmallIntegerField(_('Track number'), blank=True, null=True)
    disc_number = models.SmallIntegerField(_('Disc number'), blank=True, null=True)
    disc_total = models.SmallIntegerField(_('Total disc count'), blank=True, null=True)
    detection_method = models.CharField(_('Detection method'), max_length=100, default='no detection method set', help_text='Select a genre for this book')

    # Foreign Keys
    #artist = models.ForeignKey('Artist', on_delete=models.CASCADE, default=0)
    #album = models.ForeignKey('Album', on_delete=models.RESTRICT, default=0)
    #genre = models.ManyToManyField('Genre', max_length=64, blank=True, default="N/A")

    # instead of making models for album, genre and artist i will just make them simple text fields for simplicity
    artist = models.CharField(_('Artist'), max_length=64, blank=True, default="Unknown Artist")
    album = models.CharField(_('Album'), max_length=64, blank=True, default="Unknwon Album")
    genre = models.CharField(_('Genre'), max_length=32, blank=True, default="Unknwon Genre")

    class Meta:
        # Changes based on user preference
        unique_together = (('artist', 'album','title'),)
        db_table = 'library_song'
        verbose_name = ("Song")
        verbose_name_plural = ("Songs")
        ordering = ['artist', '-album', '-title']

    def get_artist():
        return self.artist

    def get_album():
        return self.album

    def get_genre():
        return self.genre

    def __str__(self):
        return self.title

class Profile(models.Model):
    """
        This model extends the base user model, allowing us to utilize the pre-built user model
        while adding some extra functionality (i.e. storage of api key's for database authentication)
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    discogz = models.CharField(_('Discogz User Authentication Key'), max_length=100)

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

# class Album(models.Model):
#
#     # Album DB variables
#     album = models.CharField(_('Album'), max_length=64, blank=True, unique=True)
#     year = models.CharField(_('Year'), max_length=4, blank=True)
#     track_total = models.SmallIntegerField(_('Total track count'), blank=True, null=True)
#     publisher = models.CharField(_('Publisher'), max_length=100, blank=True)
#     #cover_image = models.ImageField(_('Cover image'), upload_to=get_cover_upload_path, blank=True)
#
#     # Foreign Keys
#     artist = models.ForeignKey('Artist', on_delete=models.CASCADE, default=0)
#     genre = models.ManyToManyField('Genre', max_length=64, blank=True, default="N/A")
#
#     class Meta:
#         # Changes based on user preference
#         db_table = 'library_album'
#         verbose_name = ("Album")
#         ordering = ['album', '-artist', '-year']
#
#     def __str__(self):
#         return self.album
#
# class Genre(models.Model):
#
#     genre = models.CharField(_('Genre'), max_length=200, blank=True, unique=True, default="N/A")
#
#     class Meta:
#         # Changes based on user preference
#         db_table = 'library_genre'
#         verbose_name = ("Genre")
#         verbose_name_plural = ("Genres")
#         ordering = ['genre']
#
#     def get_genre():
#         return self.genre
#
#     def __str__(self):
#         return self.genre
#
# class Artist(models.Model):
#
#     # Artist DB variables
#     artist = models.CharField(_('Artist'), max_length=100, unique=True)
#
#     class Meta:
#         # Changes based on user preference
#         db_table = 'library_artist'
#         verbose_name = ("Artist")
#         ordering = ['artist']
#
#     def __str__(self):
#         return self.artist
