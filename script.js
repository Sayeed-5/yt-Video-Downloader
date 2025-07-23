document.addEventListener('DOMContentLoaded', () => {
    const videoUrlInput = document.getElementById('videoUrl');
    const downloadBtn = document.getElementById('downloadBtn');
    const messageDisplay = document.getElementById('message');

    // Backend Flask server ka URL
    // Make sure this matches where your Flask app is running
    const BACKEND_URL = 'https://yt-video-downloader-6inq.onrender.com'; // Flask default port

    function showMessage(msg, type = 'info') {
        messageDisplay.textContent = msg;
        messageDisplay.className = 'message'; // Reset and add base class
        messageDisplay.classList.add(type); // Add type class (e.g., 'success', 'error', 'info')
        messageDisplay.classList.remove('hidden'); // Make it visible

        // Hide message after 5 seconds
        setTimeout(() => {
            messageDisplay.classList.add('hidden');
        }, 8000);
    }

    downloadBtn.addEventListener('click', async () => {
        const url = videoUrlInput.value.trim();

        if (url === '') {
            showMessage('Kripya YouTube video URL enter karein.', 'error');
            return;
        }

        // Basic YouTube URL validation (you can make this more robust)
        // Checks if it contains youtube.com or youtu.be
        const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+$/;
        if (!youtubeRegex.test(url)) {
            showMessage('Invalid YouTube URL. Kripya sahi URL enter karein.', 'error');
            return;
        }

        showMessage('Downloading shuru ho rahi hai... Kripya wait karein, isme thoda time lag sakta hai.', 'info');
        downloadBtn.disabled = true; // Button ko disable kar dein takay user multiple clicks na kare
        downloadBtn.textContent = 'Downloading...';

        try {
            const response = await fetch(`${BACKEND_URL}/download`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url: url }),
            });

            if (response.ok) {
                // If response is OK, it means the file is being sent
                // Create a blob from the response to download the file
                const blob = await response.blob();
                const contentDisposition = response.headers.get('Content-Disposition');
                let filename = 'youtube_video.mp4'; // Default filename

                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename="([^"]+)"/);
                    if (filenameMatch && filenameMatch[1]) {
                        filename = filenameMatch[1];
                    }
                }

                // Create a temporary URL for the blob
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                a.download = filename; // Set the filename for download
                document.body.appendChild(a);
                a.click(); // Programmatically click the link to trigger download
                a.remove(); // Clean up the element
                window.URL.revokeObjectURL(downloadUrl); // Free up memory

                showMessage('Video successfully download ho gaya!', 'success');
                videoUrlInput.value = ''; // Input field clear kar dein
            } else {
                // Handle errors from the backend
                const errorData = await response.json();
                showMessage(`Download failed: ${errorData.error || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            console.error('Error during fetch:', error);
            showMessage(`Network error ya server response nahi mila: ${error.message}`, 'error');
        } finally {
            downloadBtn.disabled = false; // Button ko phir se enable kar dein
            downloadBtn.textContent = 'Download Video';
        }
    });
});
