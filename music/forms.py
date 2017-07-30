from django import forms
from django.contrib.auth.models import User
from .models import Movies, Songs


class MovieForm(forms.ModelForm):

    class Meta:
        model = Movies
        fields = ['movie_name', 'movie_logo']


class SongForm(forms.ModelForm):

    class Meta:
        model = Songs
        fields = ['song_title', 'audio_file']


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

