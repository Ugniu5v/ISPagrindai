import mimetypes
import os
import math
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt

from django.db.models import Avg, Count, Max
from django.http import FileResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from django.contrib import messages

from .models import Daina, DainosVertinimas, DainosKlausymas
from users.models import User
from users.decorators import login_required
from playlists.models import Grojarastis, GrojarastisDaina
from django.db import models
from django.utils import timezone
import json


# Create your views here.
def index(request):
    songs = Daina.objects.all().order_by("-ikelimo_data", "-pk")
    return render(
        request,
        "music/index.html",
        {
            "songs": songs,
        },
    )


def createSong(request):
    context = {
        "zanrai": Daina.Zanras.choices,
        "form_data": {"is_public": "on"},
        "field_errors": {},
    }

    if request.method == "POST":
        errors = []
        field_errors = {}

        name = request.POST.get("name", "").strip()
        minutes = request.POST.get("time", "").strip()
        release_date_raw = request.POST.get("release_date", "").strip()
        genre = request.POST.get("genre", "").strip() or Daina.Zanras.POPMUZIKA
        file_url = request.POST.get("file_url", "").strip()
        cover_url = request.POST.get("cover_url", "").strip()
        description = request.POST.get("description", "").strip()
        is_public = request.POST.get("is_public") == "on"
        uploaded_words = request.FILES.get("words")

        context["form_data"] = {
            "name": name,
            "time": minutes,
            "release_date": release_date_raw,
            "genre": genre,
            "file_url": file_url,
            "cover_url": cover_url,
            "description": description,
            "is_public": "on" if is_public else "",
        }

        if not name:
            errors.append("Song name is required.")
            field_errors["name"] = "Song name is required."

        duration_seconds = None
        if minutes:
            try:
                duration_seconds = int(float(minutes) * 60)
            except (TypeError, ValueError):
                errors.append("Duration must be a number (minutes).")
                field_errors["time"] = "Duration must be a number (minutes)."
        else:
            errors.append("Duration is required.")
            field_errors["time"] = "Duration is required."

        release_date = None
        if release_date_raw:
            try:
                release_date = datetime.strptime(release_date_raw, "%Y-%m-%d").date()
            except (TypeError, ValueError):
                errors.append("Release date is invalid.")
                field_errors["release_date"] = "Release date is invalid."
        else:
            field_errors["release_date"] = "Release date is required."

        valid_genres = {choice[0] for choice in Daina.Zanras.choices}
        if genre not in valid_genres:
            errors.append("Selected genre is not supported.")
            field_errors["genre"] = "Selected genre is not supported."

        words_text = ""
        if uploaded_words:
            raw_text = uploaded_words.read()
            try:
                words_text = raw_text.decode("utf-8")
            except UnicodeDecodeError:
                words_text = raw_text.decode("latin-1", errors="ignore")

        user = User.objects.get(pk = request.session["user_id"])

        if not errors:
            Daina.objects.create(
                savininkas=user,
                pavadinimas=name,
                trukme_sekundes=duration_seconds or 0,
                zanras=genre if genre in valid_genres else Daina.Zanras.POPMUZIKA,
                isleidimo_data=release_date,
                paleidimu_kiekis=0,
                zodziai=words_text,
                failas_url=file_url,
                virselis_url=cover_url,
                aprasymas=description,
                yra_viesa=is_public,
            )
            context["success_message"] = f'"{name}" was created successfully.'
            context["form_data"] = {"is_public": "on"}
            context["field_errors"] = {}
        else:
            # Ensure a top-level message is shown even if only field-level errors exist.
            if not errors and field_errors:
                errors.append("Cannot create song. Please fix the highlighted fields.")
            context["errors"] = errors
            context["field_errors"] = field_errors

    return render(request, "music/createSong.html", context)


def rateSong(request):
    songs = Daina.objects.all().order_by("pavadinimas")
    selected_song_id = request.GET.get("song") or request.POST.get("song")
    selected_song = None
    if selected_song_id:
        try:
            selected_song = Daina.objects.get(pk=int(selected_song_id))
        except (Daina.DoesNotExist, ValueError, TypeError):
            selected_song = None

    context = {
        "songs": songs,
        "selected_song": selected_song,
    }

    if request.method == "POST":
        errors = []
        rating_raw = request.POST.get("rating", "").strip()

        if not selected_song:
            errors.append("Song not found.")

        rating_value = None
        if rating_raw:
            try:
                rating_value = float(rating_raw)
            except (TypeError, ValueError):
                errors.append("Rating must be a number between 1 and 5.")
        else:
            errors.append("Rating is required.")

        if rating_value is not None and not (1 <= rating_value <= 5):
            errors.append("Rating must be between 1 and 5.")

        if not errors and selected_song:
            DainosVertinimas.objects.create(
                daina=selected_song,
                ivertinimas=rating_value,
            )
            context["success_message"] = f'Rating saved for "{selected_song.pavadinimas}".'
        else:
            context["errors"] = errors
            context["rating_value"] = rating_raw

    return render(request, "music/rateSong.html", context)


