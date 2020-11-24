import sys, os, datetime, discogs_client, environ
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.contrib.auth.forms import UserCreationForm
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist

# grabs .env information
environ.Env.read_env()
_env = environ.Env()
_ck = _env('CONSUMER_KEY')
_cs = _env('CONSUMER_SECRET')
_rtu = _env('REQUEST_TOKEN_URL')
_au = _env('AUTHORIZE_URL')
_atu = _env('ACCESS_TOKEN_URL')
_pt = _env("PERSONAL_TOKEN")

# registered application name represented as a string
user_agent = 'musiquarium/0.1'

""" Profile Information """

class Profile(models.Model):
    """
        This model extends the base user model, allowing us to utilize the pre-built user model
        while adding some extra functionality (i.e. storage of api key's for database authentication)
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    discogs_client = discogs_client.Client(user_agent) # temporary
    discogs_client.set_consumer_key(_ck, _cs) # temporary
    discogs_access_token = models.CharField(_('Discogs Access Token'), max_length=128, blank=True, null=True)
    discogs_access_secret = models.CharField(_('Discogs Access Secret'), max_length=128, blank=True, null=True)
    user_music_location = models.CharField(_('Music Folder Directory'), max_length=512, help_text="File Directory", blank=True, null=True)

    class Meta:
        verbose_name = ("Profile")
        verbose_name_plural = ("Profiles")
        ordering = ['user']

    def get_image_path(instance, filename):
        return os.path.join("assets/img/avatars/", filename)

    avatar = models.ImageField(upload_to=get_image_path, default="assets/img/default/avatar_male.png")

    def __str__(self):
        return self.user.username

    def set_image_path(self, filename):
        if os.path.exists(self.avatar.__str__()): # deletes previous avatar image
            os.remove(self.avatar.__str__())
        self.avatar = os.path.join("assets/img/avatars/", filename)

    def get_discogs_info(self):
        return self.discogs_access_token, self.discogs_access_secret

# signal method which creates current user associated profile upon profile creation
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
        This [signal] function automatically associates a user with a profile
        upon creation.
    """
    try:
        instance.profile.save()
    except ObjectDoesNotExist:
        Profile.objects.create(user=instance)

# sets username upon profile creation
def set_username(sender, instance, **kwargs):
    """
        Automatically sets the username for a profile/user upon creation.
    """
    if not instance.username:
        username = instance.email
        counter = 1
        while User.objects.filter(username=username):
            username = instance.email
            counter += 1
        instance.username = username
models.signals.pre_save.connect(set_username, sender=User)

""" Music information """


class Song(models.Model):
    """
        This model defines a song in the musiquarium application. A song contains
        various metadata, including artist, album and album art information.
    """
    # Stored json information
    json_item = models.CharField(max_length=4000, blank=True, null=True)

    # Stored File Information
    album_artwork = models.ImageField(upload_to="img/album_artwork/", default="img/default/null.png", blank=True, null=True)
    duration = models.IntegerField(_('Song duration in seconds'),editable=False,default=0)
    file_location = models.FileField(_('File Location'), max_length=512, null=True)

    # Song DB variables
    title = models.CharField(_('Title'), max_length=256)
    track_number = models.SmallIntegerField(_('Track number'), blank=True, null=True)
    disc_number = models.SmallIntegerField(_('Disc number'), blank=True, null=True)
    disc_total = models.SmallIntegerField(_('Total disc count'), blank=True, null=True)
    detection_method = models.CharField(_('Detection method'), max_length=192, default='no detection method set', help_text='Select a genre for this book')
    release_date = models.CharField(_('Release Year'), default=datetime.date.today, blank=True, null=True, max_length=32)

    # instead of making models for album, genre and artist i will just make them simple text fields for simplicity
    artist = models.CharField(_('Artist'), max_length=64, blank=True, default="Unknown Artist")
    album = models.CharField(_('Album'), max_length=64, blank=True, default="Unknown Album")
    genre = models.CharField(_('Genre'), max_length=32, blank=True, default="Unknown Genre")

    # musiquarium user information (i.e. profile associated with song data)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = (('artist', 'album','title'),)
        db_table = 'library_song'
        verbose_name = ("Song")
        verbose_name_plural = ("Songs")
        ordering = ['artist', '-album', '-title']

    def get_json():
        return json.loads(self.json_item)

    def __str__(self):
        return self.title
