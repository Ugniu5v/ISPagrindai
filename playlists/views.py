from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import models
from users.decorators import login_required
from .models import Grojarastis, GrojarascioVertinimas


@login_required
def index(request):
    user_id = request.session.get("user_id")

    # Show all public playlists + user's own playlists
    grojarasciai = (
        Grojarastis.objects.filter(yra_viesas=True)
        | Grojarastis.objects.filter(savininkas_id=user_id)
    ).distinct().order_by('-sukurimo_data')

    # Add rating data to each playlist
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
    })



@login_required
def editPlaylist(request, pk):
    grojarastis = get_object_or_404(Grojarastis, pk=pk)

    if grojarastis.savininkas_id != request.session.get("user_id"):
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
