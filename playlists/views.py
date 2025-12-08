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



@login_required
def editPlaylist(request, pk):
    grojarastis = get_object_or_404(Grojarastis, pk=pk)

    if grojarastis.savininkas.pk != request.session.get("user_id"):
        messages.error(request, "Galima redaguoti tik savo grojarastį.")
        return redirect("playlists:index")

    if request.method == "POST":
        grojarastis.pavadinimas = request.POST.get("pavadinimas", grojarastis.pavadinimas)
        grojarastis.aprasymas = request.POST.get("aprasymas", grojarastis.aprasymas)
        grojarastis.yra_viesas = request.POST.get("yra_viesas") == "on"
        grojarastis.save()

        messages.success(request, "Grojarastis atnaujintas!")
        return redirect("playlists:PlaylistDetail", pk=grojarastis.pk)

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
