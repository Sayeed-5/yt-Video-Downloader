from flask import Flask, request, send_file, jsonify
from flask_cors import CORS # For handling Cross-Origin Resource Sharing
import yt_dlp
import os
import shutil # For removing directories

app = Flask(__name__)
# Enable CORS for all routes, allowing your frontend (running on a different port) to access this backend
CORS(app) 

# Directory to save downloaded videos temporarily
DOWNLOAD_DIR = "downloads"

# Ensure the download directory exists
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@app.route('/')
def home():
    return "YouTube Video Downloader Backend is Live! Use the frontend to download videos."

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    video_url = data.get('url')

    if not video_url:
        return jsonify({"error": "Video URL nahi mila. Kripya URL provide karein."}), 400

    # Clean up old downloads before starting a new one
    # This ensures we don't accumulate too many files and avoid conflicts
    for filename in os.listdir(DOWNLOAD_DIR):
        file_path = os.path.join(DOWNLOAD_DIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Error deleting {file_path}: {e}')
            # Optionally, you might want to return an error to the user if cleanup fails criticaly

    # yt-dlp options
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # Prioritize mp4
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'), # Save in downloads folder with title
        'noplaylist': True, # Only download single video, not entire playlist
        'geo_bypass': True, # Bypass geo-restrictions
        # 'quiet': True, # Suppress console output from yt-dlp (uncomment for production)
        # 'no_warnings': True, # Suppress warnings (uncomment for production)
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            # Find the path of the downloaded file
            # This can be tricky as yt-dlp can download in different formats/names
            # A common way is to reconstruct the filename from info_dict
            
            # Use post-processing if necessary (e.g., if format creates multiple files)
            # For simplicity, we assume 'mp4' or the best available is chosen and is a single file.
            
            # Best approach is to get the actual filepath from info_dict if available, 
            # or try to guess based on 'outtmpl' and extracted info.
            
            # yt-dlp often returns the actual downloaded file path in 'requested_downloads'
            downloaded_filepath = None
            if 'requested_downloads' in info_dict and len(info_dict['requested_downloads']) > 0:
                downloaded_filepath = info_dict['requested_downloads'][0]['filepath']
            else:
                # Fallback: construct path based on outtmpl and info_dict
                # This might not always be accurate if yt-dlp changes filename
                title = info_dict.get('title', 'video')
                ext = info_dict.get('ext', 'mp4') # Default to mp4 if not found
                # Sanitize title for filename
                sanitized_title = "".join([c for c in title if c.isalnum() or c in (' ', '.', '_', '-')]).rstrip()
                downloaded_filename = f"{sanitized_title}.{ext}"
                downloaded_filepath = os.path.join(DOWNLOAD_DIR, downloaded_filename)
                
                # Check if the file actually exists by searching the download directory
                # This is a more robust way to find the file after download
                found_files = [f for f in os.listdir(DOWNLOAD_DIR) if f.startswith(sanitized_title)]
                if found_files:
                    # Sort to get the most relevant/last downloaded file if multiple exist
                    # A more robust solution might involve parsing all files downloaded by yt-dlp
                    downloaded_filepath = os.path.join(DOWNLOAD_DIR, found_files[0])


            if not downloaded_filepath or not os.path.exists(downloaded_filepath):
                return jsonify({"error": "Video download ho gaya par file nahi mili."}), 500
            
            # Send the file to the client
            # as_attachment=True will force the browser to download the file
            # mimetype will set the Content-Type header
            print(f"Sending file: {downloaded_filepath}")
            return send_file(downloaded_filepath, as_attachment=True, mimetype='video/mp4')

    except yt_dlp.DownloadError as e:
        # Handle errors specific to yt-dlp
        return jsonify({"error": f"Video download mein problem aayi: {str(e)}"}), 500
    except Exception as e:
        # Handle any other general errors
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    # Run the Flask app on port 5000
    # debug=True is good for development, but set to False for production
    app.run(debug=True, port=5000)
