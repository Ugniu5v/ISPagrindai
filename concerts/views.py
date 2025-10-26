from django.shortcuts import render


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
    return render(request, "concerts/concertDetail.html")


def recommendationConcert(request):
    return render(request, "concerts/recommendationConcert.html")
