from django.shortcuts import render
import requests


# Create your views here.
def index(request):
    return render(request, "concerts/index.html")


def createConcert(request):
    return render(request, "concerts/createConcert.html")


def editConcert(request):
    return render(request, "concerts/editConcert.html")


def searchConcert(request):
    return render(request, "concerts/searchConcert.html")


def concertDetail(request):
    concert_location = {
        'lat': 40.7128,
        'lng': -74.0060,
        'name': 'Madison Square Garden'
    }
    return render(request, "concerts/concertDetail.html", {'location': concert_location})


def recommendationConcert(request):
    return render(request, "concerts/recommendationConcert.html")
