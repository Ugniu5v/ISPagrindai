from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import models, transaction
from users.decorators import login_required
from .models import Grojarastis, GrojarascioVertinimas, GrojarastisDaina
from music.models import Daina
from django.http import FileResponse, HttpResponse
from django.db.models import Avg, Count
import mimetypes, os

@login_required
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
    if request.method == "POST":
        pavadinimas = request.POST.get("pavadinimas", "").strip()
        aprasymas = request.POST.get("aprasymas", "").strip()
        yra_viesas = request.POST.get("yra_viesas") == "on"

        if pavadinimas:
            Grojarastis.objects.create(
                pavadinimas=pavadinimas,
                aprasymas=aprasymas,
                yra_viesas=yra_viesas,
                savininkas_id=request.session["user_id"]
            )

            messages.success(request, "Playlist created successfully!")
            return redirect("playlists:index")

    return render(request, "playlists/createPlaylist.html")
    

@login_required
def PlaylistDetail(request, pk):
    grojarastis = get_object_or_404(Grojarastis, pk=pk)
    user_id = request.session.get("user_id")
    is_owner = (grojarastis.savininkas_id == request.session.get("user_id"))


    if not grojarastis.yra_viesas and grojarastis.savininkas_id != user_id:
        messages.error(request, "You do not have permission to view this playlist.")
        return redirect("playlists:index")

    vertinimai = grojarastis.vertinimai.all()
    avg_rating = vertinimai.aggregate(models.Avg("ivertinimas"))["ivertinimas__avg"]

    existing_rating = grojarastis.vertinimai.filter(naudotojas_id=user_id).first()

    if request.method == "POST" and grojarastis.savininkas_id != user_id:
        new_rating = float(request.POST.get("rating"))

        if existing_rating:
            existing_rating.ivertinimas = new_rating
            existing_rating.save()
        else:
            GrojarascioVertinimas.objects.create(
                grojarastis=grojarastis,
                naudotojas_id=user_id,
                ivertinimas=new_rating,
            )

        messages.success(request, "Your rating has been saved!")
        return redirect("playlists:PlaylistDetail", pk=pk)

    return render(request, "playlists/playlistDetail.html", {
        "grojarastis": grojarastis,
        "avg_rating": avg_rating,
        "ratings_count": vertinimai.count(),
        "existing_rating": existing_rating,
        "is_owner": is_owner,
    })

def editPlaylist(request, pk):
    grojarastis = get_object_or_404(Grojarastis, pk=pk)

    if grojarastis.savininkas_id != request.session.get("user_id"):
        return redirect("playlists:PlaylistDetail", pk=pk)

    if request.method == "POST":
        grojarastis.pavadinimas = request.POST.get("pavadinimas")
        grojarastis.aprasymas = request.POST.get("aprasymas")
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
        messages.error(request, "You can only delete your own playlist.")
        return redirect("playlists:index")

    grojarastis.delete()
    messages.success(request, "Playlist deleted successfully!")
    return redirect("playlists:index")

def deleteFromPlaylist(request, grojarastis_id, song_id):
    user_id = request.session.get("user_id")

    grojarastis = get_object_or_404(Grojarastis, pk=grojarastis_id)
    item = get_object_or_404(GrojarastisDaina, pk=song_id, grojarastis=grojarastis)

    if grojarastis.savininkas_id != user_id:
        messages.error(request, "You can only remove songs from your own playlists.")
        return redirect("playlists:PlaylistDetail", pk=grojarastis_id)

    item.delete()

    remaining = grojarastis.dainos.order_by("eiles_nr")
    for i, d in enumerate(remaining, start=1):
        if d.eiles_nr != i:
            d.eiles_nr = i
            d.save(update_fields=["eiles_nr"])

    messages.success(request, "Song removed from playlist.")
    return redirect("playlists:PlaylistDetail", pk=grojarastis_id)

def playPlaylistSong(request, pk):
    grojarastis = get_object_or_404(Grojarastis, pk=pk)

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
        file_path = song.failas_url
        if file_path.startswith("file://"):
            file_path = file_path[7:]
        file_path = file_path.replace("file:\\", "").replace("file:/", "")

        if not os.path.exists(file_path):
            return HttpResponse("Audio file not found.", status=404)

        ctype, _ = mimetypes.guess_type(file_path)
        return FileResponse(open(file_path, "rb"), content_type=ctype or "audio/mpeg")

    audio_url = song.failas_url
    audio_mime = None
    ext = audio_url.split(".")[-1].lower()

    if ext == "mp3":
        audio_mime = "audio/mpeg"
    elif ext == "wav":
        audio_mime = "audio/wav"
    elif ext in {"ogg", "oga"}:
        audio_mime = "audio/ogg"

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