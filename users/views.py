from django.shortcuts import render, redirect
from datetime import date
from django.contrib.auth import logout

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


# Create your views here.
def index(request):

    context = {
        "request": request,
        "users": MOCK_USERS,
    }

    return render(request, "users/index.html", context)


def createUser(request):
    return render(request, "users/createUser.html")


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
    logout(request)
    return redirect("homepage")
