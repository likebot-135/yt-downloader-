from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os

app = Flask(__name__)

# Render ke cloud server par temporary file save karne ki sahi directory
DOWNLOAD_DIR = "/tmp"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    video_url = data.get('url')
    
    if not video_url:
        return jsonify({"status": "error", "message": "URL missing hai!"}), 400

    # Sabhi tarah ke links (Long, Shorts, Mobile) ko extract karne ke liye modern config
    ydl_opts = {
        'format': 'best[ext=mp4]/best', # Multi-format compatibility ke liye single stream stream/download
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
        'noplaylist': True,
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)

        # File ko safely Chrome browser me stream karna
        response = send_file(filename, as_attachment=True, download_name=f"{info.get('title', 'video')}.mp4")
        
        return response

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error: {str(e)}"}), 500

if __name__ == '__main__':
    # Cloud hostings automatic port asign karti hain, isliye env port read karna zaroori hai
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

