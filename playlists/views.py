from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import models, transaction
from users.decorators import login_required
from .models import Grojarastis, GrojarascioVertinimas, GrojarastisDaina
from music.models import Daina, DainosKlausymas
from django.http import FileResponse, HttpResponse
from django.db.models import Avg, Count, Q
import mimetypes, os
import random
from collections import Counter

def index(request):
    user_id = request.session.get("user_id")

    grojarasciai = (
        Grojarastis.objects.filter(yra_viesas=True)
        | Grojarastis.objects.filter(savininkas_id=user_id)
    ).distinct().order_by('-sukurimo_data')

    for g in grojarasciai:
        g.avg_rating = g.vertinimai.aggregate(models.Avg("ivertinimas"))["ivertinimas__avg"]
        g.ratings_count = g.vertinimai.count()

    return render(request, "playlists/index.html", {
        "grojarasciai": grojarasciai
    })

@login_required
def createPlaylist(request):
    context = {}
    if request.method == "POST":
        pavadinimas = request.POST.get("pavadinimas", "").strip()
        aprasymas = request.POST.get("aprasymas", "").strip()
        yra_viesas = request.POST.get("yra_viesas", "on")
        errors = []
        if not pavadinimas:
            errors.append("Grojaraščio pavadinimas yra privalomas.")
        if errors:
            context.update({
                "errors": errors,
                "pavadinimas": pavadinimas,
                "aprasymas": aprasymas,
                "yra_viesas": yra_viesas,
            })
        else:
            Grojarastis.objects.create(
                pavadinimas=pavadinimas,
                aprasymas=aprasymas,
                yra_viesas=(yra_viesas == "on"),
                savininkas_id=request.session["user_id"],
            )
            messages.success(request, "Grojaraštis sėkmingai sukurtas!")
            return redirect("playlists:index")
    return render(request, "playlists/createPlaylist.html", context)


def PlaylistDetail(request, pk):
    grojarastis = get_object_or_404(Grojarastis, pk=pk)
    user_id = request.session.get("user_id")
    request.session.pop("playlist_shuffle", None)

    is_owner = grojarastis.savininkas_id == user_id
    is_logged_in = user_id is not None

    if not grojarastis.yra_viesas and not is_owner:
        messages.error(request, "Neturite teisės žiūrėti grojaraštį")
        return redirect("playlists:index")

    vertinimai = grojarastis.vertinimai.all()
    avg_rating = vertinimai.aggregate(
        avg=models.Avg("ivertinimas")
    )["avg"]
    ratings_count = vertinimai.count()

    existing_rating = None
    if is_logged_in:
        existing_rating = vertinimai.filter(
            naudotojas_id=user_id
        ).first()

    if request.method == "POST":
        if not is_logged_in:
            messages.error(request, "Prisijunkite norint įvertint.")
            return redirect("playlists:PlaylistDetail", pk=pk)

        if is_owner:
            messages.error(request, "Negalite vertinti savo grojaraščio.")
            return redirect("playlists:PlaylistDetail", pk=pk)

        try:
            rating = int(request.POST.get("rating"))
            if not (1 <= rating <= 5):
                raise ValueError
        except (TypeError, ValueError):
            messages.error(request, "Reitingas galimas tik tarp 1 ir 5.")
            return redirect("playlists:PlaylistDetail", pk=pk)

        if existing_rating:
            existing_rating.ivertinimas = rating
            existing_rating.save()
        else:
            GrojarascioVertinimas.objects.create(
                grojarastis=grojarastis,
                naudotojas_id=user_id,
                ivertinimas=rating,
            )

        messages.success(request, "Reitingas išsaugotas.")
        return redirect("playlists:PlaylistDetail", pk=pk)

    return render(request, "playlists/playlistDetail.html", {
        "grojarastis": grojarastis,
        "avg_rating": avg_rating,
        "ratings_count": ratings_count,
        "existing_rating": existing_rating,
        "is_owner": is_owner,
        "is_logged_in": is_logged_in,
    })

@login_required
def editPlaylist(request, pk):
    grojarastis = get_object_or_404(Grojarastis, pk=pk)

    if grojarastis.savininkas_id != request.session.get("user_id"):
        messages.error(request, "Redaguoti galite tik savo grojaraščius")
        return redirect("playlists:PlaylistDetail", pk=pk)

    if request.method == "POST":
        grojarastis.pavadinimas = request.POST.get("pavadinimas", "").strip()
        grojarastis.aprasymas = request.POST.get("aprasymas", "").strip()
        grojarastis.yra_viesas = request.POST.get("yra_viesas") == "on"
        grojarastis.save()

        sorted_order = request.POST.get("sorted_order", "")
        if sorted_order:
            ids = [int(x) for x in sorted_order.split(",")]

            with transaction.atomic():
                offset = len(ids) + 10

                for i, song_id in enumerate(ids):
                    GrojarastisDaina.objects.filter(
                        id=song_id,
                        grojarastis=grojarastis
                    ).update(eiles_nr=i + offset)

                for i, song_id in enumerate(ids):
                    GrojarastisDaina.objects.filter(
                        id=song_id,
                        grojarastis=grojarastis
                    ).update(eiles_nr=i + 1)

        messages.success(request, "Sėkmingai atnaujintas grojarštis")
        return redirect("playlists:PlaylistDetail", pk=pk)

    return render(
        request,
        "playlists/editPlaylist.html",
        {"grojarastis": grojarastis}
    )

