from django.contrib.auth.models import Permission, User
from django.db import models


class Movies(models.Model):
    user = models.ForeignKey(User, default=1)
    movie_name = models.CharField(max_length=500)
    movie_logo = models.FileField()
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.movie_name


class Songs(models.Model):
    movie = models.ForeignKey(Movies, on_delete=models.CASCADE)
    song_title = models.CharField(max_length=300)
    audio_file = models.FileField(default='')
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.song_title
