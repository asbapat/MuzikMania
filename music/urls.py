from django.conf.urls import url
from . import views

app_name = 'music'

urlpatterns = [
    # /music/
    url(r'^$', views.index, name='index'),
    # /music/<movie_id>
    url(r'^(?P<movie_id>[0-9]+)/$', views.detail, name='detail'),
    # /music/<movie_id>/favorite/
    url(r'^(?P<movie_id>[0-9]+)/favorite/$', views.favorite, name='favorite'),
    url(r'^create_movie/$', views.create_movie, name='create_movie'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login_user/$', views.login_user, name='login_user'),
    url(r'^logout_user/$', views.logout_user, name='logout_user'),
    url(r'^songs/(?P<filter_by>[a-zA_Z]+)/$', views.songs, name='songs'),
    url(r'^(?P<movie_id>[0-9]+)/create_song/$', views.create_song, name='create_song'),
    url(r'^(?P<movie_id>[0-9]+)/delete_song/(?P<song_id>[0-9]+)/$', views.delete_song, name='delete_song'),
    url(r'^(?P<movie_id>[0-9]+)/favorite_movie/$', views.favorite_movie, name='favorite_movie'),
    url(r'^(?P<movie_id>[0-9]+)/delete_movie/$', views.delete_movie, name='delete_movie'),
]