@login_required
def deletePlaylist(request, pk):
    grojarastis = get_object_or_404(Grojarastis, pk=pk)

    if grojarastis.savininkas_id != request.session.get("user_id"):
        messages.error(request, "Naikinti galite tik savo grojarštį")
        return redirect("playlists:index")

    grojarastis.delete()
    messages.success(request, "Sėkmingai sunaikintas grojaštis")
    return redirect("playlists:index")

@login_required
def deleteFromPlaylist(request, grojarastis_id, song_id):
    user_id = request.session.get("user_id")

    grojarastis = get_object_or_404(Grojarastis, pk=grojarastis_id)
    item = get_object_or_404(GrojarastisDaina, pk=song_id, grojarastis=grojarastis)

    if grojarastis.savininkas_id != user_id:
        messages.error(request, "Dainas naikinri galite tik savo grojaštyje")
        return redirect("playlists:PlaylistDetail", pk=grojarastis_id)

    item.delete()

    remaining = grojarastis.dainos.order_by("eiles_nr")
    for i, d in enumerate(remaining, start=1):
        if d.eiles_nr != i:
            d.eiles_nr = i
            d.save(update_fields=["eiles_nr"])

    messages.success(request, "Daina panaikinta iš grojaraščio.")
    return redirect("playlists:PlaylistDetail", pk=grojarastis_id)

def playPlaylistSong(request, pk):
    grojarastis = get_object_or_404(Grojarastis, pk=pk)

    shuffle_ids = request.session.get("playlist_shuffle")

    if shuffle_ids:
        entries = list(
            GrojarastisDaina.objects
            .filter(id__in=shuffle_ids, grojarastis=grojarastis)
            .select_related("daina")
        )

        entries.sort(key=lambda e: shuffle_ids.index(e.id))
    else:
        entries = list(
            GrojarastisDaina.objects
            .filter(grojarastis=grojarastis)
            .select_related("daina")
            .order_by("eiles_nr")
        )

    if not entries:
        return render(request, "playlists/playPlaylistSong.html", {
            "grojarastis": grojarastis,
            "errors": ["Playlist is empty."]
        })

    index = int(request.GET.get("i", 0))
    index = max(0, min(index, len(entries) - 1))

    entry = entries[index]
    song = entry.daina

    if request.GET.get("stream") == "1":
        file_path = song.failas_url.replace("file://", "").replace("file:\\", "").replace("file:/", "")
        if not os.path.exists(file_path):
            return HttpResponse("Audio file not found.", status=404)

        ctype, _ = mimetypes.guess_type(file_path)
        return FileResponse(open(file_path, "rb"), content_type=ctype or "audio/mpeg")

    audio_url = song.failas_url
    audio_mime = {
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "ogg": "audio/ogg",
        "oga": "audio/ogg",
    }.get(audio_url.split(".")[-1].lower())

    if not audio_url.startswith(("http://", "https://")):
        audio_url = f"{request.build_absolute_uri(request.path)}?i={index}&stream=1"

    rating = song.vertinimai.aggregate(
        avg=Avg("ivertinimas"),
        count=Count("id")
    )

    return render(request, "playlists/playPlaylistSong.html", {
        "grojarastis": grojarastis,
        "song": song,
        "audio_url": audio_url,
        "audio_mime": audio_mime,
        "index": index,
        "entries": entries,
        "rating_avg": rating["avg"],
        "rating_count": rating["count"],
        "has_prev": index > 0,
        "has_next": index < len(entries) - 1,
    })


def playPlaylistShuffle(request, pk):
    user_id = request.session.get("user_id")
    grojarastis = get_object_or_404(Grojarastis, pk=pk)

    entries = list(
        GrojarastisDaina.objects
        .filter(grojarastis=grojarastis)
        .select_related("daina")
    )

    if not entries:
        return redirect("playlists:PlaylistDetail", pk=pk)

    recent_listens = (
        DainosKlausymas.objects
        .filter(
            naudotojas_id=user_id,
            trukme_procentais__gte=10
        )
        .order_by("-klausymo_data")
        .select_related("daina")[:10]
    )

    genre_counter = Counter(
        l.daina.zanras for l in recent_listens if l.daina
    )

    preferred_genres = [g for g, _ in genre_counter.most_common()]

    by_genre = {}
    for e in entries:
        by_genre.setdefault(e.daina.zanras, []).append(e)

    final_order = []

    for genre in preferred_genres:
        if genre in by_genre:
            songs = by_genre.pop(genre)
            random.shuffle(songs)
            final_order.extend(songs)

    remaining_genres = list(by_genre.keys())
    random.shuffle(remaining_genres)

    for genre in remaining_genres:
        songs = by_genre[genre]
        random.shuffle(songs)
        final_order.extend(songs)

    request.session["playlist_shuffle"] = [e.id for e in final_order]

    return redirect("playlists:playPlaylistSong", pk=pk)
