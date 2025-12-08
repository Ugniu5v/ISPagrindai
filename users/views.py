from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpRequest
from .models import User
from .decorators import login_required
import bcrypt
from datetime import date
from datetime import datetime


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
        "users": User.objects.filter(is_public=True, is_blocked=False)
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
                    request.session["user_display_name"] = user.display_name
                    request.session["user_email"] = user.email
                    request.session["user_role"] = user.role
                    request.session["user_role_label"] = user.get_role_display() # type: ignore
                    if user.profile_cover_url:
                        request.session["user_profile_cover_url"] = user.profile_cover_url.url
                    request.session.modified = True

                    user.last_login_at = datetime.now()
                    user.save()

                    next = request.POST.get("next") or "homepage"
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
def userEdit(request: HttpRequest):
    errors = []
    info = []
    form = {"display_name": "", "email": "", "biography": "", "two_factor_enabled": False, "is_public": False, "date_of_birth": ""}
    user = User.objects.get(pk=request.session["user_id"])
    context = {"errors": errors, "info": info, "form": form, "user": user}

    if request.method == "GET":
        form["display_name"] =      user.display_name
        form["email"] =             user.email
        form["biography"] =         user.biography or "" 
        form["two_factor_enabled"] = user.two_factor_enabled
        form["is_public"] =         user.is_public
        form["date_of_birth"] =     user.date_of_birth
    elif request.method == "POST":
        # Gaunami duomenys
        display_name =           form["display_name"] =      request.POST["display_name"]
        email =              form["email"] =             request.POST["email"]
        biography =          form["biography"] =         request.POST["biography"]
        profile_cover =  request.FILES["profile_cover_url"] if "profile_cover_url" in request.FILES else None 
        two_factor_enabled = form["two_factor_enabled"] = "two_factor_enabled" in request.POST
        is_public =          form["is_public"] =         "is_public" in request.POST
        date_of_birth =      form["date_of_birth"] =     request.POST["date_of_birth"]

        user.display_name = display_name
        user.email = email
        user.biography = biography
        if profile_cover:
            user.profile_cover_url = profile_cover # type: ignore
        user.two_factor_enabled = two_factor_enabled
        user.is_public = is_public

        if date_of_birth != "":
            user.date_of_birth = date.fromisoformat(date_of_birth)

        user.save()

        request.session["user_display_name"] = display_name
        request.session["user_email"] = email

        if user.profile_cover_url:
            request.session["user_profile_cover_url"] = user.profile_cover_url.url

        info.append("Profilio informacija sėkmingai atnaujinta!")
        # return redirect("users:userDetail", user_id=request.session["user_id"])


    return render(request, "users/edit.html", context)

# TODO: Sugalvot ar daryt modalą ar ką
@login_required
def userTwoFa(request: HttpRequest):
    print("Labas")
    return redirect('users:userEdit')


def userDetail(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    # user.koncertai - Pagal `Koncertas` modelio `author` atributą, kuriam related_name="koncertai"
    concerts = user.koncertai.all() # type: ignore
    playlists = user.grojarasciai.all() # type: ignore
    dainos = user.dainos.all() # type: ignore

    context = {
        "request": request,
        "user": user,
        "dainos": dainos,
        "playlists": playlists,
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
    errors = []
    info = []
    if request.method == "POST":
        if "block" in request.POST:
            user_id = request.POST["block"]
            if user_id == request.session["user_id"]:
                errors.append("Negalima blokuoti savęs")
            else:
                user = User.objects.get(pk=user_id)
                user.is_blocked = True
                user.save()
                info.append(f"Sėkmingai užblokuotas naudotojas '{user.display_name}'")
        elif "unblock" in request.POST:
            user_id = request.POST["unblock"]
            if user_id == request.session["user_id"]:
                errors.append("Negalima atblokuoti savęs")
            else:
                user = User.objects.get(pk=user_id)
                user.is_blocked = False
                user.save()
                info.append(f"Sėkmingai atblokuotas naudotojas '{user.display_name}'")
        else:
            errors.append("Nesuprastas veiksmas")

    context = {"errors": errors, "info": info, "users": User.objects.all()}
    return render(request, "users/adminUsers.html", context)