def editSong(request):
    song_id = request.GET.get("song") or request.POST.get("song")
    song = None
    if song_id:
        try:
            song = get_object_or_404(Daina, pk=int(song_id))
        except (TypeError, ValueError):
            song = None

    if not song:
        return render(
            request,
            "music/editSong.html",
            {
                "errors": ["Song not found."],
                "zanrai": Daina.Zanras.choices,
            },
        )

    context = {
        "song": song,
        "zanrai": Daina.Zanras.choices,
        "form_data": {
            "name": song.pavadinimas,
            "time": round((song.trukme_sekundes or 0) / 60, 2),
            "release_date": song.isleidimo_data.strftime("%Y-%m-%d") if song.isleidimo_data else "",
            "genre": song.zanras,
            "file_url": song.failas_url,
            "cover_url": song.virselis_url,
            "description": song.aprasymas,
            "is_public": "on" if song.yra_viesa else "",
        },
        "field_errors": {},
    }

    if request.method == "POST":
        errors = []
        field_errors = {}

        name = request.POST.get("name", "").strip()
        minutes = request.POST.get("time", "").strip()
        release_date_raw = request.POST.get("release_date", "").strip()
        genre = request.POST.get("genre", "").strip() or Daina.Zanras.POPMUZIKA
        file_url = request.POST.get("file_url", "").strip()
        cover_url = request.POST.get("cover_url", "").strip()
        description = request.POST.get("description", "").strip()
        is_public = request.POST.get("is_public") == "on"
        uploaded_words = request.FILES.get("words")

        context["form_data"] = {
            "name": name,
            "time": minutes,
            "release_date": release_date_raw,
            "genre": genre,
            "file_url": file_url,
            "cover_url": cover_url,
            "description": description,
            "is_public": "on" if is_public else "",
        }

        if not name:
            errors.append("Song name is required.")
            field_errors["name"] = "Song name is required."

        duration_seconds = None
        if minutes:
            try:
                duration_seconds = int(float(minutes) * 60)
            except (TypeError, ValueError):
                errors.append("Duration must be a number (minutes).")
                field_errors["time"] = "Duration must be a number (minutes)."
        else:
            errors.append("Duration is required.")
            field_errors["time"] = "Duration is required."

        release_date = None
        if release_date_raw:
            try:
                release_date = datetime.strptime(release_date_raw, "%Y-%m-%d").date()
            except (TypeError, ValueError):
                errors.append("Release date is invalid.")
                field_errors["release_date"] = "Release date is invalid."
        else:
            field_errors["release_date"] = "Release date is required."

        valid_genres = {choice[0] for choice in Daina.Zanras.choices}
        if genre not in valid_genres:
            errors.append("Selected genre is not supported.")
            field_errors["genre"] = "Selected genre is not supported."

        if not errors:
            song.pavadinimas = name
            song.trukme_sekundes = duration_seconds or 0
            song.zanras = genre if genre in valid_genres else Daina.Zanras.POPMUZIKA
            song.isleidimo_data = release_date
            song.failas_url = file_url
            song.virselis_url = cover_url
            song.aprasymas = description
            song.yra_viesa = is_public

            if uploaded_words:
                raw_text = uploaded_words.read()
                try:
                    song.zodziai = raw_text.decode("utf-8")
                except UnicodeDecodeError:
                    song.zodziai = raw_text.decode("latin-1", errors="ignore")

            song.save()
            context["success_message"] = f'"{name}" was updated successfully.'
            context["field_errors"] = {}
        else:
            if not errors and field_errors:
                errors.append("Cannot update song. Please fix the highlighted fields.")
            context["errors"] = errors
            context["field_errors"] = field_errors

    return render(request, "music/editSong.html", context)


def playSong(request, song_id):
    # song_id = request.GET.get("song")
    song = None
    if song_id:
        try:
            song = get_object_or_404(Daina, pk=int(song_id))
        except (TypeError, ValueError):
            song = None

    context = {
        "song": song,
        "errors": []
    }

    if not song:
        context["errors"] += "Song not found or missing."
        return render(request, "music/playSong.html", context, status=404)

    if not song.failas_url:
        context["errors"] += "This song has no file URL to play."
        return render(request, "music/playSong.html", context, status=400)

    # If streaming is requested, attempt to serve the local file directly.
    if request.GET.get("stream") == "1":
        file_path = song.failas_url
        if file_path.startswith("file://"):
            file_path = file_path[7:]
        file_path = file_path.replace("file:\\", "").replace("file:/", "")

        if not os.path.isabs(file_path):
            # fallback: treat as absolute as provided
            file_path = file_path

        if not os.path.exists(file_path):
            return HttpResponse("Audio file not found on disk.", status=404)

        ctype, _ = mimetypes.guess_type(file_path)
        try:
            return FileResponse(open(file_path, "rb"), content_type=ctype or "audio/mpeg")
        except OSError:
            return HttpResponse("Unable to read audio file from disk.", status=500)

    audio_url = song.failas_url
    audio_mime = None
    ext = audio_url.split(".")[-1].lower() if "." in audio_url else ""
    if ext in {"mp3"}:
        audio_mime = "audio/mpeg"
    elif ext in {"wav"}:
        audio_mime = "audio/wav"
    elif ext in {"ogg", "oga"}:
        audio_mime = "audio/ogg"

    # Use local streaming endpoint when the stored value is not an http(s) URL.
    if not audio_url.lower().startswith(("http://", "https://")):
        audio_url = f"{request.build_absolute_uri(request.path)}?song={song.pk}&stream=1"

    rating_stats = (
        song.vertinimai.aggregate(avg=Avg("ivertinimas"), count=Count("id")) # type: ignore
        if hasattr(song, "vertinimai")
        else {"avg": None, "count": 0}
    )
    context["rating_avg"] = rating_stats.get("avg")
    context["rating_count"] = rating_stats.get("count", 0)

    context["audio_url"] = audio_url
    context["audio_mime"] = audio_mime

    user_id = request.session.get("user_id")
    user_playlists = Grojarastis.objects.filter(savininkas=user_id)
    context["user_playlists"] = user_playlists

    return render(request, "music/playSong.html", context)


