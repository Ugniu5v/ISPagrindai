'use strict';
{
    function getCookie(name) {
	    let cookieValue = null;
	    if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
				}
			}
		}
		return cookieValue;
	}

	const csrftoken = getCookie('csrftoken');

    function updateListeningHistory(listening_id, song_id, percent){
        if(window.user === undefined){
            console.log("No user");
            return;
        }
        const request = new Request("/music/updateHistory/", {
            method: "POST",
            body: `{"listening_id": "${listening_id}", "song_id": "${song_id}", "percent": "${percent}"}`,
            headers: {
				'X-CSRFToken': csrftoken,
				'Content-Type': 'application/json',
			}
        });


        fetch(request)
            .then((response) => {
                if (response.status !== 200) {
                    throw new Error("Kažkas ne taip");
                }
                return response.text();
            })
            .then((listening_id) => {
                document.querySelectorAll(".play-btn").forEach(btn => {
                    const playbutton = btn.children[0];
                    const audio = document.getElementById("music-player-control");
                    if (audio.src === playbutton.dataset.audio) {
                        audio.dataset.listeningId = listening_id;
                    }
                    if (playbutton.dataset.songId === song_id){
                        playbutton.dataset.listeningId = listening_id;
                        return
                    }
                })
            })
            .catch((error) => {
                console.error(error);
            });
    }

    function updateHandler(event){
        const audio = event.target
        const listening_id = audio.dataset.listeningId;
        const song_id = audio.dataset.songId;
        const percent = audio.currentTime * 100 / audio.duration;
        updateListeningHistory(listening_id, song_id, percent);
    }

    window.addEventListener('load', function(_) {
        const player = document.getElementById("music-player");

        // Elementai, kuriuos reikia atnaujinti
        const coverImg = player.querySelector("img");
        const titleEl = player.querySelector("strong");
        const artistEl = player.querySelector("small");

        this.document.querySelectorAll(".song-card").forEach(card => {
            const btn = card.querySelector(".play-btn");
            card.addEventListener("click", () => {
                if (!btn.matches(":hover")){
                    this.location.href = card.dataset.href
                }
            }, false);
        });

        document.querySelectorAll(".play-btn").forEach(btn => {
            btn.addEventListener("pointerup", (e) => {
                const playbutton = e.target;
                const player = document.getElementById("music-player");
                const audio = document.getElementById("music-player-control");
                if (audio.src === playbutton.dataset.audio) {
                    if (player.matches(":popover-open")) {
                        if(audio.paused){
                            audio.play();
                        }else{
                            audio.pause()
                        }
                        return;
                    }
                }
                // Atnaujinam info
                audio.src = playbutton.dataset.audio;
                audio.dataset.songId = playbutton.dataset.songId;
                audio.dataset.listeningId = playbutton.dataset.listeningId || "";
                coverImg.src = playbutton.dataset.cover || "https://picsum.photos/60"; 
                titleEl.textContent = playbutton.dataset.title || "Nežinomas pavadinimas";
                artistEl.textContent = playbutton.dataset.artist || "Nežinomas atlikėjas";

                // Paleisti audio
                audio
                    .play()
                    .then(() => {
                        updateListeningHistory(audio.dataset.listeningId, audio.dataset.songId, 0)
                    })
                    .catch(err => console.error("Nepavyko paleisti audio:", err));
            });
        });

        const audio = document.getElementById("music-player-control");

        audio.onpause = updateHandler;
        audio.onended = updateHandler;
    });
}
