
// Anime Studio AI - Script Generator

let currentScript = "";
let videoPreviewURL = null;

// Open creator section
function openCreator(type) {
    document.getElementById("type").value = type;
    scrollToCreator();
}

function scrollToCreator() {
    document.getElementById("creator").scrollIntoView({
        behavior: "smooth"
    });
}

function scrollToUpload() {
    document.getElementById("upload").scrollIntoView({
        behavior: "smooth"
    });
}

// Generate AI Script
async function createProject() {
    const anime = document.getElementById("anime").value.trim();
    const episode = document.getElementById("episode").value.trim();
    const type = document.getElementById("type").value;
    const language = document.getElementById("language").value;
    const duration = document.getElementById("duration").value;
    const instructions = document.getElementById("instructions").value;

    const status = document.getElementById("status");
    const result = document.getElementById("result");
    const scriptBox = document.getElementById("scriptBox");
    const generateBtn = document.getElementById("generateBtn");

    if (!anime) {
        alert("Please enter Anime Name!");
        return;
    }

    generateBtn.disabled = true;
    generateBtn.innerText = "Generating...";
    status.innerText = "⏳ Connecting to Anime Studio AI...";
    scriptBox.style.display = "none";

    try {
        const apiURL = window.AnimeStudio.API_BASE_URL;

        const response = await fetch(apiURL + "/generate-script", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                anime: anime,
                episode: episode || "Not specified",
                video_type: type,
                language: language,
                duration: duration,
                instructions: instructions
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "AI generation failed");
        }

        if (!data.script) {
            throw new Error("AI returned an empty script.");
        }

        currentScript = data.script;
        result.textContent = currentScript;
        scriptBox.style.display = "block";
        status.innerText = "✅ Your AI Script is ready!";

        const projects = document.getElementById("projects");

        if (projects.innerText === "No projects created yet.") {
            projects.innerText = "";
        }

        const project = document.createElement("p");
        project.textContent = "📄 " + anime + " - " + type;
        projects.prepend(project);

        scriptBox.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });

    } catch (error) {
        status.innerText =
            "❌ " + error.message +
            "\nPlease try again. Check your Backend if needed.";

    } finally {
        generateBtn.disabled = false;
        generateBtn.innerText = "✨ Generate AI Script";
    }
}

// Copy Script
async function copyScript() {
    if (!currentScript) return;

    try {
        await navigator.clipboard.writeText(currentScript);
        alert("Script copied successfully!");
    } catch (error) {
        alert("Copy failed. Please copy the script manually.");
    }
}

// Download Script
function downloadScript() {
    if (!currentScript) return;

    const blob = new Blob(
        [currentScript],
        { type: "text/plain;charset=utf-8" }
    );

    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");

    a.href = url;
    a.download = "anime-script.txt";
    a.click();

    URL.revokeObjectURL(url);
}

// Video File Preview
document.addEventListener("DOMContentLoaded", function () {
    const videoFile = document.getElementById("videoFile");

    if (!videoFile) return;

    videoFile.addEventListener("change", function () {
        const file = this.files[0];

        const info = document.getElementById("fileInfo");
        const preview = document.getElementById("videoPreview");

        if (!file) {
            info.innerText = "";
            preview.style.display = "none";
            return;
        }

        if (videoPreviewURL) {
            URL.revokeObjectURL(videoPreviewURL);
        }

        info.innerText =
            "Selected: " + file.name +
            " | Size: " +
            (file.size / 1024 / 1024).toFixed(2) + " MB";

        videoPreviewURL = URL.createObjectURL(file);

        preview.src = videoPreviewURL;
        preview.style.display = "block";
    });
});
