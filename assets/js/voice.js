
// Anime Studio AI - AI Hindi Voice Studio

const VoiceStudio = {
    audioUrl: null,

    async generate() {
        const text = document.getElementById("voiceText").value.trim();
        const voice = document.getElementById("voiceName").value;
        const style = document.getElementById("voiceStyle").value;

        const status = document.getElementById("voiceStatus");
        const button = document.getElementById("generateVoiceBtn");
        const result = document.getElementById("voiceResult");
        const audio = document.getElementById("voiceAudio");
        const download = document.getElementById("voiceDownload");

        if (!text) {
            status.textContent = "Please enter your Hindi script first.";
            return;
        }

        button.disabled = true;
        button.textContent = "Generating Voice...";
        status.textContent = "Creating your AI voice...";
        result.hidden = true;

        try {
            const response = await fetch(
                "https://anime-studio-ai.onrender.com/generate-voice",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        text: text,
                        voice: voice,
                        style: style
                    })
                }
            );

            if (!response.ok) {
                let message = "Voice generation failed.";

                try {
                    const error = await response.json();
                    message = error.detail || message;
                } catch (e) {}

                throw new Error(message);
            }

            const audioBlob = await response.blob();

            if (!audioBlob.size) {
                throw new Error("Audio file is empty.");
            }

            if (this.audioUrl) {
                URL.revokeObjectURL(this.audioUrl);
            }

            this.audioUrl = URL.createObjectURL(audioBlob);

            audio.src = this.audioUrl;
            download.href = this.audioUrl;

            result.hidden = false;
            status.textContent = "AI Voice generated successfully!";

        } catch (error) {
            console.error("Voice Error:", error);
            status.textContent = "Error: " + error.message;

        } finally {
            button.disabled = false;
            button.textContent = "🎙️ Generate AI Voice";
        }
    }
};

// Connect button after the HTML is available
function connectVoiceButton() {
    const button = document.getElementById("generateVoiceBtn");

    if (button && !button.dataset.voiceConnected) {
        button.dataset.voiceConnected = "true";

        button.addEventListener("click", function () {
            VoiceStudio.generate();
        });
    }
}

connectVoiceButton();

document.addEventListener("DOMContentLoaded", connectVoiceButton);

window.VoiceStudio = VoiceStudio;
