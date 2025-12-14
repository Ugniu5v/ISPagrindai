'use strict';
{
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
            btn.addEventListener("click", () => {
                const player = document.getElementById("music-player");
                const audio = document.getElementById("music-player-control");
                console.log("audio = ", audio.src, ", button = ", btn.dataset.audio)
                if (audio.src === btn.dataset.audio) {
                    if (player.matches(":popover-open")) {
                        if(audio.paused){
                            audio.play()
                        }else{
                            audio.pause();
                        }

                        // player.hidePopover();
                        return;
                    }
                }
                // Atnaujinam info
                audio.src = btn.dataset.audio;
                coverImg.src = btn.dataset.cover || "https://picsum.photos/60"; 
                titleEl.textContent = btn.dataset.title || "Nežinomas pavadinimas";
                artistEl.textContent = btn.dataset.artist || "Nežinomas atlikėjas"; 

                // Paleisti audio
                audio.play().catch(err => console.error("Nepavyko paleisti audio:", err));
            });
        });
    });
}
