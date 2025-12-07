from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from .models import User
from .decorators import login_required
from concerts.models import Koncertas
import bcrypt
from datetime import date

# -------------------------------
# MOCK DATA (vietoj tikrų modelių)
# -------------------------------

MOCK_MUSIC = [
    {
        "id": 1,
        "title": "Vasara 2024",
        "genre": "Popmuzika",
        "cover_url": "https://picsum.photos/180?random=10",
        "length_seconds": 210,
    },
    {
        "id": 2,
        "title": "Nakties tyluma",
        "genre": "Rokas",
        "cover_url": "https://picsum.photos/180?random=11",
        "length_seconds": 185,
    },
]

MOCK_PLAYLISTS = [
    {
        "id": 1,
        "title": "Mano mėgstamiausios",
        "created_at": date(2024, 2, 10),
        "author_names": [
            "Gytis Kaulakis",
            "Ramūnas Vengrauskas",
            "Trečias atlikėjas",
            "Ketvirtas atlikėjas",
        ],
        "cover_url": "https://picsum.photos/180?random=21",
    },
    {
        "id": 2,
        "title": "Rytiniai hitai",
        "created_at": date(2023, 12, 5),
        "author_names": ["Gytis Kaulakis", "Ramūnas Vengrauskas"],
        "cover_url": "https://picsum.photos/180?random=22",
    },
]

def get_hashed_password(plain_text_password):
    # Hash a password for the first time
    #   (Using bcrypt, the salt is saved into the hash itself)
    return bcrypt.hashpw(bytes(plain_text_password, "utf-8"), bcrypt.gensalt())

def check_password(plain_text_password, hashed_password):
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(bytes(plain_text_password, "utf-8"), hashed_password)


# Create your views here.
def index(request):

    context = {
        "request": request,
        "users": User.objects.all()
    }

    return render(request, "users/index.html", context)


def loginUser(request: HttpRequest):
    errors = []
    form = {"username": "", "password": "", "next": request.GET.get("next", "")}
    if request.method == "POST":
        # Gaunami duomenys
        username = request.POST["username"]
        password = request.POST["password"]

        # Formoje palaikomi duomenys klaidos atveju
        form["username"] = username
        form["password"] = password

        # Duomenų tikrinimas
        if len(username) == 0:
            errors.append("Naudotojo vardas tuščias.")
        if len(password) == 0:
            errors.append("Slaptažodis tuščias.")
        if len(username) > 0 and len(password) > 0:
            try:
                user = User.objects.get(username=username)

                if(not check_password(password, user.password_hash)):
                    errors.append("Slaptažodis neteisingas. Pabandykite dar kartą.")
                    form["password"] = ""
                else:
                    request.session["user"] = True
                    request.session["user_id"] = user.pk
                    request.session["user_name"] = user.username
                    request.session["user_email"] = user.email
                    request.session["user_role"] = user.role
                    request.session.modified = True

                    next = request.POST.get("next") or "homepage"
                    print("NEXT", next)
                    return redirect(next)
            except User.DoesNotExist:
                errors.append("Šis naudotojas neegzistuoja.")

    return render(request, "users/login.html", {"errors": errors, "form": form})


def registerUser(request):
    errors = []
    form = {"username": "", "email": "", "password_new": "", "password_repeat": ""}
    if request.method == "POST":
        # Gaunami duomenys
        username = request.POST["username"]
        email = request.POST["email"]
        password_new = request.POST["password_new"]
        password_repeat = request.POST["password_repeat"]

        # Formoje palaikomi duomenys klaidos atveju
        form["username"] = username
        form["email"] = email
        form["password_new"] = password_new
        form["password_repeat"] = password_repeat

        # Duomenų tikrinimas
        if (password_new != password_repeat):
            errors.append("Slaptažodis ir jo pakartojimas nėra vienodi")
            form["password_new"] = ""
            form["password_repeat"] = ""
        else:
            password_hash = get_hashed_password(password_new)

            user, created = User.objects.get_or_create(
                username = username,
                email = email,
                password_hash = password_hash,
                display_name = username,
            )
            if created:
                return redirect('users:userLogin')
            else:
                errors.append("Naudotojas jau egzistuoja.")

    context = {"errors": errors, "form": form}

    return render(request, "users/register.html", context)


@login_required
def userEdit(request):
    user = User.objects.get(pk=request.session["user_id"])
    return render(request, "users/edit.html", {"user": user})


def userDetail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    # user.koncertai - Pagal `Koncertas` modelio `author` atributą, kuriam related_name="koncertai"
    concerts = user.koncertai.all() # type: ignore

    context = {
        "request": request,
        "user": user,
        "music": MOCK_MUSIC,
        "playlists": MOCK_PLAYLISTS,
        "koncertai": concerts,
    }

    return render(request, "users/userDetail.html", context)

def logoutUser(request):
    request.session.flush()
    return redirect("homepage")

@login_required(User.RoleChoices.ADMIN)
def admin(request: HttpRequest):
    return render(request, "users/admin.html")

@login_required(User.RoleChoices.ADMIN)
def adminUsers(request: HttpRequest):
    context = {"errors": [], "users": User.objects.all()}
    return render(request, "users/adminUsers.html", context)