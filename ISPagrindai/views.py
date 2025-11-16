from django.shortcuts import render


def homepage(request):
    context = {
        "request": request,
    }
    return render(request, "homepage.html", context)
