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
            return false;
        }
        const request = new Request("/music/updateHistory/", {
            method: "POST",
            body: `{"listening_id": "${listening_id}", "song_id": "${song_id}", "percent": "${percent}"}`,
            headers: {
				'X-CSRFToken': csrftoken,
				'Content-Type': 'application/json',
			}
        });


        return fetch(request)
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Kažkas ne taip");
                }
                return response.text();
            })
    }

    function updateHandler(event){
        const audio = event.target
        if ("songId" in audio.dataset){
            const listening_id = audio.dataset.listeningId || "";
            const song_id = audio.dataset.songId;
            const percent = audio.currentTime * 100 / audio.duration;
            
            Promise.resolve(updateListeningHistory(listening_id, song_id, percent)).then((new_listening_id) => {
                if (new_listening_id !== false){
                    // Atnaujina audio elementą su klausymo id
                    audio.dataset.listeningId = new_listening_id;

                    // Atnaujina grotuvo korteliu id 
                    document.querySelectorAll(".play-btn").forEach(btn => {
                        if (btn.dataset.songId === song_id){
                            btn.dataset.listeningId = listening_id
                            return
                        }
                    })
                }
            })
        }else{
            console.log("No data on audio tag");
        }
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
            btn.addEventListener("click", _ => {
                const playbutton = btn;
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
                // Atnaujinam audio
                audio.src = playbutton.dataset.audio;
                audio.dataset.songId = playbutton.dataset.songId;
                audio.dataset.listeningId = playbutton.dataset.listeningId || "";
                    
                // Atnaujinam kitus duomenis
                coverImg.src = playbutton.dataset.cover || "https://picsum.photos/60"; 
                titleEl.textContent = playbutton.dataset.title || "Nežinomas pavadinimas";
                artistEl.textContent = playbutton.dataset.artist || "Nežinomas atlikėjas";

                // Paleisti audio
                audio.load();
                audio.play();
            });
        });

        this.document.querySelectorAll("audio").forEach(audio => {
            audio.onpause = updateHandler;
            audio.onended = updateHandler;
        });
    });
}
