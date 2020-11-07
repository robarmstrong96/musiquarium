from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models
from library.models import Profile

class RegistrationForm(UserCreationForm):

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.AutoField(auto_created = True)
    models = models.CharField(max_length=100)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password1", "password2"]

class DiscogzAPIForm(forms.Form):

    discogz = forms.CharField(max_length=100, help_text="Token", label="Discogs")

    class Meta:
        model = Profile
        fields = ["discogz"]

class ImageUploadForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('avatar',)

class BulkInitilization(forms.Form):

    DETECTION=[
        ('MUSICBRAINZ', 'MusicBrainz'),
        ('ACRCLOUD', 'Arcloud'),
        ('METADATA', 'Metadata'),
    ]

    DATABASE=[
        ('MUSICBRAINZ', 'MusicBrainz'),
        ('DISCOGS', 'Discogs'),
    ]

    detection = forms.CharField(widget=forms.Select(choices=DETECTION))
    database = forms.CharField(widget=forms.Select(choices=DATABASE))

    class Meta:
        model = Profile
        fields = ["user_music_location"]