def similarSongs(request):
    songs = list(Daina.objects.all())
    if not songs:
        return render(
            request,
            "music/similarSongs.html",
            {"errors": ["No songs available to compare."]},
        )

    song_id = request.GET.get("song")
    target_song = None
    if song_id:
        try:
            target_song = Daina.objects.get(pk=int(song_id))
        except (Daina.DoesNotExist, ValueError, TypeError):
            target_song = None
    if not target_song:
        target_song = songs[0]

    if len(songs) == 1:
        return render(
            request,
            "music/similarSongs.html",
            {
                "target_song": target_song,
                "similar_songs": [],
                "all_songs": songs,
                "info": "Add more songs to see recommendations.",
            },
        )

    genre_values = [g[0] for g in Daina.Zanras.choices]
    genre_index = {g.value: i for i, g in enumerate(genre_values)}

    def build_vector(song: Daina):
        duration_min = (song.trukme_sekundes or 0) / 60.0
        year = song.isleidimo_data.year if song.isleidimo_data else 0
        plays = song.paleidimu_kiekis or 0
        is_public = 1.0 if song.yra_viesa else 0.0
        genre_vec = [0.0] * len(genre_values)
        if song.zanras in genre_index:
            genre_vec[genre_index[song.zanras]] = 1.0
        return [duration_min, year, plays, is_public, *genre_vec]

    def distance(a, b):
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    target_vec = build_vector(target_song)
    scored = []
    for s in songs:
        if s.pk == target_song.pk:
            continue
        vec = build_vector(s)
        scored.append((distance(target_vec, vec), s))

    scored.sort(key=lambda x: x[0])
    similar = [s for _, s in scored[:3]]

    return render(
        request,
        "music/similarSongs.html",
        {
            "target_song": target_song,
            "similar_songs": similar,
            "all_songs": songs,
        },
    )


def addToPlaylist(request, song_id):
    user_id = request.session.get("user_id")
    song = get_object_or_404(Daina, pk=song_id)

    if request.method != "POST":
        return redirect(f"/music/play/{song_id}")

    playlist_id = request.POST.get("playlist_id")
    grojarastis = get_object_or_404(Grojarastis, pk=playlist_id)

    if grojarastis.savininkas.pk != user_id:
        return redirect(f"/music/play/{song_id}")

    if GrojarastisDaina.objects.filter(
        grojarastis=grojarastis,
        daina=song
    ).exists():
        return redirect(f"/music/play/{song_id}")

    last_pos = (
        GrojarastisDaina.objects
        .filter(grojarastis=grojarastis)
        .aggregate(max_nr=Max("eiles_nr"))["max_nr"] or 0
    )

    GrojarastisDaina.objects.create(
        grojarastis=grojarastis,
        daina=song,
        eiles_nr=last_pos + 1,
        prideta_data=timezone.now()
    )

    return redirect(f"/music/play/{song_id}")

def updateListeningHistory(request: HttpRequest):
    if "user" in request.session and request.method == "POST":
        info = json.loads(request.body)
        listening_id = info['listening_id']
        song_id = info['song_id']
        percent = info['percent']

        if song_id != "" and percent != "":
            percent = float(percent)
            klausymas: DainosKlausymas
            if listening_id != "":
                # Jau žinomas klausymas tai atnaujinam
                klausymas = DainosKlausymas.objects.get(pk=listening_id)
                if klausymas.trukme_procentais < percent:
                    klausymas.trukme_procentais = percent
                    klausymas.save()
            else:
                song = Daina.objects.get(pk=song_id)
                user = User.objects.get(pk=request.session["user_id"])
                klausymas = DainosKlausymas.objects.create(
                    daina=song, 
                    naudotojas=user,
                    trukme_procentais=percent
                )
                # Naujas klausymas tai sukuriam

            return HttpResponse(klausymas.pk, content_type="text/plain", status=200)

    return HttpResponse(f"Dont know what to do.", content_type="text/plain", status=422)
