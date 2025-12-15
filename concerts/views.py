from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpRequest
from django.db.models import Q
from datetime import datetime
from datetime import timedelta
from .models import Koncertas, Vieta, KoncertoDalyvis
from users.models import User
from users.decorators import login_required
import requests
from pprint import pprint


def index(request):
    koncertai = Koncertas.objects.filter(yra_viesas=True, yra_atsauktas=False)
    
    search_query = request.GET.get('q', '').strip()
    if search_query:
        koncertai = koncertai.filter(
            Q(pavadinimas__icontains=search_query) |
            Q(aprasymas__icontains=search_query) |
            Q(zanras__icontains=search_query) |
            Q(vieta__pavadinimas__icontains=search_query) |
            Q(vieta__miestas__icontains=search_query) |
            Q(vieta__salis__icontains=search_query)
        )
    
    genre_filter = request.GET.get('genre', '')
    if genre_filter:
        koncertai = koncertai.filter(zanras=genre_filter)
    
    status_filter = request.GET.get('status', '')
    if status_filter == 'private':
        koncertai = koncertai.filter(yra_viesas=False)
    elif status_filter == 'public':
        koncertai = koncertai.filter(yra_viesas=True)
    elif status_filter == 'cancelled':
        koncertai = Koncertas.objects.filter(yra_atsauktas=True)
    
    date_filter = request.GET.get('date', '')
    today = timezone.now().date()
    
    if date_filter == 'today':
        koncertai = koncertai.filter(pradzios_data=today)
    elif date_filter == 'week':
        week_end = today + timedelta(days=7)
        koncertai = koncertai.filter(pradzios_data__gte=today, pradzios_data__lte=week_end)
    elif date_filter == 'month':
        month_end = today + timedelta(days=30)
        koncertai = koncertai.filter(pradzios_data__gte=today, pradzios_data__lte=month_end)
    elif date_filter == 'upcoming':
        koncertai = koncertai.filter(pradzios_data__gte=today)
    elif date_filter == 'past':
        koncertai = koncertai.filter(pradzios_data__lt=today)
    
    koncertai = koncertai.order_by("-pradzios_data")
    zanrai = Koncertas.Zanras.choices
    
    user = None
    if "user" in request.session:
        try:
            user = User.objects.get(pk=request.session["user_id"])
        except User.DoesNotExist:
            pass
    
    return render(request, "concerts/index.html", {
        "koncertai": koncertai,
        "zanrai": zanrai,
        "search_query": search_query,
        "selected_genre": genre_filter,
        "selected_status": status_filter,
        "selected_date": date_filter,
        "user": user,
    })

