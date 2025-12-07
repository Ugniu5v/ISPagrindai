from django.shortcuts import render
from concerts.models import Koncertas
from users.models import User
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

    users = User.objects.filter(is_public=True, is_blocked=False)

    context = {"request": request, "koncertai": koncertai, "users": users}
    return render(request, "homepage.html", context)
