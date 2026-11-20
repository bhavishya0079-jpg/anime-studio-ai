
// Anime Studio AI - Main Application

const API_BASE_URL = "https://anime-studio-ai.onrender.com";

document.addEventListener("DOMContentLoaded", () => {
    console.log("Anime Studio AI is ready!");

    const year = document.getElementById("currentYear");
    if (year) {
        year.textContent = new Date().getFullYear();
    }
});

// Backend connection check
async function checkBackend() {
    try {
        const response = await fetch(API_BASE_URL);
        if (!response.ok) throw new Error("Backend unavailable");

        const data = await response.json();
        console.log("Backend status:", data);
        return true;
    } catch (error) {
        console.error("Backend connection failed:", error);
        return false;
    }
}

// Common message display
function showMessage(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = message;
    }
}

// Safe text display
function displayText(elementId, text) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = text;
    }
}

window.AnimeStudio = {
    API_BASE_URL,
    checkBackend,
    showMessage,
    displayText
};