@login_required
def createConcert(request: HttpRequest):
    if request.method == "POST":
        user = None
        try:
            user = User.objects.get(pk=request.session["user_id"])
        except User.DoesNotExist:
            redirect("concerts:index")

        vieta_id = request.POST.get("vieta", "").strip()
        vieta = None
        if vieta_id:
            try:
                vieta = Vieta.objects.get(pk=int(vieta_id))
            except (ValueError, Vieta.DoesNotExist):
                pass
        
        pradzios_data = None
        if request.POST.get("pradzios_data"):
            try:
                pradzios_data = datetime.strptime(request.POST["pradzios_data"], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                pass
        
        pabaigos_data = None
        if request.POST.get("pabaigos_data"):
            try:
                pabaigos_data = datetime.strptime(request.POST["pabaigos_data"], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                pass
                         
        koncertas = Koncertas.objects.create(
            autorius=user,
            pavadinimas=request.POST["pavadinimas"],
            pradzios_data=pradzios_data,
            pabaigos_data=pabaigos_data,
            zanras=request.POST["zanras"],
            bilietu_url=request.POST.get("bilietu_url", ""),
            aprasymas=request.POST.get("aprasymas", ""),
            sukurimo_data=timezone.now().date(),
            atnaujinimo_data=timezone.now().date(),
            yra_atsauktas=False,
            zmoniu_talpa=int(request.POST["zmoniu_talpa"]),
            yra_viesas=request.POST.get("yra_viesas") == "on",
            vieta=vieta
        )
        return redirect('concerts:concertDetail', pk=koncertas.pk)

    zanrai = Koncertas.Zanras.choices
    vietos = Vieta.objects.all()
    return render(request, "concerts/createConcert.html",{
        "zanrai": zanrai,
        "vietos": vietos  
    })

# veliau nuimti 
#@login_required
def editConcert(request, pk):
    koncertas = get_object_or_404(Koncertas, pk=pk)

    if "vieta_prideti" in request.POST:
        pavadinimas = request.POST["vieta_pavadinimas"]
        adresas = request.POST["vieta_adresas"]
        miestas = request.POST["vieta_miestas"]
        salis = request.POST["vieta_salis"]
        platuma = request.POST["vieta_platuma"]
        ilguma = request.POST["vieta_ilguma"]
        laiko_zona = request.POST["vieta_laiko_zona"]

        Vieta.objects.create(
            pavadinimas = pavadinimas,
            adresas = adresas,
            miestas = miestas,
            salis = salis,
            platuma = platuma,
            ilguma = ilguma,
            laiko_zona = laiko_zona
        )
    elif request.method == "POST":
        vieta_id = request.POST.get("vieta", "").strip()
        vieta = None
        if vieta_id:
            try:
                vieta = Vieta.objects.get(pk=int(vieta_id))
            except (ValueError, Vieta.DoesNotExist):
                pass
        
        if request.POST.get("pradzios_data"):
            try:
                koncertas.pradzios_data = datetime.strptime(request.POST["pradzios_data"], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                pass
        
        if request.POST.get("pabaigos_data"):
            try:
                koncertas.pabaigos_data = datetime.strptime(request.POST["pabaigos_data"], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                pass
        
        koncertas.pavadinimas = request.POST["pavadinimas"]
        koncertas.zanras = request.POST["zanras"]
        koncertas.bilietu_url = request.POST.get("bilietu_url", "")
        koncertas.aprasymas = request.POST.get("aprasymas", "")
        koncertas.atnaujinimo_data = timezone.now().date()
        koncertas.yra_atsauktas = request.POST.get("yra_atsauktas") == "on"
        koncertas.zmoniu_talpa = int(request.POST["zmoniu_talpa"])
        koncertas.yra_viesas = request.POST.get("yra_viesas") == "on"
        koncertas.vieta = vieta
        koncertas.save()
        return redirect('concerts:concertDetail', pk=koncertas.pk)

    vietos = Vieta.objects.all()
    zanrai = Koncertas.Zanras.choices
    return render(request, "concerts/editConcert.html", {
        "koncertas": koncertas,
        "vietos": vietos,
        "zanrai": zanrai
    })


def searchConcert(request):
    query = request.GET.get('q', '')
    zanras = request.GET.get('zanras', '')
    
    koncertai = Koncertas.objects.filter(yra_viesas=True)
    
    if query:
        koncertai = koncertai.filter(pavadinimas__icontains=query)
    
    if zanras:
        koncertai = koncertai.filter(zanras=zanras)
    
    zanrai = Koncertas.Zanras.choices
    return render(request, "concerts/searchConcert.html", {
        'koncertai': koncertai,
        'zanrai': zanrai,
        'query': query
    })


def concertDetail(request, pk):
    koncertas = get_object_or_404(Koncertas, pk=pk)
    concert_location = None
    if koncertas.vieta:
        concert_location = {
            'lat': koncertas.vieta.platuma,
            'lng': koncertas.vieta.ilguma,
            'name': koncertas.vieta.pavadinimas 
        }
    
    dalyvavimo_busena = None
    user = None
    if "user" in request.session:
        try:
            user = User.objects.get(pk=request.session["user_id"])
            dalyvis = KoncertoDalyvis.objects.get(vartotojas=user.pk, koncertas=koncertas)
            dalyvavimo_busena = dalyvis.dalyvavimo_busena
        except (KoncertoDalyvis.DoesNotExist, User.DoesNotExist):
            pass
    
    return render(request, "concerts/concertDetail.html", {
        'koncertas': koncertas,
        'location': concert_location,
        'dalyvavimo_busena': dalyvavimo_busena,
        'user': user,
    })


def recommendationConcert(request):
    koncertai = Koncertas.objects.filter(yra_viesas=True).order_by("-pradzios_data")[:10]
    zanrai = Koncertas.Zanras.choices
    return render(request, "concerts/recommendationConcert.html", {
        "koncertai": koncertai,
        "zanrai": zanrai
    })
