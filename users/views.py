from django.shortcuts import render, redirect
from django.http import HttpRequest
from .models import User
import bcrypt


# from django.contrib.auth import logout, authenticate, login
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

MOCK_CONCERTS = [
    {
        "id": 1,
        "title": "Vasaros Festas",
        "start_date": date(2024, 6, 15),
        "place": {"title": "Vingio parkas", "city": "Vilnius"},
        "going_state": "Dalyvauja",
        "cover_url": "https://picsum.photos/320/180?random=31",
        "going_count": 12,
        "interested_count": 35,
    },
    {
        "id": 2,
        "title": "Roko Naktis",
        "start_date": date(2024, 8, 20),
        "place": {"title": "Žalgirio Arena", "city": "Kaunas"},
        "going_state": "Domina",
        "cover_url": "https://picsum.photos/320/180?random=32",
        "going_count": 22,
        "interested_count": 47,
    },
]

MOCK_USERS = [
    {
        "id": 1,
        "name": "Gytis Kaulakis",
        "email": "gytis@gmail.com",
        "image_url": "https://picsum.photos/180?random=1",
        "fallower_count": 31,
    },
    {
        "id": 2,
        "name": "Ramūnas Vengrauskas",
        "email": "ramunas@gmail.com",
        "image_url": "https://picsum.photos/180?random=2",
        "fallower_count": 52,
    },
    {
        "id": 3,
        "name": "Ignas Nakčeris",
        "email": "ignas@gmail.com",
        "image_url": "https://picsum.photos/180?random=3",
        "fallower_count": 7,
    },
    {
        "id": 4,
        "name": "Ugnius Varžukas",
        "email": "ugnius@gmail.com",
        "image_url": "https://picsum.photos/180?random=4",
        "fallower_count": 70,
    },
    {
        "id": 5,
        "name": "Cool dainininkas",
        "email": "dainininkas@gmail.com",
        "image_url": "https://picsum.photos/180?random=5",
        "fallower_count": 32946,
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
        "users": MOCK_USERS,
    }

    return render(request, "users/index.html", context)


def loginUser(request):
    errors = []
    form = {"username": "", "password": ""}
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
                    request.session.modified = True
                    return redirect("homepage")
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


def editUser(request):
    return render(request, "users/editUser.html")


def userDetail(request, user_id):
    user = next((user for user in MOCK_USERS if user["id"] == user_id), None)

    context = {
        "request": request,
        "user": user,
        "music": MOCK_MUSIC,
        "playlists": MOCK_PLAYLISTS,
        "concerts": MOCK_CONCERTS,
    }

    return render(request, "users/userDetail.html", context)


def logoutUser(request):
    request.session.flush()
    return redirect("homepage")
