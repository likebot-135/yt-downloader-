from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import os
import tempfile

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    video_url = data.get('url')
    
    if not video_url:
        return jsonify({"status": "error", "message": "URL missing hai!"}), 400

    # Temporary directory jahan video temporarily save hogi stream hone se pehle
    temp_dir = tempfile.gettempdir()
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            # Agar format badla ho (jaise mkv se mp4) to sahi filename nikalne ke liye
            filename = os.path.splitext(filename)[0] + '.mp4'

        # Yeh line file ko browser par send karegi jisse Chrome use download file ki tarah treat karega
        response = send_file(filename, as_attachment=True, download_name=os.path.basename(filename))
        
        # Download ke baad temp file delete karne ke liye background me chhod sakte hain
        return response

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':    app.run(host='0.0.0.0', port=5000, debug=True)

