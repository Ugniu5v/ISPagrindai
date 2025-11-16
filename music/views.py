from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.
def index(request):
    return render(request, "music/index.html")


def createSong(request):
    return render(request, "music/createSong.html")


def rateSong(request):
    return render(request, "music/rateSong.html")


def editSong(request):
    return render(request, "music/editSong.html")


def playSong(request):
    # Intentionally blank response for play placeholder
    return HttpResponse("")


def similarSongs(request):
    return render(request, "music/similarSongs.html")
