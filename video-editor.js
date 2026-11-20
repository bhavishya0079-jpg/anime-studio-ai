// Anime Studio AI - Video Editor Module

const VideoEditor = {
    selectedVideo: null,

    selectVideo(file) {
        if (!file) {
            throw new Error("Please select a video.");
        }

        this.selectedVideo = file;

        return {
            status: "selected",
            name: file.name,
            size: file.size
        };
    },

    showMessage(elementId, message) {
        const element = document.getElementById(elementId);
        if (element) element.textContent = message;
    }
};

window.VideoEditor = VideoEditor;
