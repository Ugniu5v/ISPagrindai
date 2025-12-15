from django.shortcuts import render
from concerts.models import Koncertas
from users.models import Following, User
from music.models import Daina
from playlists.models import Grojarastis
from datetime import datetime
from datetime import timedelta
from django.utils import timezone

def homepage(request):
    # user = None
    # if "user" in request.session:
    #     user = {"name": request.session["user_name"]}

    today = timezone.now().date()
    week_end = today + timedelta(days=7)
    koncertai = Koncertas.objects.filter(pradzios_data__gte=today, pradzios_data__lte=week_end)
    koncertai = koncertai.order_by("-pradzios_data")
    grojarasciai = Grojarastis.objects.filter(yra_viesas=True)
    dainos = Daina.objects.filter(yra_viesa=True)
    users = User.objects.filter(is_public=True, is_blocked=False)

    context = {
        "request": request, 
        "dainos": dainos, 
        "koncertai": koncertai, 
        "users": users, 
        "grojarasciai": grojarasciai}
    
    if "user" in request.session:
        user = User.objects.get(pk = request.session["user_id"])
        followed_users = User.objects.filter(
            followers__follower=user,
            followers__state=Following.FollowingChoices.ACTIVE,
        )
        context["fallowers"] = followed_users
    return render(request, "homepage.html", context)
