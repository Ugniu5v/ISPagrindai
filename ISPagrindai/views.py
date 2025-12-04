from django.shortcuts import render


def homepage(request):
    user = None
    if "user" in request.session:
        user = {"name": request.session["user_name"]}

    context = {"request": request, "user": user}
    return render(request, "homepage.html", context)
