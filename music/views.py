from django.http import HttpResponse
from django.http import Http404
from django.template import loader
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .forms import MovieForm, SongForm, UserForm
from .models import Movies, Songs


AUDIO_FILE_TYPES = ['wav', 'mp3', 'ogg']
IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']


# METHOD 1
# def index(request):
#     movies_all = Movies.objects.all()
#     # html = " "
#     template = loader.get_template('music/index.html')
#     context = {
#         "movies_all": movies_all,
#     }
#     # avoid writing html code in python files
#     # for mov in movies_all:
#     #     url = '/music/' + str(mov.id) + '/'
#     #     html += '<a href = "' + url + '">'+ mov.movie + '</a><br>'
#     return HttpResponse(template.render(context, request))
#
# METHOD 2 (Using render shortcut)
def index(request):
    if not request.user.is_authenticated():
        return render(request, 'music/login.html')
    else:
        movies = Movies.objects.filter(user=request.user)
        song_results = Songs.objects.all()
        query = request.GET.get("q")
        if query:
            movies = movies.filter(
                Q(movie_name__icontains=query)
            ).distinct()
            song_results = song_results.filter(
                Q(song_title__icontains=query)
            ).distinct()
            return render(request, 'music/index.html', {
                'movies': movies,
                'songs': song_results,
            })
        else:
            return render(request, 'music/index.html', {'movies': movies})

# def detail(request, movie_id):
#     try:
#         movie = Movies.objects.get(id = movie_id)
#     except Movies.DoesNotExist:
#         raise Http404("Movie does not exist")
#     return render(request, 'music/detail.html', {"movie": movie})


# Using 404 shortcut
def detail(request, movie_id):
    if not request.user.is_authenticated():
        return render(request, 'music/login.html')
    else:
        user = request.user
        movie = get_object_or_404(Movies, pk=movie_id)
        return render(request, 'music/detail.html', {'movie': movie, 'user': user})


def create_movie(request):
    if not request.user.is_authenticated():
        return render(request, 'music/login.html')
    else:
        form = MovieForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            movie = form.save(commit=False)
            movie.user = request.user
            movie.movie_logo = request.FILES['movie_logo']
            file_type = movie.movie_logo.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in IMAGE_FILE_TYPES:
                context = {
                    'movie': movie,
                    'form': form,
                    'error_message': 'Image file must be PNG, JPG, or JPEG',
                }
                return render(request, 'music/create_movie.html', context)
            movie.save()
            return render(request, 'music/detail.html', {'movie': movie})
        context = {
            "form": form,
        }
        return render(request, 'music/create_movie.html', context)


def create_song(request, movie_id):
    form = SongForm(request.POST or None, request.FILES or None)
    movie = get_object_or_404(Movies, pk=movie_id)
    if form.is_valid():
        movie_songs = movie.songs_set.all()
        for s in movie_songs:
            if s.song_title == form.cleaned_data.get("song_title"):
                context = {
                    'movie': movie,
                    'form': form,
                    'error_message': 'You already added that song',
                }
                return render(request, 'music/create_song.html', context)
        song = form.save(commit=False)
        song.movie = movie
        song.audio_file = request.FILES['audio_file']
        file_type = song.audio_file.url.split('.')[-1]
        file_type = file_type.lower()
        if file_type not in AUDIO_FILE_TYPES:
            context = {
                'movie': movie,
                'form': form,
                'error_message': 'Audio file must be WAV, MP3, or OGG',
            }
            return render(request, 'music/create_song.html', context)
        song.save()
        return render(request, 'music/detail.html', {'movie': movie})
    context = {
        'movie': movie,
        'form': form,
    }
    return render(request, 'music/create_song.html', context)


def delete_movie(request, movie_id):
    movie = Movies.objects.get(pk=movie_id)
    movie.delete()
    movies = Movies.objects.filter(user=request.user)
    return render(request, 'music/index.html', {'movies': movies})


def delete_song(request, movie_id, song_id):
    movie = get_object_or_404(Movies, pk=movie_id)
    song = Songs.objects.get(pk=song_id)
    song.delete()
    return render(request, 'music/detail.html', {'movie': movie})


def favorite(request, song_id):
    song = get_object_or_404(Songs, pk=song_id)
    try:
        if song.is_favorite:
            song.is_favorite = False
        else:
            song.is_favorite = True
        song.save()
    except (KeyError, Songs.DoesNotExist):
        return JsonResponse({'success': False})
    else:
        return JsonResponse({'success': True})


def favorite_movie(request, movie_id):
    movie = get_object_or_404(Movies, pk=movie_id)
    try:
        if movie.is_favorite:
            movie.is_favorite = False
        else:
            movie.is_favorite = True
        movie.save()
    except (KeyError, Movies.DoesNotExist):
        return JsonResponse({'success': False})
    else:
        return JsonResponse({'success': True})


def songs(request, filter_by):
    if not request.user.is_authenticated():
        return render(request, 'music/login.html')
    else:
        try:
            song_ids = []
            for movie in Movies.objects.filter(user=request.user):
                for song in movie.songs_set.all():
                    song_ids.append(song.pk)
            users_songs = Songs.objects.filter(pk__in=song_ids)
            if filter_by == 'favorites':
                users_songs = users_songs.filter(is_favorite=True)
        except Movies.DoesNotExist:
            users_songs = []
        return render(request, 'music/songs.html', {
            'song_list': users_songs,
            'filter_by': filter_by,
        })


def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                movies = Movies.objects.filter(user=request.user)
                return render(request, 'music/index.html', {'movies': movies})
    context = {
        "form": form,
    }
    return render(request, 'music/register.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                movies = Movies.objects.filter(user=request.user)
                return render(request, 'music/index.html', {'movies': movies})
            else:
                return render(request, 'music/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'music/login.html', {'error_message': 'Invalid login'})
    return render(request, 'music/login.html')


def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'music/login.html', context)
