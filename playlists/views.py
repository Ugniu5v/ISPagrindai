from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import models
from users.decorators import login_required
from .models import Grojarastis, GrojarascioVertinimas, GrojarastisDaina


def index(request):
    user_id = request.session.get("user_id")

    grojarasciai = Grojarastis.objects.filter(yra_viesas=True)

    for g in grojarasciai:
        g.avg_rating = g.vertinimai.aggregate(models.Avg("ivertinimas"))["ivertinimas__avg"]
        g.ratings_count = g.vertinimai.count()

    return render(request, "playlists/index.html", {
        "request": request,
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
                savininkas=request.session["user_id"]
            )

            messages.success(request, "Playlist created successfully!")
            return redirect("playlists:index")

    return render(request, "playlists/createPlaylist.html")
    

def playlistDetail(request, pk):
    user_id = request.session.get("user_id")
    grojarastis = get_object_or_404(Grojarastis, pk=pk)
    is_owner = grojarastis.savininkas.pk == user_id
    
    if "user" not in request.session or not grojarastis.yra_viesas and not is_owner:
        messages.error(request, "You do not have permission to view this playlist.")
        return redirect("playlists:index")


    vertinimai = grojarastis.vertinimai.all() # type: ignore
    avg_rating = vertinimai.aggregate(models.Avg("ivertinimas"))["ivertinimas__avg"]

    existing_rating = grojarastis.vertinimai.filter(naudotojas_id=user_id).first() # type: ignore

    if request.method == "POST":
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

    # Permission check
    if grojarastis.savininkas_id != request.session.get("user_id"):
        messages.error(request, "You may only edit your own playlist.")
        return redirect("playlists:PlaylistDetail", pk=pk)

    if request.method == "POST":

        # Update general playlist fields
        grojarastis.pavadinimas = request.POST.get("pavadinimas", grojarastis.pavadinimas)
        grojarastis.aprasymas = request.POST.get("aprasymas", grojarastis.aprasymas)
        grojarastis.yra_viesas = request.POST.get("yra_viesas") == "on"
        grojarastis.save()

        # --- DRAG & DROP ORDER FIX ---
        sorted_ids = request.POST.get("sorted_order", "")
        if sorted_ids:
            id_list = [int(x) for x in sorted_ids.split(",")]

            songs = list(grojarastis.dainos.all())
            count = len(songs)

            # STEP 1 – TEMPORARILY MOVE ALL SONGS OUT OF THE WAY
            temp_offset = count + 10  # safe padding
            for song in songs:
                song.eilės_nr = song.eilės_nr + temp_offset
                song.save(update_fields=["eilės_nr"])

            # STEP 2 – ASSIGN CLEAN ORDER 1..N
            position = 1
            for song_id in id_list:
                try:
                    entry = GrojarastisDaina.objects.get(id=song_id, grojarastis=grojarastis)
                    entry.eilės_nr = position
                    entry.save(update_fields=["eilės_nr"])
                    position += 1
                except GrojarastisDaina.DoesNotExist:
                    pass

        messages.success(request, "Playlist updated.")
        return redirect("playlists:PlaylistDetail", pk=pk)

    return render(request, "playlists/editPlaylist.html", {"grojarastis": grojarastis})


@login_required
def deletePlaylist(request, pk):
    grojarastis = get_object_or_404(Grojarastis, pk=pk)

    if grojarastis.savininkas.pk != request.session.get("user_id"):
        messages.error(request, "You can only delete your own playlist.")
        return redirect("playlists:index")

    grojarastis.delete()
    messages.success(request, "Playlist deleted successfully!")
    return redirect("playlists:index")

def deleteFromPlaylist(request, grojarastis_id, song_id):
    user_id = request.session.get("user_id")

    grojarastis = get_object_or_404(Grojarastis, pk=grojarastis_id)
    item = get_object_or_404(GrojarastisDaina, pk=song_id, grojarastis=grojarastis)

    if grojarastis.savininkas.pk != user_id:
        messages.error(request, "You can only remove songs from your own playlists.")
        return redirect("playlists:PlaylistDetail", pk=grojarastis_id)

    item.delete()

    remaining = grojarastis.dainos.order_by("eilės_nr") # type: ignore
    for i, d in enumerate(remaining, start=1):
        if d.eilės_nr != i:
            d.eilės_nr = i
            d.save(update_fields=["eilės_nr"])

    messages.success(request, "Song removed from playlist.")
    return redirect("playlists:PlaylistDetail", pk=grojarastis_id)

def playPlaylistSong(request, pk, song_id):
    grojarastis = get_object_or_404(Grojarastis, pk=pk)

    # Get songs in order
    songs = list(grojarastis.dainos.order_by("eilės_nr"))

    # Find the current song entry inside playlist
    try:
        current_entry = GrojarastisDaina.objects.get(pk=song_id, grojarastis=grojarastis)
    except GrojarastisDaina.DoesNotExist:
        return HttpResponse("Song not found in this playlist.", status=404)

    # Try to find matching song in Daina table by name + artist
    try:
        song = Daina.objects.get(
            pavadinimas=current_entry.dainos_pavadinimas,
            atlikejo_vardas=current_entry.atlikėjo_vardas
        )
    except Daina.DoesNotExist:
        song = None

    # Determine previous / next song
    index = songs.index(current_entry)
    prev_id = songs[index - 1].id if index > 0 else None
    next_id = songs[index + 1].id if index < len(songs) - 1 else None

    # AUDIO URL LOGIC FROM YOUR playSong
    audio_url = None
    audio_mime = None

    if song and song.failas_url:
        ext = song.failas_url.split(".")[-1].lower()
        if ext == "mp3":
            audio_mime = "audio/mpeg"
        elif ext == "wav":
            audio_mime = "audio/wav"
        elif ext in {"ogg", "oga"}:
            audio_mime = "audio/ogg"

        if song.failas_url.lower().startswith(("http://", "https://")):
            audio_url = song.failas_url
        else:
            audio_url = f"{request.build_absolute_uri()}?stream=1"

    return render(request, "playlists/playPlaylistSong.html", {
        "playlist": grojarastis,
        "current": current_entry,
        "song": song,
        "songs": songs,
        "prev_id": prev_id,
        "next_id": next_id,
        "audio_url": audio_url,
        "audio_mime": audio_mime,
    })