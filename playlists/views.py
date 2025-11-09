from django.shortcuts import render

MOCK_PLAYLISTS = [
    {
        "id": 1,
        "title": "Chill Vibes",
        "genre": "Lo-Fi",
        "songs": 25,
        "visibility": "Public",
        "description": "Relaxing Lo-Fi beats to chill and study to.",
        "created": "Sep 10, 2024"
    },
    {
        "id": 2,
        "title": "Workout Energy",
        "genre": "EDM",
        "songs": 40,
        "visibility": "Public",
        "description": "High-energy tracks to keep your motivation up during workouts.",
        "created": "Jul 2, 2024"
    },
    {
        "id": 3,
        "title": "Classic Rock Anthems",
        "genre": "Rock",
        "songs": 50,
        "visibility": "Private",
        "description": "Legendary rock tracks from the 70s and 80s.",
        "created": "Oct 1, 2024"
    }
]

# Create your views here.
def index(request):
    return render(request, "playlists/index.html")

def createPlaylist(request):
    return render(request, 'playlists/CreatePlaylist.html')

def searchPlaylist(request):
    query = request.GET.get('query', '').lower()
    if query:
        results = [p for p in MOCK_PLAYLISTS if query in p["title"].lower() or query in p["genre"].lower()]
    else:
        results = []
    return render(request, 'playlists/searchPlaylist.html', {'playlists': results})

def playlistDetail(request, playlist_id):
    # Find the playlist by its id
    playlist = next((p for p in MOCK_PLAYLISTS if p["id"] == playlist_id), None)
    return render(request, 'playlists/playlistDetail.html', {'playlist': playlist})

def editPlaylist(request, playlist_id):
    # Find playlist
    playlist = next((p for p in MOCK_PLAYLISTS if p["id"] == playlist_id), None)
    if not playlist:
        return render(request, 'playlists/editPlaylist.html', {'playlist': None})

    if request.method == 'POST':
        # Update mock data (for now; replace with database save later)
        playlist['title'] = request.POST.get('title', playlist['title'])
        playlist['genre'] = request.POST.get('genre', playlist['genre'])
        playlist['description'] = request.POST.get('description', playlist['description'])
        playlist['songs'] = int(request.POST.get('songs', playlist['songs']))
        playlist['visibility'] = request.POST.get('visibility', playlist['visibility'])
        # Redirect to playlist details page
        return redirect('playlists:playlistDetail', playlist_id=playlist_id)

    return render(request, 'playlists/editPlaylist.html', {'playlist': playlist})