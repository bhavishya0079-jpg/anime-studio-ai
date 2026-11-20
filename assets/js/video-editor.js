
// Anime Studio AI - Automatic Video Editor
// Connects uploaded video + generated AI voice + optional background music.

(() => {
    "use strict";

    const API_BASE =
        window.AnimeStudio?.API_BASE_URL ||
        "https://anime-studio-ai.onrender.com";

    let outputUrl = null;

    function initializeEditor() {
        const videoInput = document.getElementById("videoFile");
        const panel = document.getElementById("upload");

        if (!videoInput || !panel) {
            console.error("Video Editor: Required HTML elements not found.");
            return;
        }

        // Prevent duplicate controls.
        if (document.getElementById("renderShortBtn")) return;

        const controls = document.createElement("div");
        controls.id = "automaticEditorControls";
        controls.style.cssText = `
            margin-top:20px;
            padding:16px;
            border:1px solid rgba(255,255,255,.15);
            border-radius:14px;
            background:rgba(255,255,255,.04);
        `;

        controls.innerHTML = `
            <h3>🎬 Automatic Shorts Editor</h3>

            <p style="font-size:13px;opacity:.8">
                Generate your AI voice first, then select your video.
                Background music is optional.
            </p>

            <label for="backgroundMusicFile">
                🎵 Background Music (Optional)
            </label>

            <input
                id="backgroundMusicFile"
                type="file"
                accept=".mp3,.wav,.m4a,.aac,.ogg,audio/*"
                style="display:block;width:100%;margin:10px 0 18px"
            >

            <button
                id="renderShortBtn"
                type="button"
                style="
                    width:100%;
                    padding:14px;
                    border:0;
                    border-radius:10px;
                    cursor:pointer;
                    font-weight:bold;
                "
            >
                ✨ Create My Anime Short
            </button>

            <p
                id="renderStatus"
                role="status"
                aria-live="polite"
                style="margin-top:12px;font-size:14px"
            ></p>

            <div id="renderOutput" style="margin-top:15px"></div>

            <p style="font-size:12px;opacity:.7;margin-top:15px">
                Use only video footage and music that you own or have
                permission to use. Current editor limit: 60 seconds.
            </p>
        `;

        panel.appendChild(controls);

        document
            .getElementById("renderShortBtn")
            .addEventListener("click", renderShort);
    }

    function showStatus(message, isError = false) {
        const status = document.getElementById("renderStatus");
        if (!status) return;

        status.textContent = message;
        status.style.color = isError ? "#ff7777" : "inherit";
    }

    async function getGeneratedVoice() {
        const audio = document.getElementById("voiceAudio");

        if (!audio || !audio.src) {
            throw new Error(
                "પહેલા AI Voice Studio માંથી Hindi voice બનાવો."
            );
        }

        const response = await fetch(audio.src);

        if (!response.ok) {
            throw new Error("AI voice audio મળી શક્યો નથી.");
        }

        const blob = await response.blob();

        if (!blob.size) {
            throw new Error("AI voice audio ખાલી છે.");
        }

        const extension =
            blob.type.includes("wav") ? "wav" :
            blob.type.includes("mpeg") ? "mp3" :
            blob.type.includes("mp4") ? "m4a" : "wav";

        return new File(
            [blob],
            `anime-voice.${extension}`,
            { type: blob.type || "audio/wav" }
        );
    }

    async function renderShort() {
        const button = document.getElementById("renderShortBtn");
        const videoInput = document.getElementById("videoFile");
        const musicInput = document.getElementById("backgroundMusicFile");
        const output = document.getElementById("renderOutput");

        if (!videoInput.files || !videoInput.files[0]) {
            showStatus("પહેલા તમારો video પસંદ કરો.", true);
            return;
        }

        const video = videoInput.files[0];

        if (video.size > 100 * 1024 * 1024) {
            showStatus("Video 100 MB કરતાં નાનો હોવો જોઈએ.", true);
            return;
        }

        button.disabled = true;
        button.textContent = "⏳ Creating Your Short...";
        output.replaceChildren();

        try {
            showStatus("AI voice તૈયાર કરી રહ્યા છીએ...");

            const voice = await getGeneratedVoice();

            const formData = new FormData();
            formData.append("video", video);
            formData.append("voice", voice);

            const music =
                musicInput.files && musicInput.files[0];

            if (music) {
                if (music.size > 30 * 1024 * 1024) {
                    throw new Error(
                        "Music file 30 MB કરતાં નાની હોવી જોઈએ."
                    );
                }

                formData.append("music", music);
            }

            showStatus("🎬 Video editing શરૂ થયું છે. થોડી રાહ જુઓ...");

            const response = await fetch(
                `${API_BASE}/render-short`,
                {
                    method: "POST",
                    body: formData
                }
            );

            if (!response.ok) {
                let message = "Video rendering failed.";

                try {
                    const errorData = await response.json();
                    message = errorData.detail || message;
                } catch (_) {}

                throw new Error(message);
            }

            const blob = await response.blob();

            if (!blob.size) {
                throw new Error("Generated video ખાલી છે.");
            }

            if (outputUrl) {
                URL.revokeObjectURL(outputUrl);
            }

            outputUrl = URL.createObjectURL(blob);

            const heading = document.createElement("h3");
            heading.textContent = "✅ Your Anime Short is Ready!";

            const player = document.createElement("video");
            player.src = outputUrl;
            player.controls = true;
            player.playsInline = true;
            player.style.cssText = `
                width:100%;
                max-width:360px;
                display:block;
                margin:12px auto;
                border-radius:12px;
            `;

            const download = document.createElement("a");
            download.href = outputUrl;
            download.download = "anime-studio-short.mp4";
            download.textContent = "⬇️ Download Your Video";
            download.style.cssText = `
                display:block;
                text-align:center;
                padding:13px;
                margin-top:12px;
                border-radius:10px;
                font-weight:bold;
                text-decoration:none;
                background:#7c3aed;
                color:white;
            `;

            output.append(heading, player, download);

            showStatus("તમારો video તૈયાર છે!");

        } catch (error) {
            console.error("Video Editor Error:", error);
            showStatus(
                error.message || "કંઈક ખોટું થયું. ફરી પ્રયાસ કરો.",
                true
            );
        } finally {
            button.disabled = false;
            button.textContent = "✨ Create My Anime Short";
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            initializeEditor
        );
    } else {
        initializeEditor();
    }

    window.addEventListener("beforeunload", () => {
        if (outputUrl) {
            URL.revokeObjectURL(outputUrl);
        }
    });

})();
          
