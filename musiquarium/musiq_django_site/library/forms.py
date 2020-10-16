from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models

class RegistrationForm(UserCreationForm):

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.AutoField(auto_created = True)
    models = models.CharField(max_length=100)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password1", "password2"]
